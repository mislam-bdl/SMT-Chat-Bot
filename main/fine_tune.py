# fine_tune.py
import json, re, sys, types
from pathlib import Path
import docx, PyPDF2
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import torch

# === CRITICAL PATCH: Disable inductor.config access ===
print("Applying inductor patch for PyTorch 2.4+...")
import unsloth_zoo.temporary_patches.common as patch_mod
if hasattr(patch_mod, 'inductor_config_source'):
    patch_mod.inductor_config_source = "# Patched out: torch._inductor.config removed in PyTorch 2.4+"
else:
    # Fallback: monkey-patch the module
    import importlib
    spec = importlib.util.spec_from_loader("torch._inductor.config", loader=None)
    config_mod = importlib.util.module_from_spec(spec)
    sys.modules["torch._inductor.config"] = config_mod

# === Now safe to import unsloth ===
# === AUTO-PATCH: Force Unsloth to recognize RTX 5060 Ti ===
import torch
import unsloth_zoo.device_type as dt

_original_get_device_type = dt.get_device_type

def patched_get_device_type():
    if torch.cuda.is_available():
        cap = torch.cuda.get_device_capability()
        if cap >= (12, 0):
            print(f"Detected RTX 50-series (sm_{cap[0]}{cap[1]}). Forcing CUDA mode.")
            return "cuda"
        return "cuda"
    raise NotImplementedError("Unsloth currently only works on NVIDIA, AMD and Intel GPUs.")

dt.get_device_type = patched_get_device_type


from unsloth import FastLanguageModel

# ================= CONFIG =================
BASE_MODEL = "unsloth/llama-3-8b-bnb-4bit"
OUT_DIR = Path("llama3_rag_tuned")
DATA_FILE = Path("finetune_dataset2json")
MAX_SEQ_LENGTH = 2048
# ==========================================

def build_dataset():
    rag_files = [f for f in Path(".").glob("*_rag.*") if f.suffix.lower() in [".txt", ".docx", ".pdf"]]
    samples = []
    for f in rag_files:
        print(f"Reading {f.name}...")
        try:
            if f.suffix == ".txt":
                text = f.read_text(encoding="utf-8", errors="ignore")
            elif f.suffix == ".docx":
                text = "\n".join(p.text for p in docx.Document(f).paragraphs)
            elif f.suffix == ".pdf":
                with open(f, "rb") as pdf:
                    reader = PyPDF2.PdfReader(pdf)
                    text = "\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            continue

        chunks = re.split(r'(?<=[.!?])\s+', text)
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if len(chunk) > 40:
                samples.append({
                    "instruction": f"Explain this from {f.stem} (part {i}):",
                    "input": "",
                    "output": chunk
                })

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print(f"Dataset built: {len(samples)} samples")
    return len(samples)

def format_prompt(ex):
    return f"### Instruction:\n{ex['instruction']}\n\n### Response:\n{ex['output']}"

def fine_tune():
    if OUT_DIR.exists():
        print(f"Model already exists at {OUT_DIR}. Skipping training.")
        return

    if not DATA_FILE.exists():
        build_dataset()

    dataset = load_dataset("json", data_files=str(DATA_FILE), split="train")

    print("Loading 4-bit model...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,
        load_in_4bit=True,
    )

    print("Applying LoRA...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=8,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    print("Starting training...")
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        formatting_func=format_prompt,
        max_seq_length=MAX_SEQ_LENGTH,
        args=TrainingArguments(
            per_device_train_batch_size=2,
            gradient_accumulation_steps=4,
            warmup_steps=5,
            max_steps=100,
            learning_rate=2e-4,
            fp16=not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_bf16_supported(),
            logging_steps=10,
            output_dir="outputs",
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            seed=3407,
            report_to="none",
        ),
    )

    trainer.train()

    print("Saving model...")
    model.save_pretrained(OUT_DIR)
    tokenizer.save_pretrained(OUT_DIR)
    print(f"SUCCESS: Model saved to {OUT_DIR}")

if __name__ == "__main__":
    fine_tune()
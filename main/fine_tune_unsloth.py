import json
import re
from pathlib import Path
from docx import Document
import PyPDF2

DOCS_FOLDER = Path(__file__).parent
output_file = DOCS_FOLDER / "dataset.jsonl"

def load_rag_docs():
    txt = ""
    files = [f for f in DOCS_FOLDER.iterdir() if "_rag" in f.name.lower() and f.suffix.lower() in {".txt", ".docx", ".pdf"}]
    for f in files:
        try:
            if f.suffix.lower() == ".txt":
                content = f.read_text(encoding="utf-8", errors="ignore")
            elif f.suffix.lower() == ".docx":
                doc = Document(f)
                content = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            elif f.suffix.lower() == ".pdf":
                with open(f, "rb") as pdf:
                    r = PyPDF2.PdfReader(pdf)
                    content = "\n".join(page.extract_text() or "" for page in r.pages if page.extract_text())
            txt += content + "\n\n"
            print(f"Loaded {f.name}")
        except Exception as e:
            print(f"Error {f.name}: {e}")
    return txt.strip()

def make_qa_dataset(text):
    # Simple Q&A extraction (customize for your files)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    data = []
    i = 0
    while i < len(sentences) - 1:
        q = sentences[i]
        a = sentences[i + 1]
        if q.endswith("?") and len(a) > 10:
            data.append({"instruction": q, "output": a})
        i += 1
    return data

# Run
raw_text = load_rag_docs()
qa_pairs = make_qa_dataset(raw_text)
with open(output_file, "w") as f:
    for pair in qa_pairs:
        f.write(json.dumps(pair) + "\n")
print(f"Created dataset.jsonl with {len(qa_pairs)} pairs")


from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import torch

# Load model
model, tokenizer = FastLanguageModel.from_pretrained(
    "unsloth/llama-3.2-3b-bnb-4bit",
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

model = FastLanguageModel.get_peft_model(
    model, r=16, target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_alpha=16, lora_dropout=0, bias="none", use_gradient_checkpointing="unsloth",
    random_state=3407, use_rslora=False, loftq_config=None,
)

# Load dataset
dataset = load_dataset("json", data_files="dataset.jsonl", split="train")

def formatting_prompts_func(examples):
    instructions = examples["instruction"]
    outputs = examples["output"]
    texts = []
    for instruction, output in zip(instructions, outputs):
        text = f"### Instruction:\n{instruction}\n\n### Response:\n{output}" + tokenizer.eos_token
        texts.append(text)
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)

# Train
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=2048,
    dataset_num_proc=2,
    packing=False,
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=5,
        max_steps=60,  # Adjust for data size
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        output_dir="outputs",
    ),
)

trainer.train()
model.save_pretrained("lora_model")

# Export to GGUF for Ollama
model.save_pretrained_gguf("lora_model", tokenizer, quantization_method="q4_k_m")
print("GGUF exported to lora_model/gguf!")
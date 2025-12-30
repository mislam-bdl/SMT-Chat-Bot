# --------------------------------------------------------------
# 1. DELETE OLD 'verba' ENV
# --------------------------------------------------------------
Write-Host "Deleting old 'verba' environment..." -ForegroundColor Red
conda env remove -n verba -y

# --------------------------------------------------------------
# 2. CREATE NEW 'AIChat' ENV (Python 3.11)
# --------------------------------------------------------------
Write-Host "Creating new 'AIChat' environment..." -ForegroundColor Green
conda create -n AIChat python=3.11 -y
conda activate AIChat

# --------------------------------------------------------------
# 3. INSTALL CORE DEPENDENCIES
# --------------------------------------------------------------
Write-Host "Installing core packages..." -ForegroundColor Yellow
pip install --upgrade pip

pip install \
    torch==2.3.0+cu121 \
    torchvision==0.18.0+cu121 \
    torchaudio==2.3.0+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

pip install \
    flask \
    ollama \
    numpy \
    scikit-learn \
    docx \
    PyPDF2 \
    transformers \
    datasets \
    trl \
    peft \
    accelerate \
    bitsandbytes \
    sentencepiece \
    tqdm

# --------------------------------------------------------------
# 4. INSTALL UNSLOTH + llama-cpp-python[cuda] (WITH DLL)
# --------------------------------------------------------------
Write-Host "Installing Unsloth + llama-cpp-python[cuda]..." -ForegroundColor Cyan
$env:CMAKE_ARGS = "-DLLAMA_CUDA=on -DLLAMA_BUILD=off"
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install "llama-cpp-python[cuda]" --no-cache-dir --force-reinstall

# --------------------------------------------------------------
# 5. VERIFY llama.dll EXISTS
# --------------------------------------------------------------
python -c "import site, pathlib; p = pathlib.Path(site.getsitepackages()[0]) / 'llama_cpp' / 'lib' / 'llama.dll'; print('llama.dll found:' if p.exists() else 'MISSING:', p)"

# --------------------------------------------------------------
# 6. TEST llama_cpp import
# --------------------------------------------------------------
python -c "from llama_cpp import Llama; print('llama-cpp-python OK')"

# --------------------------------------------------------------
# 7. FINAL CHECK
# --------------------------------------------------------------
Write-Host "`nENVIRONMENT READY: AIChat" -ForegroundColor Green
Write-Host "Python:" (python --version)
Write-Host "CUDA available:" (python -c "import torch; print(torch.cuda.is_available())")
Write-Host "`nRun your app now:" -ForegroundColor Magenta
Write-Host "python app.py`n"
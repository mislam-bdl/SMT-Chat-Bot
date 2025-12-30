# ==============================================================
# SETUP: AIChat Environment for LabGPT (Windows + CUDA + Ollama)
# ==============================================================
# 1. REMOVE OLD ENV
Write-Host "`n[1/8] Removing old AIChat environment..." -ForegroundColor Red
conda env remove -n AIChat -y

# 2. CREATE NEW ENV WITH PYTHON 3.11
Write-Host "`n[2/8] Creating AIChat with Python 3.11..." -ForegroundColor Green
conda create -n AIChat python=3.11 -y
conda activate AIChat

# 3. UPGRADE PIP
Write-Host "`n[3/8] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 4. INSTALL PYTORCH + CUDA (ONLY TORCH)
Write-Host "`n[4/8] Installing torch==2.3.0+cu121..." -ForegroundColor Cyan
pip install torch==2.3.0+cu121 --index-url https://download.pytorch.org/whl/cu121 --no-deps

# 5. INSTALL CORE DEPENDENCIES
Write-Host "`n[5/8] Installing core packages..." -ForegroundColor Magenta
pip install flask ollama numpy scikit-learn python-docx PyPDF2 transformers datasets trl peft accelerate bitsandbytes sentencepiece tqdm

# 6. INSTALL UNSLOTH (FIXED - Use direct file download without URL encoding)
Write-Host "`n[6/8] Downloading & installing Unsloth with curl..." -ForegroundColor Cyan
$wheelUrl = "https://github.com/unslothai/unsloth/releases/download/v2024.10.1/unsloth-2024.10.1+cu121-torch2.3.0-cp311-cp311-win_amd64.whl"
$wheelFile = "unsloth-2024.10.1_cu121.whl"

# Download the wheel with proper error handling
curl.exe -L -o $wheelFile $wheelUrl -ErrorAction Stop
if (-not (Test-Path $wheelFile)) {
    Write-Host "Failed to download Unsloth wheel. Trying alternative method..." -ForegroundColor Yellow
    # Fallback: Install from PyPI (might be slower or outdated)
    pip install 'unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git'
} else {
    # Install from local wheel with explicit path
    Write-Host "Installing wheel from local file..." -ForegroundColor Cyan
    pip install (Resolve-Path $wheelFile).Path --no-deps
    Remove-Item $wheelFile -Force
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Wheel install failed. Trying GitHub source..." -ForegroundColor Yellow
        pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
    }
}

# 7. INSTALL llama-cpp-python[cuda] WITH DLL
Write-Host "`n[7/8] Installing llama-cpp-python[cuda]..." -ForegroundColor Cyan
$env:CMAKE_ARGS = "-DLLAMA_CUDA=on -DLLAMA_BUILD=off"
pip install "llama-cpp-python[cuda]" --no-cache-dir --force-reinstall

# 8. FINAL: PIN TORCH + REMOVE UNNEEDED
Write-Host "`n[8/8] Finalizing: pin torch, remove extras..." -ForegroundColor Yellow
pip uninstall torchaudio torchvision -y
pip install torch==2.3.0+cu121 --index-url https://download.pytorch.org/whl/cu121 --force-reinstall --no-deps

# ==============================================================
# VERIFICATION
# ==============================================================
Write-Host "`nVERIFICATION:" -ForegroundColor Green
python -c "import torch; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
python -c "from unsloth import FastLanguageModel; print('Unsloth: OK')"
python -c "from llama_cpp import Llama; print('llama-cpp-python: OK')"

Write-Host "`nAIChat ENVIRONMENT IS READY!" -ForegroundColor Green
Write-Host "Run your app with: python app.py`n" -ForegroundColor Magenta
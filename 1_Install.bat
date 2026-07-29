@echo off
title Traffic AI Setup
cd /d "%~dp0"

echo Checking for AI Model...
if not exist "Model" mkdir Model
if exist "Model\Model.gguf" (
    echo Model exists, skipping download.
) else (
    echo Downloading model...
    curl -L -o "Model\Model.gguf" "https://huggingface.co/RichardErkhov/scb10x_-_llama-3-typhoon-v1.5x-8b-instruct-gguf/resolve/main/llama-3-typhoon-v1.5x-8b-instruct.IQ3_M.gguf"
)

echo Creating virtual environment...
python -m venv .venv
call .venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing GPU-accelerated backend from GitHub Release...
pip install "https://github.com/ignitears/ThaiTrafficAI/releases/download/v1.0/llama_cpp_python-0.3.33-py3-none-win_amd64.whl"

echo Installing remaining dependencies...
pip install -r requirements.txt

echo Setup Complete!
pause
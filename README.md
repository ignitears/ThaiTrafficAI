# Traffic Law AI

A lightweight, local AI assistant designed to answer questions regarding Thai traffic laws. This project runs locally on your machine using a streamlined web interface and a Retrieval-Augmented Generation (RAG) backend.

## One-Click Installation

To keep your system clean, this project uses an isolated Python environment and a simple installation script.

1. **Install Python:** Ensure you have Python installed on your Windows machine. **Important:** Check the box that says *"Add python.exe to PATH"* during installation.
2. **Run Setup:** Double-click **`1_Install.bat`**. This script will automatically create a virtual environment, handle package requirements, and fetch the required 3.78 GB Typhoon AI model directly from Hugging Face into the local directory

## How to Use

Once installed, you never have to touch the terminal again.

* Double-click **`2_Start_AI.vbs`** to launch the server silently. 
* A control panel will appear, and once the model finishes loading into memory, your web browser will open automatically to the chat interface.
* You can safely shut down the server anytime by clicking the **"Stop Server & Exit"** button on the control panel.

## Data Handling & Processing

1. Extract data from a PDF file
2. Clean the mess from PDF extraction
3. The RAG database for this project is prepared and structured using Google Colab. It uses the Gemini AI to clean and group Thai traffic law text into a well-organized JSON format so the data is easier to read for the llm.

If you want to view the processing steps or update the raw dataset, you can access the processing notebook by downloading organize_data.ipynb from the data folder and open it in google colab.

## System Requirements

| Component | Minimum Requirements | Recommended Specifications |
| :--- | :--- | :--- |
| **OS** | Windows 10/11 (64-bit) | Windows 10/11 (64-bit) |
| **Processor** | Intel Core i5 / AMD Ryzen 5 | Intel Core i7 / AMD Ryzen 7 |
| **Memory (RAM)** | 8 GB RAM | 16 GB RAM |
| **Graphics (VRAM)** | Integrated Graphics (CPU Mode) | Dedicated GPU with 6+ GB VRAM (e.g., RTX 4050) |
| **Storage** | 6 GB available space (SSD) | 10 GB available space (NVMe SSD) |

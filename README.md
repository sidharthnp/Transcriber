---

# 🎙️ Whisper Transcriber

This project provides a simple **GUI-based speech-to-text transcriber** using **Whisper**.
You can record audio snippets, transcribe them, and copy the text easily.

By default, it uses the **Whisper Tiny** model (fast and lightweight).
You can switch to the **Base** (or larger) models by editing `transcriber.py`.

---

## 📦 Prerequisites

### 1. Python

* Version: **Python 3.8 or higher**
* Check your version:

```bash
python --version
```

### 2. Required Python Packages

Install the dependencies one by one:

```bash
pip install sounddevice
pip install numpy
pip install openai-whisper
pip install torch
pip install pyperclip
```

👉 For Linux users, you may also need **tkinter** (not installed via `pip`):

```bash
sudo apt-get install python3-tk
```

---

## 📚 Library Details

* **tkinter** → GUI framework (comes pre-installed with Python, or install via system package manager if missing)
* **sounddevice** → Recording audio from your microphone
* **numpy** → Handling audio data arrays
* **whisper** → OpenAI Whisper model for transcription
* **torch** → PyTorch backend required for Whisper (uses GPU if available)
* **pyperclip** → Copying text to clipboard

---

## ⚡ GPU Support (Optional but Recommended)

If you have an NVIDIA GPU, install the **CUDA-supported version of PyTorch** for faster transcription.

1. Visit the [PyTorch Installation Guide](https://pytorch.org/get-started/locally/).
2. Select your system settings and run the recommended install command.

Example (for **CUDA 11.8**):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

---

## 🚀 Running the Program

Once dependencies are installed, run:

```bash
python transcriber.py
```

---

## 🛠️ Customization

* Default model = `"tiny"`
* You can switch models by editing the following line in `transcriber.py`:

```python
model = whisper.load_model("tiny")
```

Change `"tiny"` to `"base"`, `"small"`, `"medium"`, or `"large"` depending on your needs.

---

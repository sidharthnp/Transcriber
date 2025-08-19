#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Whisper Transcriber with SwishFormer Support
"""
import sys
import os

# SwishFormer compatibility setup
try:
    # Check if running under SwishFormer
    if 'swishformer' in sys.executable.lower() or 'SwishFormer' in str(sys.path):
        print("Running with SwishFormer interpreter")
        # Add any SwishFormer-specific configurations here if needed
        # os.environ['SWISHFORMER_MODE'] = '1'
except Exception as e:
    print(f"SwishFormer detection note: {e}")

# Ensure proper working directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Your existing imports start here...
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import threading
import sounddevice as sd
import numpy as np
import wave
import whisper
import pyperclip
import gc
import os
import torch

# =============================
# Global Variables
# =============================
is_recording = False
filename = "recorded_audio.wav"
samplerate = 16000
channels = 1
current_model = None
model_lock = threading.Lock()
transcribed_sentences = []

# =============================
# Model Loading
# =============================
def load_model_safely():
    global current_model
    with model_lock:
        model_size = model_var.get()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        try:
            if current_model is not None:
                del current_model
                gc.collect()
            add_status_message(f"📥 Loading {model_size} model ({device.upper()})...")
            current_model = whisper.load_model(model_size, device=device)
            add_status_message("✅ Model loaded!")
            return current_model
        except Exception as e:
            add_status_message(f"❌ Model loading failed: {str(e)}")
            return None

def add_status_message(message):
    text_area.insert(tk.END, f"{message}\n")
    text_area.see(tk.END)
    root.update()

def add_transcription(text, timestamp=None):
    if timestamp:
        display_text = f"[{timestamp}] {text}"
    else:
        display_text = text
    transcribed_sentences.append(text.strip())
    text_area.insert(tk.END, f"{display_text}\n")
    text_area.see(tk.END)
    root.update_idletasks()

# =============================
# Audio Recording
# =============================
def record_audio():
    global is_recording
    audio_data = []
    try:
        def callback(indata, frames, time_info, status):
            if is_recording:
                audio_data.append(indata.copy())
            else:
                raise sd.CallbackStop
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback, dtype=np.int16):
            while is_recording:
                sd.sleep(100)
        if audio_data:
            audio_data = np.concatenate(audio_data, axis=0)
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(2)
                wf.setframerate(samplerate)
                wf.writeframes(audio_data.tobytes())
    except Exception as e:
        root.after(0, lambda: add_status_message(f"❌ Recording error: {e}"))

# =============================
# Transcription
# =============================
def transcribe_audio(model_size):
    try:
        add_status_message("\n⏳ Transcribing...")
        model = load_model_safely()
        if model is None:
            return ""
        if not os.path.exists(filename):
            add_status_message("❌ No recording file found")
            return ""
        result = model.transcribe(
            filename, fp16=(model.device == "cuda"),
            language="en", task="transcribe",
            beam_size=3, best_of=3, temperature=0.0
        )
        transcribed_text = result["text"].strip()
        add_transcription(transcribed_text)
        return transcribed_text
    except Exception as e:
        add_status_message(f"❌ Transcription failed: {str(e)}")
        return ""

# =============================
# Button Handlers
# =============================
def start_recording():
    global is_recording, transcribed_sentences
    is_recording = True
    transcribed_sentences = []
    text_area.delete(1.0, tk.END)
    add_status_message("🎤 Recording...")
    start_btn.config(text="🔴 Recording...", bg="darkred", state="disabled")
    stop_btn.config(state="normal")
    threading.Thread(target=record_audio, daemon=True).start()

def stop_recording():
    global is_recording
    if is_recording:
        is_recording = False
        add_status_message("\n🛑 Recording stopped.")
        start_btn.config(text="▶ Start Recording", bg="green", state="normal")
        stop_btn.config(state="disabled")
        # Capture the model size in main thread to avoid tkinter variable in thread
        model_size = model_var.get()
        threading.Thread(target=transcribe_audio, args=(model_size,), daemon=True).start()

def copy_text():
    if transcribed_sentences:
        clean_text = " ".join(transcribed_sentences)
        pyperclip.copy(clean_text)
        messagebox.showinfo("Copied", f"✅ Transcribed text copied!\n({len(clean_text)} characters)")
    else:
        messagebox.showwarning("Empty", "⚠ No transcribed text to copy.")

def clear_text():
    global transcribed_sentences
    transcribed_sentences = []
    text_area.delete(1.0, tk.END)

def save_text():
    if transcribed_sentences:
        try:
            clean_text = " ".join(transcribed_sentences)
            with open("transcription.txt", "w", encoding="utf-8") as f:
                f.write(clean_text)
            messagebox.showinfo("Saved", f"✅ Saved {len(clean_text)} characters to transcription.txt")
        except Exception as e:
            messagebox.showerror("Error", f"❌ Save failed: {e}")
    else:
        messagebox.showwarning("Empty", "⚠ No transcribed text to save.")

# =============================
# GUI
# =============================
root = tk.Tk()
root.title("🎙 Whisper Simple Transcriber")
root.geometry("800x600")

model_frame = tk.LabelFrame(root, text="Model Settings", font=("Arial", 10, "bold"))
model_frame.pack(pady=5, padx=10, fill="x")

tk.Label(model_frame, text="Model:").grid(row=0, column=0, padx=5, sticky="w")
model_var = tk.StringVar(value="tiny")
model_combo = ttk.Combobox(model_frame, textvariable=model_var, values=["tiny", "base"], width=15)
model_combo.grid(row=0, column=1, padx=5)

status_label = tk.Label(model_frame, text="Device: GPU if available, else CPU | Default: Whisper Tiny", fg="blue")
status_label.grid(row=1, column=0, columnspan=6, pady=5, sticky="w")

btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="▶ Start Recording", command=start_recording, 
                     bg="green", fg="white", width=15, height=2, font=("Arial", 9, "bold"))
start_btn.grid(row=0, column=0, padx=5)
stop_btn = tk.Button(btn_frame, text="⏹ Stop Recording", command=stop_recording, 
                    bg="red", fg="white", width=15, height=2, font=("Arial", 9, "bold"), state="disabled")
stop_btn.grid(row=0, column=1, padx=5)

copy_btn = tk.Button(btn_frame, text="📋 Copy Transcript", command=copy_text, 
                    bg="blue", fg="white", width=15, font=("Arial", 9, "bold"))
copy_btn.grid(row=1, column=0, padx=5, pady=5)
save_btn = tk.Button(btn_frame, text="💾 Save Transcript", command=save_text, 
                    bg="darkgreen", fg="white", width=15, font=("Arial", 9, "bold"))
save_btn.grid(row=1, column=1, padx=5, pady=5)
clear_btn = tk.Button(btn_frame, text="🗑️ Clear All", command=clear_text, 
                     bg="orange", fg="white", width=15, font=("Arial", 9, "bold"))
clear_btn.grid(row=1, column=2, padx=5, pady=5)

text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=85, height=22, font=("Consolas", 11))
text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

help_text = """
🎙️ SIMPLE WHISPER TRANSCRIBER

• Model: Whisper Tiny (default, fastest) or Base (better accuracy). Uses GPU if present.
• Usage: Start Recording → Speak → Stop Recording → Transcript appears (copy/save/clear available).
"""

text_area.insert(tk.END, help_text)

def on_closing():
    global is_recording
    is_recording = False
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()

#!/usr/bin/env python3
import sys
import os

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

print("Starting simple test...", flush=True)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Importing customtkinter...", flush=True)
import customtkinter as ctk

print("Creating root window...", flush=True)
root = ctk.CTk()
root.title("Simple Test")
root.geometry("400x300")

print("Adding label...", flush=True)
label = ctk.CTkLabel(root, text="Window is visible!", font=("Arial", 20))
label.pack(pady=50)

print("Adding button...", flush=True)
def on_close():
    print("Button clicked, closing...", flush=True)
    root.destroy()

button = ctk.CTkButton(root, text="Close", command=on_close)
button.pack(pady=20)

print("Starting mainloop...", flush=True)
root.mainloop()

print("Mainloop ended", flush=True)

import tkinter as tk
from tkinter import ttk
import subprocess
import threading
import time
import urllib.request
import webbrowser
import sys
import os

class AILauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic AI - Control Panel")
        self.root.geometry("400x150")
        self.root.eval('tk::PlaceWindow . center')
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)
        self.root.resizable(False, False)
        
        self.label = tk.Label(root, text="Loading AI Model...\n(This may take a while you can go get some coffee)", font=("Segoe UI", 10))
        self.label.pack(pady=(20, 10))
        
        # Changed to determinate for one-way animation
        self.progress = ttk.Progressbar(root, mode='determinate', length=300, maximum=100)
        self.progress.pack(pady=5)
        
        self.btn = ttk.Button(root, text="Cancel", command=self.close_app)
        self.btn.pack(pady=10)
        
        self.server = None
        self.is_ready = False
        
        # Start our custom one-way animation
        self.animate_progress()
        threading.Thread(target=self.start_server, daemon=True).start()

    def animate_progress(self):
        if not self.is_ready:
            self.progress['value'] += 2
            if self.progress['value'] >= 100:
                self.progress['value'] = 0
            # Loop the animation every 30 milliseconds
            self.root.after(30, self.animate_progress)

    def start_server(self):
        python_exe = os.path.join(".venv", "Scripts", "python.exe")
        if not os.path.exists(python_exe): 
            python_exe = "python"
            
        self.server = subprocess.Popen(
            [python_exe, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"],
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        ready = False
        while not ready and self.server.poll() is None:
            try:
                urllib.request.urlopen("http://127.0.0.1:8000/api/characters", timeout=1)
                ready = True
            except:
                time.sleep(1)
        
        if ready:
            self.root.after(0, self.set_ready)

    def set_ready(self):
        self.is_ready = True
        self.label.config(text="AI is running. Browser opened.")
        self.progress.config(value=100)
        self.btn.config(text="Stop Server & Exit")
        webbrowser.open("http://127.0.0.1:8000")

    def close_app(self):
        if self.server: 
            self.server.kill()
        self.root.destroy()
        sys.exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = AILauncher(root)
    root.mainloop()
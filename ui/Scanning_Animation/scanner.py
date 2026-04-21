import os
import json
import time
from PyQt6.QtCore import QThread, pyqtSignal

class ImageScanner(QThread):
    # Live file address bhejne ke liye signal
    progress_signal = pyqtSignal(str)
    # Scanning khatam hone par results bhejne ke liye signal
    finished_signal = pyqtSignal(list)

    def __init__(self, paths_to_scan=None, extensions=None, callback=None):
        super().__init__()
        self.callback = callback
        self.paths_to_scan = paths_to_scan if paths_to_scan else [os.path.expanduser("~")]
        
        # Extension logic: .jpg aur .jpeg dono ko handle karega
        processed_extensions = []
        if extensions:
            for ext in extensions:
                ext = ext.lower()
                processed_extensions.append(ext)
                if ext == ".jpg" and ".jpeg" not in extensions:
                    processed_extensions.append(".jpeg")
                elif ext == ".jpeg" and ".jpg" not in extensions:
                    processed_extensions.append(".jpg")
            self.extensions = tuple(processed_extensions)
        else:
            self.extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')

        self.found_files = []
        self.is_finished = False

    def run(self):
        self.found_files = [] 
        
        for target in self.paths_to_scan:
            if not os.path.exists(target):
                continue
            
            for root, dirs, files in os.walk(target):
                # Har folder ke andar ki files ko iterate karna
                for file in files:
                    full_path = os.path.normpath(os.path.join(root, file))
                    
                    # --- LIVE EMIT: Har file ka path UI ko bhejna ---
                    self.progress_signal.emit(full_path)
                    
                    # Chota sa delay taake UI par path "flow" hota nazar aaye
                    # Isse scanning ki real speed ka ehsas hoga
                    time.sleep(0.001) 
                    
                    if file.lower().endswith(self.extensions):
                        self.found_files.append(full_path)
        
        # DB.json update
        db_path = os.path.join(os.getcwd(), "DB.json")
        try:
            with open(db_path, "w") as f:
                json.dump({"images": self.found_files}, f, indent=4)
        except Exception as e:
            print(f"Error saving DB: {e}")

        self.is_finished = True
        
        if self.callback:
            self.callback(self.found_files)
        
        self.finished_signal.emit(self.found_files)
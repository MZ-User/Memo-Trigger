import os
import sqlite3
import time
from PyQt6.QtCore import QThread, pyqtSignal

class ImageScanner(QThread):
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list)

    def __init__(self, paths_to_scan=None, extensions=None, callback=None):
        super().__init__()
        self.callback = callback
        self.db_name = "memo_trigger.db"
        self.paths_to_scan = paths_to_scan if paths_to_scan else [os.path.expanduser("~")]
        
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

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
        ''')
        cursor.execute("DELETE FROM scan_results")
        conn.commit()
        return conn

    def run(self):
        self.found_files = [] 
        
        for target in self.paths_to_scan:
            if not os.path.exists(target):
                continue
            
            for root, dirs, files in os.walk(target):
                for file in files:
                    full_path = os.path.normpath(os.path.join(root, file))
                    self.progress_signal.emit(full_path)
                    time.sleep(0.001) 
                    
                    if file.lower().endswith(self.extensions):
                        self.found_files.append(full_path)
        
        try:
            conn = self.init_db()
            cursor = conn.cursor()
            for path in self.found_files:
                if os.path.exists(path):
                    ts = os.path.getctime(path)
                    cursor.execute("INSERT INTO scan_results (file_path, timestamp) VALUES (?, ?)", 
                                   (path, ts))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Database Error: {e}")

        if self.callback:
            self.callback(self.found_files)
        
        self.finished_signal.emit(self.found_files)
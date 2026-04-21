import os
import psutil
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFrame, QFileDialog, QScrollArea,
                             QApplication, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QSize
from PyQt6.QtGui import QFont, QPixmap, QColor

class CustomButton(QPushButton):
    def __init__(self, text, neon_blue, dark_blue, parent=None):
        super().__init__(text, parent)
        self.nb = neon_blue
        self.db = dark_blue
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.set_normal_style()

    def set_normal_style(self):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self.nb}; color: {self.db}; border: 2px solid {self.db};
                font-weight: 900; border-radius: 25px; font-size: 18px; margin: 0px;
            }}
        """)

    def enterEvent(self, event):
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self.db}; color: {self.nb}; border: 2px solid {self.nb};
                font-weight: 900; border-radius: 25px; font-size: 18px; margin: -2px;
            }}
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.set_normal_style()
        super().leaveEvent(event)

class OptionsPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.neon_blue = "#00F2FF"
        self.dark_blue = "#001A33"
        self.selected_paths = []
        self.selected_extensions = {".jpg", ".png", ".pdf", ".mp4", ".txt"} # Default types
        self.init_ui()

    def init_ui(self):
        # Background
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("static/images/bg.jpg"))
        self.bg_label.setScaledContents(True)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)

        # Dark Box Container
        self.dark_box = QFrame(self)
        self.dark_box.setStyleSheet("background-color: rgba(0, 0, 0, 230); border-radius: 30px;")
        self.box_layout = QVBoxLayout(self.dark_box)
        self.box_layout.setContentsMargins(35, 35, 35, 35)

        # Main Heading (Restored to large size)
        self.heading = QLabel("Where To Search?")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading.setStyleSheet(f"color: white; font-weight: 800; font-size: 42px; padding-bottom: 5px;")
        self.box_layout.addWidget(self.heading)

        # Header Row (Drives Label + Scan Settings Button)
        header_row_widget = QWidget()
        h_layout = QHBoxLayout(header_row_widget)
        h_layout.setContentsMargins(0, 0, 0, 0)
        
        d_label = QLabel("Drives:")
        d_label.setStyleSheet(f"color: {self.neon_blue}; font-weight: bold; font-size: 24px;")
        h_layout.addWidget(d_label)
        h_layout.addStretch()

        self.settings_btn = QPushButton("Scan Settings")
        self.settings_btn.setFixedSize(160, 45) # Increased size
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton { 
                background: white; color: black; font-weight: 900; 
                border-radius: 8px; font-size: 16px;
            }
            QPushButton:hover { background: #D3D3D3; }
        """)
        self.settings_btn.clicked.connect(self.open_side_panel)
        h_layout.addWidget(self.settings_btn)
        self.box_layout.addWidget(header_row_widget)

        # Increased Space between "Drives:" row and first drive name (2.5x spacing logic)
        self.box_layout.addSpacing(40) 

        # Scroll Area for Drives
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("background: transparent; border: none;")
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(15) # Normal spacing between drive rows
        self.scroll.setWidget(self.scroll_content)
        self.box_layout.addWidget(self.scroll)

        self.refresh_drives()

        # Bottom Buttons
        bottom_btns = QHBoxLayout()
        self.start_btn = CustomButton("START SCANNING", self.neon_blue, self.dark_blue, self)
        self.start_btn.setFixedSize(220, 60)
        self.start_btn.clicked.connect(self.execute_final_scan)

        self.home_btn = CustomButton("HOME", self.neon_blue, self.dark_blue, self)
        self.home_btn.setFixedSize(180, 60)
        self.home_btn.clicked.connect(self.go_home)

        bottom_btns.addStretch()
        bottom_btns.addWidget(self.start_btn)
        bottom_btns.addSpacing(30)
        bottom_btns.addWidget(self.home_btn)
        bottom_btns.addStretch()
        self.box_layout.addLayout(bottom_btns)

        self.main_layout.addWidget(self.dark_box)

        # --- SIDE PANEL UI (Cleanup version) ---
        self.side_panel = QFrame(self)
        self.side_panel.setFixedWidth(240)
        self.side_panel.setStyleSheet(f"background-color: {self.dark_blue}; border-left: 2px solid {self.neon_blue}; border-top-left-radius: 20px; border-bottom-left-radius: 20px;")
        self.side_panel.move(self.width(), 0)

        panel_layout = QVBoxLayout(self.side_panel)
        panel_layout.setContentsMargins(20, 20, 20, 20)
        
        # Close Button
        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(35, 35)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton { background: white; color: black; font-weight: bold; border-radius: 5px; font-size: 16px; }
            QPushButton:hover { background: red; color: white; }
        """)
        self.close_btn.clicked.connect(self.close_side_panel)
        panel_layout.addWidget(self.close_btn)

        panel_layout.addSpacing(30)
        
        ft_label = QLabel("File Types:")
        ft_label.setStyleSheet(f"color: {self.neon_blue}; font-size: 22px; font-weight: bold; border: none;")
        panel_layout.addWidget(ft_label)
        panel_layout.addSpacing(10)

        # All Button
        self.all_btn = self.create_type_chip("All", is_action=True)
        self.all_btn.clicked.connect(self.select_all_exts)
        panel_layout.addWidget(self.all_btn)

        # Scrollable Extension List (Indented)
        self.ext_scroll = QScrollArea()
        self.ext_scroll.setWidgetResizable(True)
        self.ext_scroll.setStyleSheet("background: transparent; border: none;")
        ext_widget = QWidget()
        self.ext_v_layout = QVBoxLayout(ext_widget)
        self.ext_v_layout.setContentsMargins(15, 5, 0, 5) # Indentation
        self.ext_v_layout.setSpacing(8)
        
        self.ext_list = [".jpg", ".png", ".pdf", ".svg", ".webp", ".mp4", ".txt", ".exe", ".zip", ".docx", ".mp3"]
        self.chip_widgets = {}
        
        for ext in self.ext_list:
            btn = self.create_type_chip(ext)
            btn.clicked.connect(lambda ch, e=ext: self.toggle_extension(e))
            self.chip_widgets[ext] = btn
            self.ext_v_layout.addWidget(btn)
        
        self.ext_scroll.setWidget(ext_widget)
        panel_layout.addWidget(self.ext_scroll)
        
        # Deselect All Button
        self.deselect_btn = self.create_type_chip("Deselect All", is_action=True)
        self.deselect_btn.clicked.connect(self.deselect_all_exts)
        panel_layout.addWidget(self.deselect_btn)
        
        panel_layout.addStretch()

    def create_type_chip(self, text, is_action=False):
        btn = QPushButton(text)
        btn.setFixedHeight(35)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_chip_style(btn, text in self.selected_extensions if not is_action else False)
        return btn

    def update_chip_style(self, btn, is_selected):
        if is_selected:
            btn.setStyleSheet(f"background-color: {self.neon_blue}; color: {self.dark_blue}; font-weight: bold; border-radius: 5px; text-align: left; padding-left: 15px; font-size: 14px; border: none;")
        else:
            btn.setStyleSheet("background-color: transparent; color: white; border-radius: 5px; text-align: left; padding-left: 15px; font-size: 14px; border: none;")

    def toggle_extension(self, ext):
        if ext in self.selected_extensions:
            self.selected_extensions.remove(ext)
        else:
            self.selected_extensions.add(ext)
        self.update_chip_style(self.chip_widgets[ext], ext in self.selected_extensions)

    def select_all_exts(self):
        for ext in self.ext_list:
            self.selected_extensions.add(ext)
            if ext in self.chip_widgets: self.update_chip_style(self.chip_widgets[ext], True)

    def deselect_all_exts(self):
        self.selected_extensions.clear()
        for ext in self.ext_list:
            if ext in self.chip_widgets: self.update_chip_style(self.chip_widgets[ext], False)

    def open_side_panel(self):
        self.side_panel.setFixedHeight(self.height())
        self.side_anim = QPropertyAnimation(self.side_panel, b"pos")
        self.side_anim.setDuration(400)
        self.side_anim.setStartValue(QPoint(self.width(), 0))
        self.side_anim.setEndValue(QPoint(self.width() - 240, 0))
        self.side_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.side_panel.raise_()
        self.side_anim.start()

    def close_side_panel(self):
        self.side_anim = QPropertyAnimation(self.side_panel, b"pos")
        self.side_anim.setDuration(300)
        self.side_anim.setStartValue(self.side_panel.pos())
        self.side_anim.setEndValue(QPoint(self.width(), 0))
        self.side_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        self.side_anim.start()

    def refresh_drives(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for drive in psutil.disk_partitions():
            try:
                if 'cdrom' in drive.opts or drive.fstype == "": continue
                drive_name = "Local Disk"
                try:
                    import ctypes
                    buf = ctypes.create_unicode_buffer(1024)
                    ctypes.windll.kernel32.GetVolumeInformationW(drive.mountpoint, buf, 1024, None, None, None, None, 0)
                    if buf.value: drive_name = buf.value
                except: pass

                row = QFrame()
                row.setStyleSheet("background: rgba(255,255,255,12); border-radius: 12px;")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(15, 10, 15, 10)
                
                name = QLabel(f"{drive_name} ({drive.mountpoint})")
                name.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
                row_layout.addWidget(name)

                path_display = QLabel("")
                path_display.setStyleSheet("color: #00F2FF; font-size: 13px; font-style: italic;")
                row_layout.addWidget(path_display, 1)
                
                # Action Buttons (Increased Size)
                sf_btn = QPushButton("Select Folder")
                sa_btn = QPushButton("Scan All")
                for btn in [sf_btn, sa_btn]:
                    btn.setFixedSize(130, 40)
                    btn.setCursor(Qt.CursorShape.PointingHandCursor)
                    btn.setStyleSheet("""
                        QPushButton { 
                            background: white; color: black; font-weight: 900; 
                            border-radius: 6px; font-size: 14px;
                        } 
                        QPushButton:hover { background: #E0E0E0; }
                    """)
                
                sf_btn.clicked.connect(lambda ch, p=drive.mountpoint, lbl=path_display: self.select_folder(p, lbl))
                sa_btn.clicked.connect(lambda ch, p=drive.mountpoint: self.direct_scan_all(p))
                
                row_layout.addWidget(sf_btn)
                row_layout.addSpacing(10)
                row_layout.addWidget(sa_btn)
                self.scroll_layout.addWidget(row)
            except: continue
        self.scroll_layout.addStretch()

    def select_folder(self, drive_path, label):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", drive_path)
        if folder:
            if folder not in self.selected_paths: self.selected_paths.append(folder)
            metrics = label.fontMetrics()
            label.setText(metrics.elidedText(folder, Qt.TextElideMode.ElideMiddle, 250))

    def direct_scan_all(self, drive_path):
        # Scan entire drive with selected extensions
        self.start_scan([drive_path])

    def execute_final_scan(self):
        if self.selected_paths:
            self.start_scan(self.selected_paths)

    def start_scan(self, paths):
        # Redirecting to animation.py and passing data to scanner logic
        if hasattr(self.parent, 'trigger_animation'):
            # Passing list of paths and list of selected extensions
            self.parent.trigger_animation(paths, list(self.selected_extensions))

    def go_home(self):
        if hasattr(self.parent, 'show_dashboard'): self.parent.show_dashboard()

    def resizeEvent(self, event):
        self.bg_label.setGeometry(self.rect())
        self.side_panel.setFixedHeight(self.height())
        if self.side_panel.x() < self.width():
             self.side_panel.move(self.width() - 240, 0)
        else:
             self.side_panel.move(self.width(), 0)
        super().resizeEvent(event)
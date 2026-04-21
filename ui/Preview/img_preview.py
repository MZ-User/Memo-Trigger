import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QHBoxLayout, QPushButton, QMenu, QFileIconProvider
from PyQt6.QtCore import Qt, QRect, QSize, QPoint, QFileInfo
from PyQt6.QtGui import QPixmap, QFont, QAction, QGuiApplication, QColor, QIcon
from datetime import datetime

class ImagePreviewOverlay(QFrame):
    def __init__(self, parent, img_list, current_index):
        super().__init__(parent)
        self.parent = parent
        self.img_list = img_list # Metadata list (path, time)
        self.current_idx = current_index
        
        self.setGeometry(parent.rect())
        self.setStyleSheet("background-color: rgba(0, 0, 0, 245);")
        self.setMouseTracking(True)
        
        # Keyboard focus enable karna zaroori hai
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setFocus()

        self.init_ui()
        self.update_content()

    def init_ui(self):
        # Top Header Requirement: Name (Left) | Date-Time (Center) | Close (Right)
        self.header = QFrame(self)
        self.header.setGeometry(20, 20, self.width()-40, 80)
        self.header.setStyleSheet("background: transparent;")
        h_layout = QHBoxLayout(self.header)

        # 1. Name Box
        self.name_frame = QFrame()
        self.name_frame.setStyleSheet("background: rgba(255,255,255,20); border-radius: 10px; padding: 5px;")
        self.name_lbl = QLabel()
        self.name_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 16px; border: none;")
        QVBoxLayout(self.name_frame).addWidget(self.name_lbl)
        
        # 2. Date-Time Box (Yellow Bold)
        self.dt_frame = QFrame()
        self.dt_frame.setStyleSheet("background: rgba(255,255,255,10); border-radius: 15px; border: 1px solid #FFFF00;")
        self.dt_lbl = QLabel()
        self.dt_lbl.setStyleSheet("color: #FFFF00; font-family: 'Impact'; font-size: 22px; border: none; padding: 0 20px;")
        QVBoxLayout(self.dt_frame).addWidget(self.dt_lbl)

        # 3. Close Box (Red Hover Effect)
        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(50, 50)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #00F2FF; color: #001A33; 
                font-size: 24px; font-weight: bold; border-radius: 10px;
            }
            QPushButton:hover { background-color: #FF0000; color: white; }
        """)
        self.close_btn.clicked.connect(self.deleteLater)

        h_layout.addWidget(self.name_frame)
        h_layout.addStretch()
        h_layout.addWidget(self.dt_frame)
        h_layout.addStretch()
        h_layout.addWidget(self.close_btn)

        # Main Image Area
        self.img_container = QLabel(self)
        self.img_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_container.setGeometry(100, 120, self.width()-200, self.height()-200)
        
        # UI/UX: Context Menu for Image
        self.img_container.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.img_container.customContextMenuRequested.connect(self.show_copy_menu)

        # Navigation Arrows
        self.left_btn = self.create_nav_arrow("<")
        self.right_btn = self.create_nav_arrow(">")
        self.left_btn.clicked.connect(self.prev_img)
        self.right_btn.clicked.connect(self.next_img)

    def create_nav_arrow(self, txt):
        btn = QPushButton(txt, self)
        btn.setFixedSize(70, 120)
        btn.hide()
        btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 242, 255, 30); color: white;
                border: 2px solid #00F2FF; border-radius: 15px; font-size: 40px;
            }
            QPushButton:hover { background: #00F2FF; color: #001A33; }
            QPushButton:pressed { padding-left: 5px; }
        """)
        return btn

    def update_content(self):
        path, ts = self.img_list[self.current_idx]
        dt = datetime.fromtimestamp(ts)
        
        # Top Bar Update
        self.name_lbl.setText(os.path.basename(path))
        self.dt_lbl.setText(f"{dt.strftime('%d-%m-%Y')}  |  {dt.strftime('%I:%M %p')}")
        
        # --- UPDATED ICON/IMAGE LOGIC ---
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
            pix = QPixmap(path)
        else:
            # Non-image files ke liye system icon fetch karna
            file_info = QFileInfo(path)
            icon = QFileIconProvider().icon(file_info)
            # 256x256 quality icon for preview
            pix = icon.pixmap(256, 256)

        if not pix.isNull():
            self.img_container.setPixmap(pix.scaled(self.img_container.size(), 
                                         Qt.AspectRatioMode.KeepAspectRatio, 
                                         Qt.TransformationMode.SmoothTransformation))
        else:
            self.img_container.setText("No Preview Available")
            self.img_container.setStyleSheet("color: white; font-size: 20px;")

    def prev_img(self):
        if self.current_idx > 0:
            self.current_idx -= 1
            self.update_content()

    def next_img(self):
        if self.current_idx < len(self.img_list) - 1:
            self.current_idx += 1
            self.update_content()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.prev_img()
        elif event.key() == Qt.Key.Key_Right:
            self.next_img()
        elif event.key() == Qt.Key.Key_Escape:
            self.deleteLater()
        else:
            super().keyPressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position().x()
        if pos < 150 and self.current_idx > 0:
            self.left_btn.move(20, self.height()//2 - 60)
            self.left_btn.show()
        elif pos > self.width() - 150 and self.current_idx < len(self.img_list) - 1:
            self.right_btn.move(self.width() - 90, self.height()//2 - 60)
            self.right_btn.show()
        else:
            self.left_btn.hide()
            self.right_btn.hide()

    def show_copy_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { font-weight: 900; background: white; border: 1px solid black; }
            QMenu::item { color: black; padding: 10px 20px; }
            QMenu::item:selected { background: lightgray; }
            """)
        copy = QAction("Copy Path", self)
        copy.triggered.connect(lambda: QGuiApplication.clipboard().setText(self.img_list[self.current_idx][0]))
        menu.addAction(copy)
        menu.exec(self.img_container.mapToGlobal(pos))
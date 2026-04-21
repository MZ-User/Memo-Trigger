import os
import json
from PyQt6.QtWidgets import (QWidget, QLabel, QFrame, QPushButton, QGraphicsDropShadowEffect, 
                             QVBoxLayout, QHBoxLayout, QScrollArea)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QEvent, QTimer
from PyQt6.QtGui import QFont, QColor

class DashboardPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Colors & Constants
        self.neon_blue = "#00F2FF"
        self.dark_blue = "#001A33"
        self.dark_box_bg = "rgba(0, 0, 0, 180)"
        self.dense_white = "rgba(255, 255, 255, 0.6)" 
        
        # Minimum Constraints
        self.setMinimumSize(300, 400)
        
        # DEBUG: Initial Geometry Setup
        if self.parent:
            self.setGeometry(self.parent.rect())

        # 16ms Trigger for Geometry Fix
        self.sync_timer = QTimer(self)
        self.sync_timer.setSingleShot(True)
        self.sync_timer.timeout.connect(self.apply_initial_sync)

        self.init_ui()

    def showEvent(self, event):
        """Page show hote hi 16ms baad sync trigger karega"""
        super().showEvent(event)
        self.sync_timer.start(16)

    def apply_initial_sync(self):
        """Corner bug fix: Parent geometry se sync aur UI refresh"""
        if self.parent:
            self.setGeometry(self.parent.rect())
        self.update_ui_scaling()

    def init_ui(self):
        # Main Layout
        self.page_layout = QVBoxLayout(self)
        self.page_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 30); 
                width: 14px; border-radius: 7px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.dark_blue}; 
                border: 3px solid rgba(255, 255, 255, 50); 
                min-height: 40px; border-radius: 7px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        # Container
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0, 20, 0, 20)
        self.layout.setSpacing(40)

        # LOGO SECTION
        self.d_logo_bg = QFrame()
        self.d_logo_bg.setStyleSheet(f"background-color: {self.dense_white}; border-radius: 15px; min-height: 90px;")
        logo_inner = QVBoxLayout(self.d_logo_bg)
        self.d_logo = QLabel("Memo Trigger")
        self.d_logo.setStyleSheet(f"color: {self.dark_blue}; background: transparent;")
        self.d_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.apply_shadow(self.d_logo, "white")
        logo_inner.addWidget(self.d_logo)

        # WELCOME SECTION
        self.d_bar1 = QFrame()
        self.d_bar1.setStyleSheet(f"background-color: {self.dark_box_bg}; min-height: 75px;")
        bar1_layout = QVBoxLayout(self.d_bar1)
        self.d_welcome = QLabel("Welcome!")
        self.d_welcome.setStyleSheet(f"color: {self.neon_blue}; background: transparent;")
        self.d_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar1_layout.addWidget(self.d_welcome)

        # TAGLINE SECTION
        self.d_bar2 = QFrame()
        self.d_bar2.setStyleSheet(f"background-color: {self.dark_box_bg}; min-height: 75px;")
        bar2_layout = QVBoxLayout(self.d_bar2)
        self.d_tagline = QLabel("Click on Start\nTo See Your Past")
        self.d_tagline.setStyleSheet(f"color: {self.neon_blue}; background: transparent;")
        self.d_tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bar2_layout.addWidget(self.d_tagline)

        # BUTTONS SECTION
        self.btn_container = QWidget()
        self.btn_layout = QHBoxLayout(self.btn_container)
        
        self.exit_btn = QPushButton("EXIT")
        self.start_btn = QPushButton("START")
        
        for b in [self.exit_btn, self.start_btn]:
            b.setMouseTracking(True)
            b.installEventFilter(self)
            b.setFixedSize(160, 55)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            self.set_btn_style(b, "normal")

        self.start_btn.clicked.connect(self.handle_start_click)
        self.exit_btn.clicked.connect(self.handle_exit_click)

        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.exit_btn)
        self.btn_layout.addWidget(self.start_btn)
        self.btn_layout.addStretch()

        # Vertical Structure
        self.layout.addStretch(2)
        self.layout.addWidget(self.d_logo_bg)
        self.layout.addStretch(1)
        self.layout.addWidget(self.d_bar1)
        self.layout.addStretch(1)
        self.layout.addWidget(self.d_bar2)
        self.layout.addStretch(1)
        self.layout.addWidget(self.btn_container)
        self.layout.addStretch(2)

        self.scroll.setWidget(self.container)
        self.page_layout.addWidget(self.scroll)

    def set_btn_style(self, btn, state):
        if state == "normal":
            btn.setStyleSheet(f"background: {self.neon_blue}; color: {self.dark_blue}; font-weight: 900; border-radius: 25px; border: 2px solid {self.dark_blue}; font-size: 16px;")
        elif state == "hover":
            btn.setStyleSheet(f"background: {self.dark_blue}; color: {self.neon_blue}; font-weight: 900; border-radius: 25px; border: 2px solid {self.neon_blue}; font-size: 16px;")
        elif state == "active":
            btn.setStyleSheet(f"background: {self.neon_blue}; color: {self.dark_blue}; font-weight: 900; border-radius: 25px; border: 4px solid {self.dark_blue}; font-size: 16px;")

    def apply_shadow(self, widget, color):
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(15)
        sh.setColor(QColor(color))
        sh.setOffset(0, 0)
        widget.setGraphicsEffect(sh)

    def handle_start_click(self):
        if hasattr(self.parent, 'show_options'):
            self.parent.show_options()

    def handle_exit_click(self):
        db_path = os.path.join(os.getcwd(), "DB.json")
        try:
            with open(db_path, "w") as f:
                json.dump({"images": []}, f)
        except: pass
        os._exit(0)

    def eventFilter(self, obj, event):
        if isinstance(obj, QPushButton):
            if event.type() == QEvent.Type.Enter: self.set_btn_style(obj, "hover")
            elif event.type() == QEvent.Type.Leave: self.set_btn_style(obj, "normal")
            elif event.type() == QEvent.Type.MouseButtonPress: self.set_btn_style(obj, "active")
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if obj.underMouse(): self.set_btn_style(obj, "hover")
        return super().eventFilter(obj, event)

    def update_ui_scaling(self):
        """Responsive scaling refresh"""
        w = self.width()
        logo_f = max(int(w * 0.08), 30)
        welcome_f = max(int(w * 0.06), 25)
        tag_f = max(int(w * 0.025), 14)
        
        self.btn_layout.setSpacing(int(w * 0.05))
        self.d_logo.setFont(QFont(self.parent.custom_font, logo_f))
        self.d_welcome.setFont(QFont(self.parent.custom_font, welcome_f))
        self.d_tagline.setFont(QFont("Verdana", tag_f, QFont.Weight.Bold))

    def resizeEvent(self, event):
        self.update_ui_scaling()
        super().resizeEvent(event)
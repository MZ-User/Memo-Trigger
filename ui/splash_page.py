import math
from PyQt6.QtWidgets import (QWidget, QLabel, QFrame, QGraphicsDropShadowEffect, 
                             QVBoxLayout, QScrollArea, QSpacerItem, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor

class SplashPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        # Constraints: Minimum width 300px, Minimum height 400px
        self.setMinimumWidth(300)
        self.setMinimumHeight(400)
        
        self.neon_blue = "#00F2FF"
        self.dark_blue = "#001A33"
        self.dark_box_bg = "rgba(0, 0, 0, 180)"
        self.anim_val = 0
        
        self.init_ui()

    def init_ui(self):
        # 1. Main Page Layout
        self.page_layout = QVBoxLayout(self)
        self.page_layout.setContentsMargins(0, 0, 0, 0)

        # 2. SCROLL AREA (Keeping your exact scrollbar styles)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: rgba(255, 255, 255, 30); 
                width: 14px; 
                margin: 0px;
                border-radius: 7px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.dark_blue}; 
                border: 3px solid rgba(255, 255, 255, 50); 
                min-height: 40px;
                border-radius: 7px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
        """)

        # 3. CONTENT CONTAINER
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.layout = QVBoxLayout(self.container)
        
        # Equal and increased spacing for vertical alignment
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(60) # Constant gap between bars

        # --- HEADING SECTION ---
        self.s_bar1 = QFrame()
        self.s_bar1.setStyleSheet(f"background-color: {self.dark_box_bg}; border: none;")
        self.s_bar1.setMinimumHeight(120) # Slightly increased for visibility
        bar1_layout = QVBoxLayout(self.s_bar1)
        
        self.s_heading = QLabel("Memo Trigger")
        self.s_heading.setStyleSheet(f"color: {self.neon_blue}; border: none; background: transparent;")
        self.s_heading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.s_heading.setWordWrap(True)
        self.apply_shadow(self.s_heading)
        bar1_layout.addWidget(self.s_heading)
        
        # --- TAGLINE SECTION ---
        self.s_bar2 = QFrame()
        self.s_bar2.setStyleSheet(f"background-color: {self.dark_box_bg}; border: none;")
        self.s_bar2.setMinimumHeight(80)
        bar2_layout = QVBoxLayout(self.s_bar2)

        self.s_tagline = QLabel("Launching App In Windows")
        self.s_tagline.setStyleSheet("color: white; border: none; background: transparent;")
        self.s_tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.s_tagline.setWordWrap(True)
        self.apply_shadow(self.s_tagline)
        bar2_layout.addWidget(self.s_tagline)

        # --- LOADER SECTION ---
        self.loader_parent = QWidget()
        self.loader_parent.setFixedSize(200, 100)
        self.loader_boxes = [QFrame(self.loader_parent) for _ in range(4)]
        for box in self.loader_boxes:
            box.setFixedSize(22, 38)
            box.setStyleSheet(f"background-color: {self.dark_blue}; border: 1px solid {self.neon_blue};")

        # --- VERTICAL SPACING LOGIC ---
        # Stretch adds equal dynamic space at top, middle, and bottom
        self.layout.addStretch(2)
        self.layout.addWidget(self.s_bar1)
        self.layout.addStretch(1)
        self.layout.addWidget(self.s_bar2)
        self.layout.addStretch(1)
        self.layout.addWidget(self.loader_parent, 0, Qt.AlignmentFlag.AlignCenter)
        self.layout.addStretch(2)

        self.scroll.setWidget(self.container)
        self.page_layout.addWidget(self.scroll)

        # Animation Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)

    def apply_shadow(self, widget):
        outline = QGraphicsDropShadowEffect()
        outline.setBlurRadius(4)
        outline.setColor(QColor("white"))
        outline.setOffset(0, 0)
        widget.setGraphicsEffect(outline)

    def animate(self):
        self.anim_val += 0.05
        w = self.width()
        
        # Dynamic Font Scaling
        head_font_size = max(int(w * 0.08), 28)
        tag_font_size = max(int(w * 0.025), 14)
        
        self.s_heading.setFont(QFont(self.parent.custom_font, head_font_size, QFont.Weight.Bold))
        self.s_tagline.setFont(QFont("Verdana", tag_font_size, QFont.Weight.Bold))

        # Loader Boxes Wave Animation
        for i, box in enumerate(self.loader_boxes):
            box.move(i * 45 + 10, int(30 + math.sin(self.anim_val * 3 - (i * 0.8)) * 20))

    def resizeEvent(self, event):
        # Auto-adjust scroll area to fill SplashPage
        self.scroll.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)
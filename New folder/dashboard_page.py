from PyQt6.QtWidgets import QWidget, QLabel, QFrame, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QEvent
from PyQt6.QtGui import QFont, QColor

class DashboardPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.resize(self.parent.size())
        
        self.neon_blue = "#00F2FF"
        self.dark_blue = "#001A33"
        self.dark_box_bg = "rgba(0, 0, 0, 180)"
        self.dense_white = "rgba(255, 255, 255, 0.6)" # 60% Density
        
        self.init_ui()

    def init_ui(self):
        # 1. Logo Section
        self.d_logo_bg = QFrame(self)
        self.d_logo_bg.setStyleSheet(f"background-color: {self.dense_white}; border-radius: 15px;")
        
        self.d_logo = QLabel("Memo Trigger", self)
        self.d_logo.setStyleSheet(f"color: {self.dark_blue};")
        self.d_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.apply_shadow(self.d_logo, "white")

        # 2. Welcome Section
        self.d_bar1 = QFrame(self)
        self.d_bar1.setStyleSheet(f"background-color: {self.dark_box_bg};")
        
        self.d_welcome = QLabel("Welcome!", self)
        self.d_welcome.setStyleSheet(f"color: {self.neon_blue};")
        self.d_welcome.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 3. Tagline Section
        self.d_bar2 = QFrame(self)
        self.d_bar2.setStyleSheet(f"background-color: {self.dark_box_bg};")

        self.d_tagline = QLabel("Click on Start\nTo See Your Past", self)
        self.d_tagline.setStyleSheet(f"color: {self.neon_blue};")
        self.d_tagline.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 4. START Button
        self.btn = QPushButton("START", self)
        self.btn.setMouseTracking(True)
        self.btn.installEventFilter(self)
        self.set_btn_style("normal")
        self.btn.clicked.connect(self.parent.start_scanning)
        
        self.update_positions()

    def set_btn_style(self, state):
        if state == "normal":
            self.btn.setStyleSheet(f"background-color: {self.neon_blue}; color: {self.dark_blue}; font-weight: 900; border-radius: 25px; border: 2px solid {self.dark_blue};")
        elif state == "hover":
            self.btn.setStyleSheet(f"background-color: {self.dark_blue}; color: {self.neon_blue}; font-weight: 900; border-radius: 25px; border: 2px solid {self.neon_blue};")
        elif state == "active":
            self.btn.setStyleSheet(f"background-color: {self.neon_blue}; color: {self.dark_blue}; font-weight: 900; border-radius: 25px; border: 2px solid {self.dark_blue};")

    def apply_shadow(self, widget, color):
        sh = QGraphicsDropShadowEffect()
        sh.setBlurRadius(15)
        sh.setColor(QColor(color))
        sh.setOffset(0, 0)
        widget.setGraphicsEffect(sh)

    def update_positions(self):
        w, h = self.width(), self.height()
        
        # --- SPACING LOGIC ---
        # Margin Top aur Bottom ko balance rakha hai
        margin_y = int(h * 0.1) 
        content_area_h = h - (2 * margin_y)
        
        # Font Sizes ko 'Clamp' kiya hai taake ye had se zyada bade na hon
        logo_font_size = min(int(w * 0.08), 55)
        welcome_font_size = min(int(w * 0.06), 45)
        tag_font_size = min(int(w * 0.025), 18)
        btn_font_size = min(int(w * 0.035), 22)

        # 1. Logo (Positioned at Top Margin)
        logo_w = int(w * 0.8)
        logo_h = min(int(h * 0.12), 100) # Max height limit taake space bache
        self.d_logo_bg.setGeometry(int((w-logo_w)/2), margin_y, logo_w, logo_h)
        self.d_logo.setGeometry(int((w-logo_w)/2), margin_y, logo_w, logo_h)
        self.d_logo.setFont(QFont(self.parent.custom_font, logo_font_size))

        # 2. Welcome (25% niche content area mein)
        welcome_y = margin_y + int(content_area_h * 0.28)
        bar_h = min(int(h * 0.1), 80)
        self.d_bar1.setGeometry(0, welcome_y, w, bar_h)
        self.d_welcome.setGeometry(0, welcome_y, w, bar_h)
        self.d_welcome.setFont(QFont(self.parent.custom_font, welcome_font_size))

        # 3. Tagline (55% niche content area mein)
        tag_y = margin_y + int(content_area_h * 0.55)
        self.d_bar2.setGeometry(0, tag_y, w, bar_h)
        self.d_tagline.setGeometry(0, tag_y, w, bar_h)
        self.d_tagline.setFont(QFont("Verdana", tag_font_size, QFont.Weight.Bold))

        # 4. Button (At Bottom Margin)
        btn_w = min(int(w * 0.35), 250)
        btn_h = min(int(h * 0.08), 65)
        self.btn_normal_rect = QRect(int((w - btn_w) / 2), h - margin_y - btn_h, btn_w, btn_h)
        self.btn.setGeometry(self.btn_normal_rect)
        self.btn.setFont(QFont("Verdana", btn_font_size, QFont.Weight.Bold))

    def eventFilter(self, obj, event):
        if obj == self.btn:
            if event.type() == QEvent.Type.Enter:
                self.set_btn_style("hover")
                self.animate_btn(self.btn_normal_rect.adjusted(-6, -3, 6, 3))
            elif event.type() == QEvent.Type.Leave:
                self.set_btn_style("normal")
                self.animate_btn(self.btn_normal_rect)
            elif event.type() == QEvent.Type.MouseButtonPress:
                self.set_btn_style("active")
                self.animate_btn(self.btn_normal_rect.adjusted(4, 2, -4, -2))
            elif event.type() == QEvent.Type.MouseButtonRelease:
                if self.btn.underMouse():
                    self.set_btn_style("hover")
                    self.animate_btn(self.btn_normal_rect.adjusted(-6, -3, 6, 3))
        return super().eventFilter(obj, event)

    def animate_btn(self, target_rect):
        self.anim = QPropertyAnimation(self.btn, b"geometry")
        self.anim.setDuration(120)
        self.anim.setEndValue(target_rect)
        self.anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.anim.start()

    def resizeEvent(self, event):
        self.update_positions()
        super().resizeEvent(event)
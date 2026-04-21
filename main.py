import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFontDatabase

# Set High DPI Scaling Policy before creating QApplication
if hasattr(Qt, 'HighDpiScaleFactorRoundingPolicy'):
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui import SplashPage, DashboardPage, ResultsPage, OptionsPage
from ui.Scanning_Animation.animation import ScanningAnimationPage

class SpendedMeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Memo Trigger")
        self.setMinimumSize(650, 800)
        
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Load Application Fonts
        font_path = os.path.join(self.base_dir, "static", "fonts", "Gwenchana.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        self.custom_font = QFontDatabase.applicationFontFamilies(font_id)[0] if font_id != -1 else "Impact"

        self.main_container = QWidget()
        self.setCentralWidget(self.main_container)
        
        # Background Setup
        self.bg_label = QLabel(self.main_container)
        self.update_background()

        self.current_screen = None
        self.show_splash()

    def update_background(self):
        bg_img = os.path.join(self.base_dir, "static", "images", "bg.jpg")
        pix = QPixmap(bg_img)
        if not pix.isNull():
            self.bg_label.setPixmap(pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
            self.bg_label.setGeometry(0, 0, self.width(), self.height())

    def resizeEvent(self, event):
        self.update_background()
        if self.current_screen and not self.current_screen.isHidden():
            try:
                self.current_screen.resize(self.size())
            except: pass
        super().resizeEvent(event)

    def clear_screen(self):
        if self.current_screen:
            self.current_screen.deleteLater()
            self.current_screen = None

    def show_splash(self):
        self.clear_screen()
        self.current_screen = SplashPage(self)
        self.current_screen.resize(self.size())
        self.current_screen.show()
        QTimer.singleShot(5000, self.show_dashboard)

    def show_dashboard(self):
        self.clear_screen()
        self.current_screen = DashboardPage(self)
        self.current_screen.resize(self.size())
        self.current_screen.show()

    def show_options(self):
        self.clear_screen()
        self.current_screen = OptionsPage(self)
        self.current_screen.resize(self.size())
        self.current_screen.show()

    def trigger_animation(self, paths, extensions=None):
        self.clear_screen()
        self.current_screen = ScanningAnimationPage(self)
        self.current_screen.resize(self.size())
        self.current_screen.show()
        
        if hasattr(self.current_screen, 'start_scanning_process'):
            self.current_screen.start_scanning_process(paths, extensions)

    def show_results(self):
        self.clear_screen()
        self.current_screen = ResultsPage(self)
        self.current_screen.resize(self.size())
        self.current_screen.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpendedMeApp()
    window.show()
    sys.exit(app.exec())
import math
import random
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, QPointF, QRectF, pyqtSlot
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QRadialGradient, QPixmap, QFont, QPainterPath, QConicalGradient, QFontMetrics

from .scanner import ImageScanner

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)

    def enterEvent(self, event):
        self.setStyleSheet("background: #00F2FF; color: #001A33; font-weight: bold; border-radius: 12px; margin: -2px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("background: white; color: #001A33; font-weight: bold; border-radius: 10px; margin: 0px;")
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.setStyleSheet(self.styleSheet() + "margin: 2px;")
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.setStyleSheet(self.styleSheet().replace("margin: 2px;", ""))
        super().mouseReleaseEvent(event)

class ScanningAnimationPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.neon_blue = QColor("#00F2FF")
        self.dark_neon = QColor(0, 150, 255, 180)
        self.dark_box_bg = QColor(0, 0, 0, 230)
        
        self.radar_angle = 0.0
        self.sphere_rotation = 0.0
        self.pulse_val = 0.0
        self.pop_images = []
        self.independent_dots = []
        self.scanning_complete = False
        self.min_time_passed = False
        
        self.setup_icon()
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_anim)

    def setup_icon(self):
        pix = QPixmap("static/images/icons.png")
        if pix.isNull():
            pix = QPixmap(23, 23)
            pix.fill(self.neon_blue)
        self.icon_pixmap = QPixmap(23, 23)
        self.icon_pixmap.fill(Qt.GlobalColor.transparent)
        p = QPainter(self.icon_pixmap)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, 23, 23), 6, 6)
        p.setClipPath(path)
        p.drawPixmap(0, 0, pix.scaled(23, 23, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        p.end()

    def init_ui(self):
        self.heading = QLabel("Finding and Loading Data ...", self)
        self.heading.setStyleSheet("color: white; font-weight: bold; background: transparent;")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.path_preview = QLabel("Initializing engine...", self)
        self.path_preview.setStyleSheet("color: #00F2FF; font-size: 11px; background: transparent;")
        self.path_preview.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.path_preview.setContentsMargins(15, 0, 0, 0)

        self.stop_btn = AnimatedButton("STOP", self)
        self.stop_btn.setFixedSize(100, 35)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setStyleSheet("background: white; color: #001A33; font-weight: bold; border-radius: 10px;")
        self.stop_btn.clicked.connect(self.handle_stop)

    def start_scanning_process(self, paths, extensions=None):
        self.scanning_complete = False
        self.min_time_passed = False
        self.start_time = datetime.now()
        self.pop_images = []
        self.independent_dots = []
        self.timer.start(16)
        QTimer.singleShot(8000, self.mark_min_time_done)
        self.scanner = ImageScanner(paths_to_scan=paths, extensions=extensions, callback=self.on_scan_finished)
        if hasattr(self.scanner, 'progress_signal'):
            self.scanner.progress_signal.connect(self.update_path_preview)
        self.scanner.start()

    @pyqtSlot(str)
    def update_path_preview(self, path):
        metrics = QFontMetrics(self.path_preview.font())
        available_width = self.path_preview.width() - 20
        elided_path = metrics.elidedText(f"Scanning: {path}", Qt.TextElideMode.ElideRight, available_width)
        self.path_preview.setText(elided_path)

    def mark_min_time_done(self):
        self.min_time_passed = True
        if self.scanning_complete:
            self.handle_stop()

    def on_scan_finished(self, results):
        self.scanning_complete = True
        if self.min_time_passed:
            QTimer.singleShot(500, self.handle_stop)

    def handle_stop(self):
        if hasattr(self.parent, 'show_results'): 
            self.parent.show_results()
        self.timer.stop()

    def update_anim(self):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        # 1. Reverse Radar Direction
        self.radar_angle = (self.radar_angle - 5.0) % 360
        
        # 2. Speed Control (Max 25 RPS approx logic)
        ramp = min(1.0, elapsed / 5.0)
        speed = 5.0 + (ramp * 20.0) 
        
        # 3. Reverse Sphere Direction
        self.sphere_rotation = (self.sphere_rotation - speed) % 360
        
        self.pulse_val = (math.sin(elapsed * 4) + 1) / 2 

        rx, ry = self.width() * 0.40, self.height() * 0.35
        
        if random.random() > 0.85:
            ang = math.radians(random.uniform(0, 360))
            dist = random.uniform(80, rx - 20)
            self.independent_dots.append({'pos': QPointF(dist * math.cos(ang), dist * math.sin(ang)), 'life': 255, 'birth': datetime.now()})

        for dot in self.independent_dots[:]:
            if (datetime.now() - dot['birth']).total_seconds() > 2.0:
                dot['life'] -= 10
                if dot['life'] <= 0: self.independent_dots.remove(dot)

        if random.random() > 0.93:
            ang = math.radians(random.uniform(0, 360))
            dist = random.uniform(85, rx - 35)
            self.pop_images.append({'pos': QPointF(dist * math.cos(ang), dist * math.sin(ang)), 'life': 0, 'birth': datetime.now(), 'state': 'wait'})

        for img in self.pop_images[:]:
            age = (datetime.now() - img['birth']).total_seconds()
            if img['state'] == 'wait':
                img['life'] = min(255, img['life'] + 25)
                if age > 1.0: img['state'] = 'dissolve'
            else:
                img['pos'] *= 0.93
                img['life'] -= 15
                if img['life'] <= 0: self.pop_images.remove(img)
        
        self.update()

    def paintEvent(self, event):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        box = QRectF(20, 20, w-40, h-40)
        cx, cy = box.center().x(), box.center().y() + 20
        rx, ry = box.width() * 0.40, box.height() * 0.35

        painter.setBrush(QBrush(self.dark_box_bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(box, 30, 30)

        main_oval_path = QPainterPath()
        main_oval_path.addEllipse(QRectF(cx-rx, cy-ry, rx*2, ry*2))
        
        painter.save()
        painter.setClipPath(main_oval_path)

        # 1. CYBER WEB
        painter.setPen(QPen(QColor(0, 242, 255, 60), 2))
        for i in range(0, 360, 45):
            rad = math.radians(i)
            painter.drawLine(QPointF(cx + 70*math.cos(rad), cy + 70*math.sin(rad)), QPointF(cx + rx*math.cos(rad), cy + ry*math.sin(rad)))
        painter.drawEllipse(QRectF(cx-rx*0.72, cy-ry*0.72, rx*1.44, ry*1.44))

        # 2. V-SHAPE SCANNER
        painter.save()
        painter.translate(cx, cy)
        inner_cut = QPainterPath()
        inner_cut.addEllipse(QRectF(-72, -72, 144, 144))
        painter.setClipPath(main_oval_path.translated(-cx, -cy).subtracted(inner_cut))
        painter.rotate(self.radar_angle)
        grad = QConicalGradient(0, 0, 0)
        grad.setColorAt(0, QColor(0, 242, 255, 180))
        grad.setColorAt(0.18, Qt.GlobalColor.transparent)
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPie(QRectF(-rx, -ry, rx*2, ry*2), 0, 45 * 16)
        painter.restore()

        # 3. ELECTRIC STORM (Refined & Controlled Pulse Out)
        painter.save()
        painter.translate(cx, cy)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Plus)
        
        for i in range(4):
            storm_rotation = (self.sphere_rotation * (1.2 + i * 0.4)) * (1 if i % 2 == 0 else -1)
            painter.rotate(storm_rotation % 360)
            
            base_radius = 95 
            # Controlled Pulse Out: Ab bahar zyada expand nahi karega
            dynamic_pulse = self.pulse_val * (15 + i * 10) 
            storm_radius = base_radius + dynamic_pulse
            
            electric_grad = QRadialGradient(0, 0, storm_radius)
            electric_grad.setColorAt(0.55, Qt.GlobalColor.transparent) 
            
            # Sharp Electric "Sparks" (White/Blue mix)
            spark_color = QColor(200, 250, 255, 200 - (i * 30))
            electric_grad.setColorAt(0.65, spark_color) 
            electric_grad.setColorAt(0.70, QColor(0, 150, 255, 150)) # Core blue
            electric_grad.setColorAt(0.85, QColor(0, 100, 255, 50))  # Fade out
            electric_grad.setColorAt(1.0, Qt.GlobalColor.transparent)
            
            painter.setBrush(QBrush(electric_grad))
            painter.setPen(Qt.PenStyle.NoPen)
            
            # Irregular shape for lightning feel
            crackle = 0.05 * math.sin(elapsed * 20 + i) 
            stretch = 0.85 + crackle
            painter.drawEllipse(QRectF(-storm_radius, -storm_radius * stretch, storm_radius * 2, storm_radius * stretch * 2))
            
        painter.restore()

        # 4. DOTS & IMAGES
        painter.save()
        painter.translate(cx, cy)
        for dot in self.independent_dots:
            dot_alpha = int((dot['life']/255) * (150 + self.pulse_val * 105))
            painter.setBrush(QBrush(QColor(0, 242, 255, dot_alpha)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(dot['pos'], 3, 3)
        for img in self.pop_images:
            painter.setOpacity(img['life']/255)
            painter.drawPixmap(int(img['pos'].x()-11), int(img['pos'].y()-11), self.icon_pixmap)
        painter.restore()
        painter.restore()

        # 5. CORE ENGINE
        painter.save()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.setOpacity(1.0) 
        painter.translate(cx, cy)
        painter.rotate(self.sphere_rotation)
        bright_neon = QColor("#00F2FF")
        bright_neon.setAlpha(255) 
        painter.setPen(QPen(bright_neon, 5, Qt.PenStyle.DashLine))
        painter.drawEllipse(-70, -70, 140, 140)
        connector_pen = QPen(bright_neon, 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(connector_pen)
        for _ in range(3):
            painter.rotate(120)
            painter.drawLine(QPointF(10, 0), QPointF(70, 0))
            painter.drawArc(-40, -40, 80, 80, 0, 55 * 16)
        painter.setBrush(QBrush(bright_neon))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(-10, -10, 20, 20)
        painter.restore()

        # 6. OUTER BORDER
        painter.setPen(QPen(self.neon_blue, 10))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QRectF(cx-rx, cy-ry, rx*2, ry*2))

        # UI POSITIONING
        self.heading.setGeometry(int(box.x()), int(box.y()+20), int(box.width()), 40)
        self.heading.setFont(QFont("Verdana", 16, QFont.Weight.Bold))
        self.path_preview.setGeometry(int(box.x() + 10), int(box.bottom() - 50), int(box.width() - 140), 35)
        self.stop_btn.move(int(box.right()-120), int(box.bottom()-50))
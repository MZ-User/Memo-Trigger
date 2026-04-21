import math
import random
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, QPoint, QSize, QRectF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QRadialGradient, QPixmap, QFont, QPainterPath

class LoadingPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.resize(self.parent.size())
        
        self.neon_blue = QColor("#00F2FF")
        self.dark_neon = QColor(0, 150, 200, 80) 
        self.dark_box_bg = QColor(0, 0, 0, 200)
        
        # FIX: Define attributes in init to avoid AttributeError
        self.radar_angle = 0.0
        self.sphere_rotation = 0.0
        self.current_rps_factor = 0.0 
        self.pop_images = []
        self.particles = []
        
        self.icon_pixmap = QPixmap("static/images/icons.png")
        if self.icon_pixmap.isNull():
            self.icon_pixmap = QPixmap(QSize(20, 20))
            self.icon_pixmap.fill(self.neon_blue)
        else:
            self.icon_pixmap = self.icon_pixmap.scaled(20, 20, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.init_ui()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_anim)
        self.timer.start(16)
        self.start_time = datetime.now()

    def init_ui(self):
        self.heading = QLabel("Finding and Loading Images", self)
        self.heading.setStyleSheet("color: white; font-weight: bold; background: transparent;")
        self.heading.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def update_anim(self):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.radar_angle = (self.radar_angle + 3.0) % 360
        
        # Speed: 0 to 15 RPS in 3s (Max 90 deg/frame)
        max_speed = 90.0
        self.current_rps_factor = min(1.0, elapsed / 3.0) 
        current_speed = 4.0 + (self.current_rps_factor * (max_speed - 4.0))
        self.sphere_rotation = (self.sphere_rotation + current_speed) % 360
        
        # Blips logic
        if random.random() > 0.92:
            self.particles.append({'ang': random.uniform(0, 360), 'dist': random.uniform(0.1, 0.95), 'life': 255})
        for p in self.particles[:]:
            p['life'] -= 3
            if p['life'] <= 0: self.particles.remove(p)

        # Oval Bounds for Logic
        w, h = self.width(), self.height()
        box_w, box_h = int(w * 0.9), int(h * 0.95)
        rx, ry = (box_w * 0.90) / 2, (box_h * 0.75) / 2
        cx, cy = w // 2, (h // 2) + 35
        sphere_r = 55

        # Popup Images
        if random.random() > 0.94:
            rand_ang = math.radians(random.uniform(0, 360))
            rand_dist = random.uniform(0.3, 0.9)
            px = cx + (rx * rand_dist * math.cos(rand_ang))
            py = cy + (ry * rand_dist * math.sin(rand_ang))
            self.pop_images.append({'pos': QPoint(int(px), int(py)), 'life': 0, 'state': 'pop', 'birth': datetime.now()})

        for img in self.pop_images[:]:
            if img['state'] == 'pop':
                if img['life'] < 255: img['life'] += 25
                if (datetime.now() - img['birth']).total_seconds() > 0.7: img['state'] = 'merge'
            else:
                target = QPoint(int(cx), int(cy))
                diff = target - img['pos']
                if math.sqrt(diff.x()**2 + diff.y()**2) > (sphere_r - 5):
                    img['pos'] += diff / 12
                else:
                    self.pop_images.remove(img)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        
        # 1. Background Box
        box_w, box_h = int(w * 0.9), int(h * 0.95)
        bx, by = (w - box_w)//2, (h - box_h)//2
        painter.setBrush(QBrush(self.dark_box_bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bx, by, box_w, box_h, 25, 25)

        self.heading.setGeometry(bx, by + 15, box_w, 40)
        self.heading.setFont(QFont("Verdana", int(w * 0.032)))

        rx, ry = (box_w * 0.90) / 2, (box_h * 0.75) / 2
        cx, cy = w // 2, (h // 2) + 35
        sphere_r = 55
        
        # Clipping Path
        clip_path = QPainterPath()
        clip_path.addEllipse(QRectF(cx - rx, cy - ry, rx * 2, ry * 2))
        painter.setClipPath(clip_path)

        painter.translate(cx, cy)

        # 2. Oval Web
        painter.setPen(QPen(QColor(0, 242, 255, 40), 2))
        for r_factor in [0.4, 0.7, 1.0]:
            painter.drawEllipse(QRectF(-rx*r_factor, -ry*r_factor, rx*r_factor*2, ry*r_factor*2))

        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            sx, sy = sphere_r * math.cos(rad), (sphere_r * (ry/rx)) * math.sin(rad)
            ox, oy = rx * math.cos(rad), ry * math.sin(rad)
            painter.drawLine(QPoint(int(sx), int(sy)), QPoint(int(ox), int(oy)))

        # 3. Scanning V-Shape
        painter.save()
        painter.rotate(-self.radar_angle)
        sweep_grad = QRadialGradient(0, 0, rx)
        sweep_grad.setColorAt(0, self.dark_neon)
        sweep_grad.setColorAt(1, QColor(0, 242, 255, 0))
        painter.setBrush(QBrush(sweep_grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPie(QRectF(-rx, -ry, rx*2, ry*2), 0, 40 * 16)
        painter.setPen(QPen(self.neon_blue, 2))
        painter.drawLine(sphere_r, 0, int(rx), 0)
        painter.restore()

        # 4. Dynamic Energy Field (Aura)
        if self.current_rps_factor > 0.4:
            aura_alpha = int(120 * self.current_rps_factor)
            aura_grad = QRadialGradient(0, 0, sphere_r + 25)
            aura_grad.setColorAt(0.6, QColor(0, 242, 255, 0))
            aura_grad.setColorAt(0.8, QColor(0, 242, 255, aura_alpha))
            aura_grad.setColorAt(1.0, QColor(0, 242, 255, 0))
            painter.setBrush(QBrush(aura_grad))
            painter.drawEllipse(-sphere_r-25, -sphere_r-25, (sphere_r+25)*2, (sphere_r+25)*2)

        # 5. Central Sphere (3 Thick C-Lines)
        painter.save()
        painter.rotate(self.sphere_rotation)
        painter.setPen(QPen(self.neon_blue, 10))
        painter.drawEllipse(-sphere_r, -sphere_r, sphere_r*2, sphere_r*2)
        
        painter.setPen(QPen(self.neon_blue, 7))
        for i in range(3):
            painter.rotate(120)
            painter.drawArc(QRectF(-sphere_r+10, -sphere_r+10, (sphere_r-10)*2, (sphere_r-10)*2), 30*16, 100*16)
        painter.restore()

        # 6. Particles & Popups
        for p in self.particles:
            rad = math.radians(-p['ang'])
            px, py = (rx * p['dist']) * math.cos(rad), (ry * p['dist']) * math.sin(rad)
            painter.setBrush(QBrush(QColor(0, 242, 255, p['life'])))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPoint(int(px), int(py)), 3, 3)

        painter.resetTransform()
        for img in self.pop_images:
            painter.setOpacity(img['life'] / 255)
            ix, iy = img['pos'].x(), img['pos'].y()
            painter.setBrush(QBrush(QColor(0, 26, 51)))
            painter.setPen(QPen(self.neon_blue, 1))
            painter.drawRoundedRect(ix-11, iy-11, 22, 22, 4, 4)
            painter.drawPixmap(ix-10, iy-10, self.icon_pixmap)
        painter.setOpacity(1.0)

    def resizeEvent(self, event):
        self.resize(self.parent.size())
        super().resizeEvent(event)
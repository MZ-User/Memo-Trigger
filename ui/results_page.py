import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QPushButton, 
                             QHBoxLayout, QListView, QStyledItemDelegate, 
                             QStyle, QScrollArea, QGridLayout, QMenu, QGraphicsDropShadowEffect)
from PyQt6.QtCore import (Qt, QAbstractListModel, QModelIndex, QRect, 
                          QSize, pyqtSignal, QPoint)
from PyQt6.QtGui import (QFont, QColor, QPixmap, QPainter, QPen, QAction, 
                         QGuiApplication, QPainterPath, QFontDatabase)

# Boss, aapka preferred import path:
from .Preview.img_preview import ImagePreviewOverlay

class FileModel(QAbstractListModel):
    def __init__(self, data=None):
        super().__init__()
        self._all_data = data or []
        self._display_data = []
        self.chunk_size = 150 

    def load_more(self):
        curr = len(self._display_data)
        next_batch = self._all_data[curr : curr + self.chunk_size]
        if next_batch:
            self.beginInsertRows(QModelIndex(), curr, curr + len(next_batch) - 1)
            self._display_data.extend(next_batch)
            self.endInsertRows()

    def canFetchMore(self, parent=QModelIndex()):
        return len(self._display_data) < len(self._all_data)

    def fetchMore(self, parent=QModelIndex()):
        self.load_more()

    def rowCount(self, parent=QModelIndex()): return len(self._display_data)
    
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.UserRole: return self._display_data[index.row()]
        return None

    def sort_data(self, reverse=False):
        self.layoutAboutToBeChanged.emit()
        self._all_data.sort(key=lambda x: x[1], reverse=reverse)
        self._display_data = self._all_data[:self.chunk_size]
        self.layoutChanged.emit()

class FileDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        data = index.data(Qt.ItemDataRole.UserRole)
        if not data: return
        path, ts = data
        dt = datetime.fromtimestamp(ts)
        
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        
        rect = option.rect.adjusted(10, 10, -10, -10)
        is_hover = option.state & QStyle.StateFlag.State_MouseOver
        
        # UX Improvement: Hover hone par card thoda bright aur interactive feel dega
        bg_color = QColor(0, 242, 255, 60) if is_hover else QColor(20, 20, 30, 200)
        border_color = QColor(0, 242, 255) if is_hover else QColor(255, 255, 255, 50)
        
        painter.setBrush(bg_color)
        painter.setPen(QPen(border_color, 2 if is_hover else 1))
        painter.drawRoundedRect(rect, 15, 15)

        thumb_area = QRect(rect.x()+15, rect.y()+15, rect.width()-30, 110)
        
        ext = os.path.splitext(path)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
            pix = QPixmap(path)
        else:
            file_info = QStyle.StandardPixmap.SP_FileIcon
            if ext == '.exe': file_info = QStyle.StandardPixmap.SP_ComputerIcon
            icon = self.parent().style().standardIcon(file_info)
            pix = icon.pixmap(100, 100)

        if not pix.isNull():
            scaled_pix = pix.scaled(thumb_area.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            img_rect = QRect(thumb_area.x()+(thumb_area.width()-scaled_pix.width())//2, 
                             thumb_area.y()+(thumb_area.height()-scaled_pix.height())//2, 
                             scaled_pix.width(), scaled_pix.height())
            
            path_obj = QPainterPath()
            path_obj.addRoundedRect(img_rect.toRectF(), 12, 12)
            painter.setClipPath(path_obj)
            painter.drawPixmap(img_rect, scaled_pix)
            painter.setClipping(False)

        base_y = rect.bottom()
        
        # Readability boost using Text Shadows (simulated by drawing black offset text first)
        name_rect = QRect(rect.x() + 15, base_y - 85, rect.width() - 30, 35) 
        filename = os.path.basename(path)
        
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        # Shadow for name
        painter.setPen(QColor(0, 0, 0, 200))
        painter.drawText(name_rect.translated(1, 1), Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, filename)
        # Actual name
        painter.setPen(QColor("white"))
        painter.drawText(name_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, filename)
        
        painter.setFont(QFont("Impact", 14))
        date_str = dt.strftime('%d-%m-%Y')
        # Shadow for Date
        painter.setPen(QColor(0, 0, 0, 200))
        painter.drawText(rect.x() + 1, base_y - 44, rect.width(), 25, Qt.AlignmentFlag.AlignCenter, date_str)
        # Actual Date
        painter.setPen(QColor("#FFFF00")) 
        painter.drawText(rect.x(), base_y - 45, rect.width(), 25, Qt.AlignmentFlag.AlignCenter, date_str)
        
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        time_str = dt.strftime('%I:%M %p')
        # Shadow for Time
        painter.setPen(QColor(0, 0, 0, 200))
        painter.drawText(rect.x() + 1, base_y - 19, rect.width(), 20, Qt.AlignmentFlag.AlignCenter, time_str)
        # Actual Time
        painter.setPen(QColor("white"))
        painter.drawText(rect.x(), base_y - 20, rect.width(), 20, Qt.AlignmentFlag.AlignCenter, time_str)
        
        painter.restore()

    def sizeHint(self, option, index): return QSize(200, 250)


class ResultsPage(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)
        
        # --- CUSTOM FONT LOADING LOGIC ---
        font_path = os.path.join("static", "fonts", "Gwenchana.ttf")
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            self.custom_font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        else:
            # Fallback agar OTF ho ya file na mile
            otf_path = os.path.join("static", "fonts", "Gwenchana.otf")
            font_id_otf = QFontDatabase.addApplicationFont(otf_path)
            self.custom_font_family = QFontDatabase.applicationFontFamilies(font_id_otf)[0] if font_id_otf != -1 else "Impact"

        # --- LOGO WITH DIM WHITE BLUR BOX ---
        self.logo_container = QFrame()
        self.logo_container.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 180); /* Dim White Frosted Feel */
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 50);
            }
        """)
        self.logo_container.setMinimumHeight(100)
        logo_layout = QVBoxLayout(self.logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)

        self.logo_lbl = QLabel("MEMO TRIGGER")
        self.logo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_lbl.setStyleSheet(f"""
            color: black; 
            font-family: '{self.custom_font_family}'; 
            font-size: 55px; 
            background: transparent; 
            padding: 10px;
        """)
        
        logo_layout.addWidget(self.logo_lbl)
        self.layout.addWidget(self.logo_container)

        # --- SCROLL AREA WITH CUSTOM UI/UX SCROLLBAR ---
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("""
            QScrollArea {
                background: transparent; 
                border: none;
            }
            /* Modern Neon Scrollbar */
            QScrollBar:vertical {
                border: none;
                background: rgba(0, 0, 0, 80);
                width: 12px;
                border-radius: 6px;
                margin: 0px 2px 0px 2px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 242, 255, 150); /* Cyan color */
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 242, 255, 255);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.container_lay = QVBoxLayout(self.container)
        self.container_lay.setSpacing(25)
        
        self.oldest_box = self.create_section("Oldest Files")
        self.all_box = self.create_section("All Files", is_list=True)
        self.latest_box = self.create_section("Latest Files")
        
        self.container_lay.addWidget(self.oldest_box['frame'])
        self.container_lay.addWidget(self.all_box['frame'])
        self.container_lay.addWidget(self.latest_box['frame'])
        
        self.scroll.setWidget(self.container)
        self.layout.addWidget(self.scroll)

        # Nav Buttons (BILKUL UNTOUCHED AS REQUESTED)
        nav = QHBoxLayout()
        self.btn_again = self.create_nav_btn("AGAIN")
        self.btn_home = self.create_nav_btn("HOME")
        self.btn_again.clicked.connect(lambda: self.parent.show_options())
        self.btn_home.clicked.connect(lambda: self.parent.show_dashboard())
        nav.addWidget(self.btn_again)
        nav.addWidget(self.btn_home)
        self.layout.addLayout(nav)

    def create_section(self, title, is_list=False):
        frame = QFrame()
        frame.setStyleSheet("background: rgba(10, 15, 25, 180); border-radius: 20px; border: 1px solid rgba(0, 242, 255, 40);")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(15, 15, 15, 15)
        
        header_lay = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-size: 26px; font-weight: bold; background: transparent; border: none; letter-spacing: 2px;")
        
        if is_list:
            self.btn_o = self.create_f_btn("Oldest to Latest", True)
            self.btn_n = self.create_f_btn("Latest to Oldest", False)
            header_lay.addWidget(self.btn_o)
            header_lay.addStretch()
            header_lay.addWidget(title_lbl)
            header_lay.addStretch()
            header_lay.addWidget(self.btn_n)
            lay.addLayout(header_lay)
            
            self.view = QListView()
            self.view.setViewMode(QListView.ViewMode.IconMode)
            self.view.setSpacing(15)
            
            self.view.setMinimumHeight(850) 
            self.view.setResizeMode(QListView.ResizeMode.Adjust) 
            self.view.setUniformItemSizes(True) 
            self.view.setGridSize(QSize(215, 265)) 
            
            self.view.setStyleSheet("background: transparent; border: none; outline: none;")
            
            self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.view.customContextMenuRequested.connect(self.show_list_menu)

            def check_scroll(val):
                bar = self.view.verticalScrollBar()
                if val >= bar.maximum() - 50: 
                    if self.model.canFetchMore():
                        self.model.fetchMore()
            
            self.view.verticalScrollBar().valueChanged.connect(check_scroll)

            self.model = FileModel()
            self.view.setModel(self.model)
            self.view.setItemDelegate(FileDelegate(self))
            self.view.clicked.connect(self.open_preview_all)
            
            self.btn_o.clicked.connect(lambda: self.resort(False))
            self.btn_n.clicked.connect(lambda: self.resort(True))
            
            lay.addWidget(self.view)
            return {'frame': frame, 'model': self.model, 'label': title_lbl}
        else:
            header_lay.addStretch(); header_lay.addWidget(title_lbl); header_lay.addStretch()
            lay.addLayout(header_lay)
            grid = QGridLayout()
            grid.setSpacing(15)
            lay.addLayout(grid)
            return {'frame': frame, 'grid': grid, 'label': title_lbl}
        
    def show_card_menu(self, pos, path, widget):
        self._generic_menu(widget.mapToGlobal(pos), path)

    def _generic_menu(self, pos, path):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: white; border: 1px solid #FFF; border-radius: 8px; font-weight: bold;}
            QMenu::item { color: #001A33; padding: 10px 30px; font-size: 14px;}
            QMenu::item:selected { background-color: #00F2FF; color: black; border-radius: 5px;}
        """)
        copy_action = QAction("Copy Path", self)
        copy_action.triggered.connect(lambda: QGuiApplication.clipboard().setText(path))
        menu.addAction(copy_action)
        menu.exec(pos)

    def create_static_card(self, item, index, full_list):
        card = QFrame()
        card.setFixedSize(190, 250)
        card.setStyleSheet("""
            QFrame { 
                background: rgba(20, 20, 30, 200); 
                border: 1px solid rgba(255,255,255,50); 
                border-radius: 15px; 
            } 
            QFrame:hover { 
                border: 2px solid #00F2FF; 
                background: rgba(0, 242, 255, 30);
            }
        """)
        
        v = QVBoxLayout(card)
        v.setContentsMargins(10, 10, 10, 10)
        v.setSpacing(4)
        
        img_container = QLabel()
        img_container.setFixedSize(170, 110)
        
        path_str = item[0]
        ext = os.path.splitext(path_str)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']:
            pix = QPixmap(path_str).scaled(170, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
            icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
            pix = icon.pixmap(100, 100).scaled(170, 110, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        rounded_pix = QPixmap(pix.size())
        rounded_pix.fill(Qt.GlobalColor.transparent)
        painter = QPainter(rounded_pix)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        p_path = QPainterPath()
        p_path.addRoundedRect(0, 0, pix.width(), pix.height(), 12, 12)
        painter.setClipPath(p_path)
        painter.drawPixmap(0, 0, pix)
        painter.end()
        
        img_container.setPixmap(rounded_pix)
        img_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(img_container)
        v.addStretch() 
        
        # Helper to add shadow for better readability
        def add_shadow(widget):
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0, 0, 0, 255))
            shadow.setOffset(1, 1)
            widget.setGraphicsEffect(shadow)

        name = QLabel(os.path.basename(path_str))
        name.setWordWrap(True)
        name.setContentsMargins(5, 0, 5, 0)
        name.setFixedHeight(45) 
        name.setStyleSheet("color: white; font-weight: bold; font-size: 13px; border: none; background: transparent;")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        add_shadow(name)
        
        dt = datetime.fromtimestamp(item[1])
        
        d_lbl = QLabel(dt.strftime('%d-%m-%Y'))
        d_lbl.setStyleSheet("color: #FFFF00; font-family: 'Impact'; font-size: 15px; border: none; background: transparent; letter-spacing: 1px;")
        d_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        add_shadow(d_lbl)
        
        t_lbl = QLabel(dt.strftime('%I:%M %p'))
        t_lbl.setStyleSheet("color: white; font-weight: bold; font-size: 12px; border: none; background: transparent;")
        t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        add_shadow(t_lbl)

        v.addWidget(name); v.addWidget(d_lbl); v.addWidget(t_lbl)
        
        card.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        card.customContextMenuRequested.connect(lambda pos: self.show_card_menu(pos, path_str, card))

        def card_click_logic(event):
            if event.button() == Qt.MouseButton.LeftButton:
                self.open_preview_custom(full_list, index)

        card.mousePressEvent = card_click_logic
        return card

    def open_preview_all(self, idx):
        self.overlay = ImagePreviewOverlay(self.parent, self.model._all_data, idx.row())
        self.overlay.show()

    def open_preview_custom(self, data_list, idx):
        self.overlay = ImagePreviewOverlay(self.parent, data_list, idx)
        self.overlay.show()

    def create_nav_btn(self, t):
        btn = QPushButton(t)
        btn.setFixedSize(220, 55)
        btn.setStyleSheet("""
            QPushButton { 
                background-color: #00F2FF; 
                color: #001A33; 
                border: 3px solid #001A33;
                border-radius: 27px; 
                font-weight: bold; 
                font-size: 20px;
            }
            QPushButton:hover { 
                background-color: #001A33; 
                color: #00F2FF; 
                border: 3px solid #00F2FF; 
            }
            QPushButton:pressed { 
                background-color: #00F2FF; 
                color: #001A33; 
                border: 5px solid #001A33;
                padding-top: 5px;  
                padding-left: 5px;
            }
        """)
        return btn

    def create_f_btn(self, t, active):
        btn = QPushButton(t)
        btn.setFixedSize(150, 35)
        self.style_f(btn, active)
        return btn

    def style_f(self, btn, active):
        if active:
            btn.setStyleSheet("background: #00F2FF; color: #001A33; border: 2px solid white; border-radius: 10px; font-weight: bold;")
        else:
            btn.setStyleSheet("background: rgba(255,255,255,10); color: white; border: 1px solid rgba(255,255,255,50); border-radius: 10px;")
            
        # Add quick hover effect to filter buttons
        btn.setProperty("active", active)

    def resort(self, rev):
        self.style_f(self.btn_o, not rev)
        self.style_f(self.btn_n, rev)
        self.model.sort_data(rev)

    def load_data(self):
        db_path = "DB.json"
        if os.path.exists(db_path):
            with open(db_path, 'r') as f:
                paths = json.load(f).get("images", [])
            
            data = [(p, os.path.getctime(p)) for p in paths if os.path.exists(p)]
            data.sort(key=lambda x: x[1])
            
            self.all_box['label'].setText(f"All Files ({len(data)})")
            
            self.model._all_data = data
            self.model.load_more()
            
            # Clear old widgets in grid before re-loading to prevent overlap
            for i in reversed(range(self.oldest_box['grid'].count())): 
                self.oldest_box['grid'].itemAt(i).widget().setParent(None)
            for i in reversed(range(self.latest_box['grid'].count())): 
                self.latest_box['grid'].itemAt(i).widget().setParent(None)

            for i in range(min(4, len(data))):
                self.oldest_box['grid'].addWidget(self.create_static_card(data[i], i, data), 0, i)
            
            latest_list = sorted(data, key=lambda x: x[1], reverse=True)
            for i in range(min(4, len(latest_list))):
                self.latest_box['grid'].addWidget(self.create_static_card(latest_list[i], i, latest_list), 0, i)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_data()
    
    def show_list_menu(self, pos):
        idx = self.view.indexAt(pos)
        if idx.isValid():
            data = idx.data(Qt.ItemDataRole.UserRole)
            if data:
                self._generic_menu(self.view.mapToGlobal(pos), data[0])
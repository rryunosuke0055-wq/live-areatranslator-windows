from PySide6.QtCore import Qt, QRect, QPoint, Signal, QSize
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtGui import QColor, QMouseEvent, QCursor

# ウィンドウ端からこのピクセル数以内にマウスがある場合、リサイズモードに入る
EDGE_MARGIN = 12

class TranslationOverlay(QWidget):
    on_close_requested = Signal()

    def __init__(self, target_rect: QRect):
        super().__init__()
        self.target_rect = target_rect
        self.drag_start_position = QPoint()
        self._resizing = False
        self._dragging = False
        self._resize_edges = set()
        self._resize_start_pos = QPoint()
        self._resize_start_geom = QRect()
        
        self._font_size = 16
        self._theme = "dark"
        
        self.init_ui()

    def init_ui(self):
        # FramelessWindowHint + WindowStaysOnTopHint のみ
        # → カーソル変更が正常に動作し、他アプリをクリックしてもウィンドウは消えない
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # フォーカスポリシーをNoFocusにして、キーボード入力を奪わない
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        # マウストラッキング：ボタン押下なしでもmouseMoveEventを発生させる
        self.setMouseTracking(True)
        self.setMinimumSize(120, 60)

        layout = QVBoxLayout()
        layout.setContentsMargins(EDGE_MARGIN, EDGE_MARGIN, EDGE_MARGIN, EDGE_MARGIN)
        
        # --- 閉じる（×）ボタン ---
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.btn_close = QPushButton("✖")
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.btn_close.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 0, 0, 150);
                color: white;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: rgba(255, 0, 0, 180); }
        """)
        self.btn_close.clicked.connect(self.on_close_requested.emit)
        header_layout.addWidget(self.btn_close)
        
        layout.addLayout(header_layout)
        layout.setSpacing(0)
        
        self.text_label = QLabel("Waiting for translation...")
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.text_label.setMouseTracking(True)
        self._apply_text_style()
        layout.addWidget(self.text_label)
        self.setLayout(layout)

        self.setGeometry(
            self.target_rect.x(),
            self.target_rect.bottom() + 10,
            self.target_rect.width(),
            150
        )
    
    def apply_settings(self, font_size: int, theme: str):
        self._font_size = font_size
        self._theme = theme
        self._apply_text_style()

    def _apply_text_style(self):
        if self._theme == "dark":
            bg = "rgba(0, 0, 0, 180)"
            fg = "white"
        else:
            bg = "rgba(255, 255, 255, 220)"
            fg = "#222222"
        
        self.text_label.setStyleSheet(
            f"QLabel {{"
            f"  color: {fg};"
            f"  background-color: {bg};"
            f"  padding: 10px;"
            f"  border-radius: 5px;"
            f"  font-size: {self._font_size}px;"
            f"}}"
        )
        
    def update_text(self, new_text: str):
        self.text_label.setText(new_text)

    # ====== リサイズ判定ヘルパー ======
    def _get_resize_edges(self, pos: QPoint) -> set:
        edges = set()
        rect = self.rect()
        if pos.x() <= EDGE_MARGIN:
            edges.add('left')
        if pos.x() >= rect.width() - EDGE_MARGIN:
            edges.add('right')
        if pos.y() <= EDGE_MARGIN:
            edges.add('top')
        if pos.y() >= rect.height() - EDGE_MARGIN:
            edges.add('bottom')
        return edges

    def _get_cursor_for_edges(self, edges: set) -> Qt.CursorShape:
        if edges == {'left'} or edges == {'right'}:
            return Qt.CursorShape.SizeHorCursor
        if edges == {'top'} or edges == {'bottom'}:
            return Qt.CursorShape.SizeVerCursor
        if edges == {'left', 'top'} or edges == {'right', 'bottom'}:
            return Qt.CursorShape.SizeFDiagCursor
        if edges == {'right', 'top'} or edges == {'left', 'bottom'}:
            return Qt.CursorShape.SizeBDiagCursor
        return Qt.CursorShape.OpenHandCursor

    def _update_cursor_for_pos(self, pos: QPoint):
        """マウス位置に応じてカーソル形状を更新する"""
        edges = self._get_resize_edges(pos)
        if edges:
            self.setCursor(self._get_cursor_for_edges(edges))
        else:
            self.setCursor(Qt.CursorShape.OpenHandCursor)

    # ====== マウスイベント ======
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            edges = self._get_resize_edges(pos)
            
            if edges:
                self._resizing = True
                self._dragging = False
                self._resize_edges = edges
                self._resize_start_pos = event.globalPosition().toPoint()
                self._resize_start_geom = self.geometry()
                self.setCursor(self._get_cursor_for_edges(edges))
            else:
                self._resizing = False
                self._dragging = True
                self.drag_start_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.position().toPoint()
        
        if event.buttons() == Qt.MouseButton.LeftButton:
            global_pos = event.globalPosition().toPoint()
            if self._resizing:
                delta = global_pos - self._resize_start_pos
                geom = QRect(self._resize_start_geom)
                min_w = self.minimumWidth()
                min_h = self.minimumHeight()

                if 'left' in self._resize_edges:
                    new_left = geom.left() + delta.x()
                    if geom.right() - new_left + 1 >= min_w:
                        geom.setLeft(new_left)
                if 'right' in self._resize_edges:
                    new_right = geom.right() + delta.x()
                    if new_right - geom.left() + 1 >= min_w:
                        geom.setRight(new_right)
                if 'top' in self._resize_edges:
                    new_top = geom.top() + delta.y()
                    if geom.bottom() - new_top + 1 >= min_h:
                        geom.setTop(new_top)
                if 'bottom' in self._resize_edges:
                    new_bottom = geom.bottom() + delta.y()
                    if new_bottom - geom.top() + 1 >= min_h:
                        geom.setBottom(new_bottom)

                self.setGeometry(geom)
            elif self._dragging:
                self.move(global_pos - self.drag_start_position)
            event.accept()
        else:
            # ホバー時：カーソル形状を更新
            self._update_cursor_for_pos(pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._resizing = False
            self._dragging = False
            self._resize_edges = set()
            self._update_cursor_for_pos(event.position().toPoint())
            event.accept()

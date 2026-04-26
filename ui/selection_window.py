import sys
from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen, QGuiApplication
from PySide6.QtWidgets import QWidget


def _get_physical_cursor_pos():
    """
    Windows API (GetCursorPos) を直接呼び出して、物理ピクセル単位の
    カーソル座標を取得する。Qt の座標変換を一切経由しないため、
    DPIスケーリングやマルチモニターの影響を完全に受けない。
    mss が使う座標系と 100% 同一の値が返る。
    """
    if sys.platform == "win32":
        import ctypes

        class POINT(ctypes.Structure):
            _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

        pt = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        return QPoint(pt.x, pt.y)
    else:
        from PySide6.QtGui import QCursor
        return QCursor.pos()


class SelectionWindow(QWidget):
    def __init__(self, on_selected):
        super().__init__()
        self.on_selected = on_selected

        # ---- 描画用 (ウィジェットローカル座標) ----
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False

        # ---- キャプチャ用 (物理ピクセル、mss互換座標) ----
        self._phys_start = QPoint()
        self._phys_end = QPoint()

        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)

    # ------------------------------------------------------------------ #
    #  描画
    # ------------------------------------------------------------------ #
    def paintEvent(self, event):
        painter = QPainter(self)
        # 半透明の暗い背景
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))

        if self.is_drawing and not self.start_point.isNull() and not self.end_point.isNull():
            selection_rect = QRect(self.start_point, self.end_point).normalized()

            # 選択領域を「くり抜き」にする
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(selection_rect, Qt.GlobalColor.transparent)

            # 緑の枠線を描画
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 255, 0), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(selection_rect)

    # ------------------------------------------------------------------ #
    #  マウスイベント
    # ------------------------------------------------------------------ #
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 描画用: ウィジェットローカル座標
            self.start_point = event.pos()
            self.end_point = self.start_point
            # キャプチャ用: Windows API から物理ピクセル座標を直接取得
            self._phys_start = _get_physical_cursor_pos()
            self.is_drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            # 描画用のみ更新 (物理座標は最終確定時に取得)
            self.end_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_point = event.pos()
            # キャプチャ用: Windows API から物理ピクセル座標を直接取得
            self._phys_end = _get_physical_cursor_pos()
            self.is_drawing = False
            self.update()

            local_rect = QRect(self.start_point, self.end_point).normalized()
            if local_rect.width() > 10 and local_rect.height() > 10:
                # mss に渡す座標は物理ピクセル座標から直接構築する
                capture_rect = QRect(self._phys_start, self._phys_end).normalized()
                self.on_selected(capture_rect)
            else:
                self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

from PySide6.QtCore import Qt, QRect, QPoint
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QGuiApplication

class SelectionWindow(QWidget):
    def __init__(self, on_selected):
        super().__init__()
        self.on_selected = on_selected
        
        # 枠線描画用の変数
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.is_drawing = False

        self.init_ui()

    def init_ui(self):
        # フルスクリーンで最前面、枠なし、タスクバー非表示
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        # 背景を透明に
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 複数モニター対応のため全スクリーンの合計ジオメトリを取得
        screens = QGuiApplication.screens()
        rect = QRect()
        for screen in screens:
            rect = rect.united(screen.geometry())
        self.setGeometry(rect)
        
        # カーソルを十字に変更
        self.setCursor(Qt.CursorShape.CrossCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 画面全体を半透明の暗い色で塗りつぶす
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))

        if self.is_drawing and not self.start_point.isNull() and not self.end_point.isNull():
            # 選択中の領域を切り抜く（透明にする）ための描画
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            
            # その領域のハイライト（暗い背景を消す）
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(selection_rect, Qt.GlobalColor.transparent)
            
            # 元のモードに戻して枠線を描画
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            pen = QPen(QColor(0, 255, 0), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawRect(selection_rect)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.globalPos()
            self.end_point = self.start_point
            self.is_drawing = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_drawing:
            self.end_point = event.globalPos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_drawing:
            self.end_point = event.globalPos()
            self.is_drawing = False
            self.update()
            
            selection_rect = QRect(self.start_point, self.end_point).normalized()
            # 一定サイズ以上の領域が選択された場合のみコールバックを呼ぶ
            if selection_rect.width() > 10 and selection_rect.height() > 10:
                self.on_selected(selection_rect)
            else:
                # キャンセル処理：閉じる
                self.close()

    def keyPressEvent(self, event):
        # ESCキーでキャンセル
        if event.key() == Qt.Key.Key_Escape:
            self.close()

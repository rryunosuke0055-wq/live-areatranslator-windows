from PySide6.QtCore import Qt, QRect, QObject, Signal
from PySide6.QtWidgets import QWidget
from ui.selection_window import SelectionWindow
from ui.translation_overlay import TranslationOverlay
from worker.capture_worker import CaptureWorker

class OverlayManager(QObject):
    # 翻訳が終了・キャンセルされたことを通知するシグナル
    on_translation_stopped = Signal()

    def __init__(self):
        super().__init__()
        self.selection_window = None
        self.translation_overlay = None
        
        # 設定値（HomeWindowから渡される）
        self._font_size = 16
        self._theme = "dark"
        
        # ワーカースレッドの初期化
        self.worker = CaptureWorker()
        self.worker.translation_ready.connect(self.on_translation_ready)

    def start_selection_mode(self):
        """画面上の領域を選択するモードを開始する"""
        if not self.selection_window:
            self.selection_window = SelectionWindow(on_selected=self.on_area_selected)
        self.selection_window.show()
        # 既存のオーバーレイを隠してワーカーを止める
        if self.translation_overlay:
            self.translation_overlay.hide()
        if self.worker.isRunning():
            self.worker.stop()

    def on_area_selected(self, rect: QRect):
        """領域が選択された後に呼ばれるコールバック"""
        print(f"Area selected: {rect.x()}, {rect.y()}, {rect.width()}x{rect.height()}")
        self.selection_window.close()
        
        # オーバーレイ用のウィンドウを作成して表示
        self.show_translation_overlay(rect)
        
        # バックグラウンド処理の開始
        self.worker.set_rect(rect)
        self.worker.start()

    def show_translation_overlay(self, rect: QRect):
        """選択された領域をもとに、翻訳結果を表示する透明オーバーレイを作成"""
        if not self.translation_overlay:
            self.translation_overlay = TranslationOverlay(rect)
            # 閉じるボタンが押された際の処理を登録
            self.translation_overlay.on_close_requested.connect(self.stop_and_close)
        else:
            # 使い回す場合は位置を更新
            self.translation_overlay.target_rect = rect
            self.translation_overlay.setGeometry(
                rect.x(), rect.bottom() + 10, rect.width(), 150
            )
        self.translation_overlay.show()
        self.translation_overlay.apply_settings(self._font_size, self._theme)
        self.translation_overlay.update_text("Waiting for translation... (Updates on screen changes)")

    def on_translation_ready(self, translated_text: str):
        """バックグラウンドワーカーから翻訳完了のシグナルを受け取った際の処理"""
        if self.translation_overlay:
            self.translation_overlay.update_text(translated_text)

    def stop_and_close(self):
        """ユーザーが×ボタンを押した際にキャプチャループを停止しウィンドウを隠す"""
        if self.worker.isRunning():
            self.worker.stop()
        if self.translation_overlay:
            self.translation_overlay.hide()
        # ホーム画面を復帰させるためのシグナルを発行
        self.on_translation_stopped.emit()

    def cleanup(self):
        """アプリ終了時のクリーンアップ処理"""
        if self.worker.isRunning():
            self.worker.stop()

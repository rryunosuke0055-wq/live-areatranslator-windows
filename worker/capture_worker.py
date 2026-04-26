import time
from PySide6.QtCore import QThread, Signal, QRect
from capture.screen_capture import ScreenCapture
from ocr.text_extractor import TextExtractor, TranslatorAPI

class CaptureWorker(QThread):
    # テキストが見つかり、翻訳されたら発行されるシグナル
    translation_ready = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.rect = None
        self.running = False
        self.capture = ScreenCapture()
        self.extractor = TextExtractor()
        self.translator = TranslatorAPI()
        
        self.last_img = None
        self.last_text = ""
        
        self.diff_threshold = 2.0  # 画像の変化判定の閾値
        self.fps = 2               # 1秒間にキャプチャする回数
        self.interval = 1.0 / self.fps

    def set_fps(self, fps: int):
        """キャプチャ速度（FPS）を動的に変更する。実行中でも即座に反映される。"""
        self.fps = max(1, min(fps, 30))  # 1〜30の範囲に制限
        self.interval = 1.0 / self.fps

    def set_rect(self, rect: QRect):
        self.rect = rect
        self.last_img = None
        self.last_text = ""

    def run(self):
        self.running = True
        while self.running:
            try:
                if self.rect and self.rect.width() > 0 and self.rect.height() > 0:
                    current_img = self.capture.capture_rect(self.rect)
                    
                    # 画像の差分をチェック
                    diff = self.capture.calculate_difference(self.last_img, current_img)
                    
                    # 差分が閾値以上の場合のみOCRを実行
                    if diff > self.diff_threshold:
                        text = self.extractor.extract_text(current_img)
                        
                        # テキストが存在し、前回と違う場合のみ翻訳
                        if text and text != self.last_text:
                            translated_text = self.translator.translate(text)
                            # シグナルでUIスレッドへ通知
                            self.translation_ready.emit(translated_text)
                            
                            self.last_text = text
                            
                        self.last_img = current_img
                
                # FPSに基づくウェイト
                time.sleep(self.interval)
            except Exception as e:
                import traceback
                print(f"Worker Error: {e}")
                traceback.print_exc()
                time.sleep(self.interval)  # エラー時も連続ループを避けるため少し待つ

    def stop(self):
        self.running = False
        self.wait()
        self.capture.close()

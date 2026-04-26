import cv2
import numpy as np
from winocr import recognize_cv2_sync
from deep_translator import GoogleTranslator

class TextExtractor:
    def __init__(self):
        # Windows ネイティブOCR (Windows.Media.Ocr) を使用
        # winocr パッケージ経由で呼び出す
        print("[OCR] Using Windows.Media.Ocr via winocr")

    def extract_text(self, image_bgr: np.ndarray) -> str:
        """
        OpenCVの画像(BGR)を受け取り、Windows内蔵のOCRエンジンでテキストを抽出する。
        Tesseract等の外部ソフトのインストールは不要。
        """
        try:
            # 英語で認識を試みる（自動言語検出はWindowsOCRでは非対応のため）
            result = recognize_cv2_sync(image_bgr, lang="en")
            text = result.get("text", "")
            
            # 英語で結果が空の場合、日本語で再試行
            if not text.strip():
                result = recognize_cv2_sync(image_bgr, lang="ja")
                text = result.get("text", "")
            
            return text.strip()
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

class TranslatorAPI:
    def __init__(self):
        # 無料で使える Google Translator (deep-translator) を使用
        self.translator = GoogleTranslator(source='auto', target='ja')
        
    def translate(self, text: str) -> str:
        """
        APIを用いて、与えられたテキストを日本語に翻訳する。
        """
        if not text:
            return ""
            
        print(f"Original Text:\n{text}")
        try:
            translated = self.translator.translate(text)
            return translated
        except Exception as e:
            print(f"Translation Error: {e}")
            return f"[Translation Error] {e}"

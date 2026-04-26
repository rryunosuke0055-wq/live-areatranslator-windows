import cv2
import numpy as np
from winocr import recognize_cv2_sync
from deep_translator import GoogleTranslator


class TextExtractor:
    def __init__(self):
        # Windows ネイティブOCR (Windows.Media.Ocr) を使用
        print("[OCR] Using Windows.Media.Ocr via winocr")

    def extract_text(self, image_bgr: np.ndarray) -> str:
        """
        OpenCVの画像(BGR)を受け取り、Windows内蔵のOCRエンジンでテキストを抽出する。
        英語と日本語を同時に認識させることで、2回呼び出す無駄を省く。
        """
        try:
            # まず英語で認識（英語テキストが圧倒的に多いため）
            result = recognize_cv2_sync(image_bgr, lang="en")
            text = result.get("text", "").strip()

            # 英語で結果が得られなかった場合のみ日本語でフォールバック
            if not text:
                result = recognize_cv2_sync(image_bgr, lang="ja")
                text = result.get("text", "").strip()

            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""


class TranslatorAPI:
    def __init__(self):
        # 無料で使える Google Translator (deep-translator) を使用
        self._source = 'auto'
        self._target = 'ja'

    def translate(self, text: str) -> str:
        """
        APIを用いて、与えられたテキストを日本語に翻訳する。
        """
        if not text:
            return ""

        try:
            translator = GoogleTranslator(source=self._source, target=self._target)
            translated = translator.translate(text)
            return translated
        except Exception as e:
            print(f"Translation Error: {e}")
            return f"[Translation Error] {e}"

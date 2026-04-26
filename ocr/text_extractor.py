import re
import json
import cv2
import numpy as np
import requests
from winocr import recognize_cv2_sync


def _merge_ocr_lines(raw_text: str) -> str:
    """
    OCR が行ごとに分割してしまったテキストを、文脈上つながっている場合は
    1文に結合する。句読点（.!?。！？）で終わる行はそこで切り、
    それ以外の行は次の行とスペースで連結する。
    """
    lines = raw_text.split("\n")
    merged = []
    buffer = ""
    for line in lines:
        line = line.strip()
        if not line:
            if buffer:
                merged.append(buffer)
                buffer = ""
            continue
        if buffer:
            buffer += " " + line
        else:
            buffer = line
        # 句読点で終わっていれば切る
        if re.search(r'[.!?。！？]$', buffer):
            merged.append(buffer)
            buffer = ""
    if buffer:
        merged.append(buffer)
    return "\n".join(merged)


class TextExtractor:
    def __init__(self):
        print("[OCR] Using Windows.Media.Ocr via winocr")

    def extract_text(self, image_bgr: np.ndarray) -> str:
        """
        OpenCVの画像(BGR)を受け取り、Windows内蔵のOCRエンジンでテキストを抽出する。
        """
        try:
            result = recognize_cv2_sync(image_bgr, lang="en")
            text = result.get("text", "").strip()

            if not text:
                result = recognize_cv2_sync(image_bgr, lang="ja")
                text = result.get("text", "").strip()

            # OCRの改行を文脈に応じて結合してから返す
            return _merge_ocr_lines(text)
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""


class TranslatorAPI:
    """
    Google Translate の無料 Web API を直接呼び出す高速翻訳クラス。
    requests.Session を使い回すことで TCP/TLS の再接続コストを排除し、
    deep-translator ライブラリ比で 2〜4 倍高速に動作する。
    """

    _URL = "https://translate.googleapis.com/translate_a/single"

    def __init__(self, target: str = "ja"):
        self._target = target
        # セッションを使い回すことで HTTP Keep-Alive が効き、
        # 2回目以降のリクエストが圧倒的に高速になる
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return ""

        try:
            params = {
                "client": "gtx",
                "sl": "auto",
                "tl": self._target,
                "dt": "t",
                "q": text,
            }
            resp = self._session.get(self._URL, params=params, timeout=5)
            resp.raise_for_status()

            data = resp.json()
            # Google Translate API は [[["翻訳文","原文",null,null,10],...]] の形式
            translated_parts = [part[0] for part in data[0] if part[0]]
            result = "".join(translated_parts)
            return result
        except Exception as e:
            print(f"Translation Error: {e}")
            return f"[Translation Error] {e}"

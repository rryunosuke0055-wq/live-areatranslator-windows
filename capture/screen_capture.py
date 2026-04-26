import mss
import mss.tools
import numpy as np
import cv2
from PySide6.QtCore import QRect

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()

    def capture_rect(self, rect: QRect) -> np.ndarray:
        """
        指定されたQRectの領域をキャプチャし、OpenCV形式のNumPy配列（BGR）を返す
        """
        # mss用のキャプチャ領域形式に変換
        monitor = {
            "top": rect.y(),
            "left": rect.x(),
            "width": rect.width(),
            "height": rect.height()
        }
        
        # 画面をキャプチャ
        sct_img = self.sct.grab(monitor)
        
        # NumPy配列に変換し、BGRAからBGRに変換して返す
        img_np = np.array(sct_img)
        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_BGRA2BGR)
        
        return img_bgr

    def calculate_difference(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        2つの画像の差分（変化量）を計算する。
        ここでは簡単なピクセル差分の平均を計算している。
        """
        if img1 is None or img2 is None:
            return 100.0 # 強制的に更新
            
        if img1.shape != img2.shape:
            return 100.0
            
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        diff = cv2.absdiff(gray1, gray2)
        score = np.mean(diff)
        return float(score)

    def close(self):
        self.sct.close()

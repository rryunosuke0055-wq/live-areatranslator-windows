import sys
import os

# Windows特有のDPIスケーリングによる座標ズレ（マウスと描画枠の位置がずれるバグ）を完全に防ぐため、
# OSレベルでプロセスのDPIスケーリングを無効化（Per-Monitor V2）する
if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        pass

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

from PySide6.QtWidgets import QApplication
from ui.overlay_manager import OverlayManager
from ui.home_window import HomeWindow

def main():
    app = QApplication(sys.argv)
    
    # オーバーレイ管理クラスとホーム画面の初期化
    manager = OverlayManager()
    home_window = HomeWindow(manager)
    
    # アプリケーション終了時にワーカーを停止させる
    app.aboutToQuit.connect(manager.cleanup)
    
    # ホーム画面を表示
    home_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

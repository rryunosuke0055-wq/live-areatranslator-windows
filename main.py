import sys
import os

# マルチ・モニターやディスプレイ スケーリング (125%, 150% 等) 環境における、
# Windows特有の座標ズレや枠外への表示バグを完全に修正するため、HighDPIスケーリングを無効化する。
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

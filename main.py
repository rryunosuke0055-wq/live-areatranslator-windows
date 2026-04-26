import sys
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

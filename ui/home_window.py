import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QComboBox, QApplication, QLabel
)
from PySide6.QtGui import QFont, QIcon

from ui.settings_modal import SettingsModal

class HomeWindow(QMainWindow):
    def __init__(self, overlay_manager):
        super().__init__()
        self.overlay_manager = overlay_manager
        # 翻訳オーバーレイが×ボタンで閉じられたらホーム画面を元のサイズで復帰させる
        self.overlay_manager.on_translation_stopped.connect(self.showNormal)
        
        # 設定値を保持（アプリ起動中は維持される）
        self._font_size = 16
        self._theme = "dark"
        self._fps = 2
        
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Live AreaTranslator")
        self.setMinimumSize(400, 200)
        
        # クリーンな白基調のグローバルデザイン (QSS)
        self.setStyleSheet("""
            QMainWindow { background-color: #FFFFFF; }
            QWidget { font-family: "Helvetica Neue", Helvetica, Arial, sans-serif; color: #333333; }
            QPushButton {
                background-color: #F0F0F0;
                border: 1px solid #DDDDDD;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #E2E2E2; }
            QComboBox {
                border: 1px solid #DDDDDD;
                border-radius: 8px;
                padding: 6px 10px;
                background-color: white;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 1. ヘッダー領域
        header_layout = QHBoxLayout()
        self.btn_close = QPushButton("✖ Close")
        self.btn_close.clicked.connect(self.close)
        
        self.btn_settings = QPushButton("⚙ Settings")
        self.btn_settings.clicked.connect(self.open_settings)
        
        header_layout.addWidget(self.btn_close)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_settings)
        main_layout.addLayout(header_layout)

        # 2. 言語選択パネル
        lang_layout = QHBoxLayout()
        
        major_languages = [
            "Japanese (ja)", "English (en)", "Korean (ko)", 
            "Chinese (zh-CN)", "Spanish (es)", "French (fr)", 
            "German (de)", "Italian (it)", "Portuguese (pt)", "Russian (ru)"
        ]
        
        self.combo_source = QComboBox()
        self.combo_source.addItems(["Auto Detect (auto)"] + major_languages)
        
        self.lbl_arrow = QLabel("➔")
        self.lbl_arrow.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_arrow.setFixedWidth(40)
        self.lbl_arrow.setStyleSheet("font-size: 24px; color: #666666;")
        
        self.combo_target = QComboBox()
        self.combo_target.addItems(major_languages)
        
        lang_layout.addWidget(self.combo_source, stretch=1)
        lang_layout.addWidget(self.lbl_arrow)
        lang_layout.addWidget(self.combo_target, stretch=1)
        main_layout.addLayout(lang_layout)

        # 3. 画面キャプチャ起動ボタン
        self.btn_camera = QPushButton("📷 Drag to Select Area & Start Live Translation")
        self.btn_camera.setStyleSheet("background-color: #E8F0FE; color: #1967D2; font-weight: bold; border-color: #1967D2; font-size: 16px; padding: 15px;")
        self.btn_camera.clicked.connect(self.start_live_translation)
        
        main_layout.addWidget(self.btn_camera)
        main_layout.addStretch()

    def extract_lang_code(self, text):
        """ コンボボックスのテキスト('英語 (en)')等からコード('en')を抽出 """
        if "Auto" in text: return "auto"
        start = text.find('(')
        end = text.find(')')
        if start != -1 and end != -1:
            return text[start+1:end]
        return "ja"

    def start_live_translation(self):
        # 選択された言語を抽出してワーカーに適用する
        source_lang = self.extract_lang_code(self.combo_source.currentText())
        target_lang = self.extract_lang_code(self.combo_target.currentText())
        
        # ワーカースレッドの言語設定を更新
        self.overlay_manager.worker.translator.translator.source = source_lang
        self.overlay_manager.worker.translator.translator.target = target_lang

        # ホーム画面は一時的に最小化してキャプチャUIを呼び出す
        self.showMinimized()
        self.overlay_manager.start_selection_mode()

    def open_settings(self):
        """設定ダイアログを開く。現在の設定値を渡し、変更後に反映する。"""
        modal = SettingsModal(
            current_font_size=self._font_size,
            current_theme=self._theme,
            current_fps=self._fps,
            parent=self
        )
        modal.settings_changed.connect(self._on_settings_changed)
        modal.exec()

    def _on_settings_changed(self, font_size: int, theme: str, fps: int):
        """設定変更時のコールバック。値を保持し、既存のオーバーレイがあればリアルタイムに反映する。"""
        self._font_size = font_size
        self._theme = theme
        self._fps = fps
        
        # マネージャーにも設定値を同期（新規オーバーレイ作成時に反映される）
        self.overlay_manager._font_size = font_size
        self.overlay_manager._theme = theme
        
        # ワーカーのキャプチャ速度を即座に更新
        self.overlay_manager.worker.set_fps(fps)
        
        # 既にオーバーレイが存在する場合は即座に反映
        overlay = self.overlay_manager.translation_overlay
        if overlay:
            overlay.apply_settings(font_size, theme)

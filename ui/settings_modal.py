from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QSpinBox, QPushButton, QGroupBox, QSlider
)

class SettingsModal(QDialog):
    """設定ダイアログ。文字サイズ・テーマ・キャプチャ速度を変更できる。"""

    # 設定が変更されたことを通知するシグナル (font_size: int, theme: str, capture_fps: int)
    settings_changed = Signal(int, str, int)

    def __init__(self, current_font_size: int = 16, current_theme: str = "dark", 
                 current_fps: int = 2, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 400)
        
        self._font_size = current_font_size
        self._theme = current_theme
        self._fps = current_fps

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # ====== 文字サイズの変更セクション ======
        font_group = QGroupBox("Font Size")
        font_layout = QVBoxLayout()

        # SpinBox で 1pt 単位の細かい調整を可能にする
        size_row = QHBoxLayout()
        size_row.addWidget(QLabel("Size (px):"))
        
        self.spin_font_size = QSpinBox()
        self.spin_font_size.setRange(8, 72)        # 8px〜72pxの範囲
        self.spin_font_size.setSingleStep(1)        # 1px刻み
        self.spin_font_size.setValue(self._font_size)
        self.spin_font_size.setSuffix(" px")
        self.spin_font_size.setStyleSheet("""
            QSpinBox {
                padding: 5px 10px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
        size_row.addWidget(self.spin_font_size, stretch=1)
        font_layout.addLayout(size_row)

        # プレビュー表示
        self.lbl_preview = QLabel("Translation Preview Text")
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setWordWrap(True)
        self.lbl_preview.setMinimumHeight(60)
        font_layout.addWidget(self.lbl_preview)
        
        self.spin_font_size.valueChanged.connect(self._update_preview)
        font_group.setLayout(font_layout)
        layout.addWidget(font_group)

        # ====== テーマ設定セクション ======
        theme_group = QGroupBox("Theme")
        theme_layout = QHBoxLayout()

        self.btn_light = QPushButton("☀ Light Mode")
        self.btn_dark = QPushButton("🌙 Dark Mode")

        self.btn_light.setCheckable(True)
        self.btn_dark.setCheckable(True)

        self.btn_light.clicked.connect(lambda: self._set_theme("light"))
        self.btn_dark.clicked.connect(lambda: self._set_theme("dark"))
        
        theme_layout.addWidget(self.btn_light)
        theme_layout.addWidget(self.btn_dark)
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # ====== キャプチャ速度セクション ======
        speed_group = QGroupBox("Capture Speed")
        speed_layout = QVBoxLayout()

        # 説明ラベル
        desc_label = QLabel("Higher = faster response, more CPU usage\n(Translation speed also depends on OCR & API response time)")
        desc_label.setStyleSheet("color: #888; font-size: 11px;")
        desc_label.setWordWrap(True)
        speed_layout.addWidget(desc_label)

        # スライダー + 数値表示の行
        slider_row = QHBoxLayout()
        
        lbl_slow = QLabel("🐢 Slow")
        lbl_slow.setStyleSheet("font-size: 12px; color: #666;")
        slider_row.addWidget(lbl_slow)
        
        self.slider_fps = QSlider(Qt.Orientation.Horizontal)
        self.slider_fps.setRange(1, 30)         # 1 FPS 〜 30 FPS
        self.slider_fps.setSingleStep(1)
        self.slider_fps.setTickInterval(5)
        self.slider_fps.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider_fps.setValue(self._fps)
        self.slider_fps.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #ddd;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #1967D2;
                width: 16px;
                height: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #1967D2;
                border-radius: 3px;
            }
        """)
        slider_row.addWidget(self.slider_fps, stretch=1)
        
        lbl_fast = QLabel("🐇 Fast")
        lbl_fast.setStyleSheet("font-size: 12px; color: #666;")
        slider_row.addWidget(lbl_fast)
        
        speed_layout.addLayout(slider_row)

        # 現在値とインターバル表示
        self.lbl_fps_value = QLabel()
        self.lbl_fps_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_fps_value.setStyleSheet("font-size: 13px; font-weight: bold; color: #1967D2;")
        speed_layout.addWidget(self.lbl_fps_value)
        
        self.slider_fps.valueChanged.connect(self._update_fps_label)
        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)

        # ====== 閉じるボタン ======
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        btn_apply = QPushButton("Apply & Close")
        btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #1967D2;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #1558b0; }
        """)
        btn_apply.clicked.connect(self._apply_and_close)
        btn_row.addWidget(btn_apply)
        layout.addLayout(btn_row)

        # 初期表示を反映
        self._set_theme(self._theme)
        self._update_preview()
        self._update_fps_label()

    def _set_theme(self, theme: str):
        """テーマを切り替える"""
        self._theme = theme
        self.btn_light.setChecked(theme == "light")
        self.btn_dark.setChecked(theme == "dark")

        # 選択中のボタンを強調表示
        active_style = """
            QPushButton {
                background-color: #1967D2; color: white;
                font-weight: bold; padding: 8px 15px;
                border-radius: 6px; font-size: 13px;
            }
        """
        inactive_style = """
            QPushButton {
                background-color: #F0F0F0; color: #333;
                padding: 8px 15px; border-radius: 6px;
                font-size: 13px; border: 1px solid #ddd;
            }
            QPushButton:hover { background-color: #E2E2E2; }
        """
        self.btn_light.setStyleSheet(active_style if theme == "light" else inactive_style)
        self.btn_dark.setStyleSheet(active_style if theme == "dark" else inactive_style)

        self._update_preview()

    def _update_preview(self):
        """プレビューラベルのスタイルを現在の設定に合わせて更新する"""
        size = self.spin_font_size.value()
        if self._theme == "dark":
            bg = "rgba(0, 0, 0, 180)"
            fg = "white"
        else:
            bg = "rgba(255, 255, 255, 220)"
            fg = "#222222"
        
        self.lbl_preview.setStyleSheet(
            f"background-color: {bg}; color: {fg}; "
            f"margin: 5px; padding: 10px; border-radius: 5px; "
            f"font-size: {size}px;"
        )

    def _update_fps_label(self):
        """FPSスライダーの値表示を更新する"""
        fps = self.slider_fps.value()
        interval_ms = int(1000 / fps)
        self.lbl_fps_value.setText(f"{fps} FPS  (every {interval_ms} ms)")

    def _apply_and_close(self):
        """設定を適用してダイアログを閉じる"""
        self._font_size = self.spin_font_size.value()
        self._fps = self.slider_fps.value()
        self.settings_changed.emit(self._font_size, self._theme, self._fps)
        self.accept()

    def get_font_size(self) -> int:
        return self._font_size

    def get_theme(self) -> str:
        return self._theme
    
    def get_fps(self) -> int:
        return self._fps

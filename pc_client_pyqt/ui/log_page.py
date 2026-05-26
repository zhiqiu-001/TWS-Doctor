from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit
)
from datetime import datetime


class LogPage(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        self.clear_btn = QPushButton("清空日志")
        toolbar_layout.addWidget(self.clear_btn)
        toolbar_layout.addStretch()
        
        layout.addWidget(toolbar)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFontFamily("Consolas")
        
        layout.addWidget(self.log_text)
        
        self.clear_btn.clicked.connect(self.log_text.clear)
    
    def add_log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

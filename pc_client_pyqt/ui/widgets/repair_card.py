#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复功能卡片组件"""

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal


class RepairCard(QGroupBox):
    """修复功能卡片"""
    
    action_triggered = pyqtSignal(str)
    
    def __init__(self, title, description, icon_text, button_text):
        super().__init__()
        self._title = title
        self._description = description
        self._icon_text = icon_text
        self._button_text = button_text
        self._action_btn = None
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(14, 14, 14, 14)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_label.setFixedSize(32, 32)
        icon_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 255, 136, 0.15);
                border-radius: 8px;
                color: #00ff88;
                font-size: 16px;
                text-align: center;
                line-height: 32px;
            }
        """)
        icon_label.setText(self._icon_text)
        
        title_label = QLabel(self._title)
        title_label.setStyleSheet("color: #e0e0e0; font-size: 13px; font-weight: 600;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        desc_label = QLabel(self._description)
        desc_label.setStyleSheet("color: #888; font-size: 11px;")
        desc_label.setWordWrap(True)
        desc_label.setMaximumHeight(32)
        
        self._action_btn = QPushButton(self._button_text)
        self._action_btn.setFixedHeight(30)
        self._action_btn.clicked.connect(lambda: self.action_triggered.emit(self._title))
        self._action_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                border: none;
                border-radius: 4px;
                padding: 5px 14px;
                color: white;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton:disabled {
                background-color: #2a2d32;
                color: #666;
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(desc_label)
        layout.addWidget(self._action_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QGroupBox {
                background-color: #1e252b;
                border: 1px solid #2a3441;
                border-radius: 8px;
                margin-top: 0px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0;
                height: 0px;
            }
        """)
    
    def set_enabled(self, enabled):
        if self._action_btn:
            self._action_btn.setEnabled(enabled)
    
    def set_executing(self):
        if self._action_btn:
            self._action_btn.setText("执行中...")
            self._action_btn.setEnabled(False)
    
    def complete(self):
        if self._action_btn:
            self._action_btn.setText(self._button_text)
            self._action_btn.setEnabled(True)
    
    def reset(self):
        self.complete()

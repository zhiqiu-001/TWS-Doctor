#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""日志页面"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit,
    QComboBox, QPushButton, QTextEdit
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer


class LogPage(QWidget):
    """日志页面"""
    
    log_search = pyqtSignal(str, str)
    log_export = pyqtSignal()
    log_clear = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 日志输出区域
        log_group = QGroupBox("日志输出")
        log_layout = QVBoxLayout(log_group)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(8)
        
        time_label = QLabel("时间筛选：")
        time_label.setStyleSheet("color: #888;")
        
        self._time_combo = QComboBox()
        self._time_combo.addItems(["全部", "最近 10 分钟", "最近 1 小时", "今天"])
        self._time_combo.setStyleSheet("""
            QComboBox {
                background-color: #1A1D29;
                border: 1px solid #2D3142;
                border-radius: 6px;
                padding: 4px 8px;
                color: #E2E8F0;
                min-width: 120px;
            }
        """)
        # 设置下拉列表样式
        self._time_combo.view().setStyleSheet("""
            QListView {
                background-color: #1A1D29;
                border: 1px solid #2D3142;
                border-radius: 6px;
                color: #E2E8F0;
            }
            QListView::item {
                padding: 4px 8px;
                min-height: 24px;
                border-radius: 4px;
                margin: 2px;
            }
            QListView::item:hover {
                background-color: #3B82F6;
                color: white;
            }
            QListView::item:selected {
                background-color: #2563EB;
                color: white;
                font-weight: bold;
            }
        """)
        
        keyword_label = QLabel("关键词搜索：")
        keyword_label.setStyleSheet("color: #888;")
        
        self._keyword_edit = QLineEdit()
        self._keyword_edit.setPlaceholderText("请输入关键词...")
        self._keyword_edit.setStyleSheet("min-width: 180px;")
        
        search_btn = QPushButton("搜索")
        search_btn.setFixedHeight(24)
        search_btn.setStyleSheet("padding: 3px 12px;")
        search_btn.clicked.connect(self._on_search_clicked)
        
        export_btn = QPushButton("导出日志")
        export_btn.setFixedHeight(24)
        export_btn.setStyleSheet("padding: 3px 12px; background-color: #2a2d32;")
        export_btn.clicked.connect(self.log_export.emit)
        
        clear_btn = QPushButton("清空日志")
        clear_btn.setFixedHeight(24)
        clear_btn.setStyleSheet("padding: 3px 12px; background-color: #2a2d32;")
        clear_btn.clicked.connect(self.log_clear.emit)
        
        toolbar_layout.addWidget(time_label)
        toolbar_layout.addWidget(self._time_combo)
        toolbar_layout.addWidget(keyword_label)
        toolbar_layout.addWidget(self._keyword_edit)
        toolbar_layout.addWidget(search_btn)
        toolbar_layout.addWidget(export_btn)
        toolbar_layout.addWidget(clear_btn)
        toolbar_layout.addStretch()
        
        log_layout.addLayout(toolbar_layout)
        
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        log_layout.addWidget(self._log_text)
        
        layout.addWidget(log_group)
    
    def _on_search_clicked(self):
        keyword = self._keyword_edit.text().strip()
        time_filter = self._time_combo.currentText()
        self.log_search.emit(keyword, time_filter)
    
    def add_log(self, log_line):
        """添加日志"""
        self._log_text.append(log_line)
        QTimer.singleShot(0, self._scroll_log_to_bottom)
    
    def _scroll_log_to_bottom(self):
        scroll_bar = self._log_text.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
    
    def clear_log(self):
        """清空日志"""
        self._log_text.clear()
    
    def set_log_content(self, content):
        """设置日志内容"""
        self._log_text.setHtml(content)

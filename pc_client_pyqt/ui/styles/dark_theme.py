#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""深色主题样式表"""


def get_dark_stylesheet():
    """获取深色主题样式表"""
    return """
        QMainWindow {
            background-color: #0d1117;
            color: #e0e0e0;
        }
        
        QWidget {
            font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
            font-size: 12px;
        }
        
        QPushButton {
            background-color: #0d6efd;
            border: none;
            border-radius: 4px;
            padding: 6px 16px;
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
        
        QComboBox {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 5px 24px 5px 8px;
            color: #e0e0e0;
            min-width: 180px;
            font-size: 12px;
        }
        
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        
        QComboBox::down-arrow {
            image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%238b949e' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
            width: 12px;
            height: 12px;
        }
        
        QComboBox QAbstractItemView {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            color: #e0e0e0;
            selection-background-color: #0d6efd;
        }
        
        QComboBox QAbstractItemView::item {
            padding: 5px 10px;
        }
        
        QTabWidget::tab-bar {
            alignment: left;
        }
        
        QTabWidget::tab {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-bottom: none;
            border-radius: 6px 6px 0 0;
            padding: 8px 20px;
            margin-right: 4px;
            color: #888;
            font-weight: 500;
            font-size: 12px;
        }
        
        QTabWidget::tab:selected {
            background-color: #0d1117;
            color: #0d6efd;
            border-color: #30363d;
            border-bottom: 2px solid #0d6efd;
        }
        
        QTabWidget::pane {
            border: 1px solid #30363d;
            border-radius: 0 6px 6px 6px;
            background-color: #0d1117;
        }
        
        QTableWidget {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 6px;
            gridline-color: #21262d;
        }
        
        QTableWidget::item {
            padding: 8px 10px;
            border-bottom: 1px solid #21262d;
        }
        
        QTableWidget::item:selected {
            background-color: #0d6efd;
            color: white;
        }
        
        QHeaderView::section {
            background-color: #161b22;
            color: #888;
            padding: 8px 10px;
            border: none;
            border-bottom: 1px solid #30363d;
            font-weight: 600;
            font-size: 12px;
        }
        
        QTextEdit {
            background-color: #0d1117;
            border: 1px solid #30363d;
            border-radius: 6px;
            color: #e0e0e0;
            padding: 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 11px;
        }
        
        QLineEdit {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 5px 10px;
            color: #e0e0e0;
            font-size: 12px;
        }
        
        QLineEdit::placeholder {
            color: #666;
        }
        
        QGroupBox {
            background-color: #1e252b;
            border: 1px solid #2a3441;
            border-radius: 8px;
            padding: 12px;
            color: #e0e0e0;
            font-weight: 600;
            margin-top: 10px;
            font-size: 12px;
        }
        
        QGroupBox::title {
            color: #0d6efd;
            padding: 0 6px;
        }
        
        QSpinBox {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 4px;
            color: #e0e0e0;
            width: 70px;
            font-size: 12px;
        }
        
        QToolButton {
            background-color: #161b22;
            border: 1px solid #30363d;
            border-radius: 4px;
            padding: 4px 10px;
            color: #e0e0e0;
            font-size: 12px;
        }
        
        QToolButton:hover {
            background-color: #21262d;
        }
        
        QFrame {
            color: #30363d;
        }
        
        QStatusBar {
            background-color: #161b22;
            color: #888;
            border-top: 1px solid #30363d;
            font-size: 11px;
        }
    """

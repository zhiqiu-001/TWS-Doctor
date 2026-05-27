#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主窗口样式表"""

STYLE_SHEET = """
/* 全局 */
QMainWindow {
    background-color: #0F1118;
}
QWidget {
    color: #E2E8F0;
    font-family: "Microsoft YaHei", sans-serif;
    background-color: #0F1118;
}
/* 顶部标题栏 */
#TitleBar {
    background-color: #1A1D29;
    border-bottom: 1px solid #2D3142;
}
#TitleLabel {
    font-size: 18px;
    font-weight: bold;
    color: #FFFFFF;
}
/* 卡片 */
#Card {
    background-color: #1A1D29;
    border-radius: 8px;
    border: 1px solid #2D3142;
}
/* 按钮 */
QPushButton {
    background-color: #2563EB;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    color: white;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #3B82F6;
}
QPushButton:pressed {
    background-color: #1D4ED8;
}
QPushButton:disabled {
    background-color: #334155;
    color: #94A3B8;
}
/* 下拉框 */
QComboBox {
    background-color: #1A1D29;
    border: 1px solid #2D3142;
    border-radius: 6px;
    padding: 4px 8px;
    color: #E2E8F0;
}
QComboBox::drop-down {
    border: none;
}
QComboBox::down-arrow {
    color: #E2E8F0;
}
/* 下拉弹出窗口容器 */
QComboBox QAbstractItemView {
    background-color: #1A1D29;
    border: none;
    border-radius: 6px;
    color: #E2E8F0;
    selection-background-color: #2563EB;
    show-decoration-selected: 1;
    outline: none;
}
QComboBox QAbstractItemView::item {
    padding: 4px 8px;
    min-height: 24px;
    border-radius: 4px;
    margin: 2px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #3B82F6;
    color: white;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #2563EB;
    color: white;
    font-weight: bold;
}
/* 移除滚动区域边框 */
QComboBox QAbstractScrollArea {
    border: none;
    background-color: transparent;
}
QComboBox QScrollBar:vertical {
    background-color: #1A1D29;
    width: 8px;
}
QComboBox QScrollBar::handle:vertical {
    background-color: #3B82F6;
    border-radius: 4px;
}
/* Tab */
QTabWidget {
    background-color: #0F1118;
}
QTabWidget::pane {
    border: none;
    background-color: #0F1118;
}
QTabBar::tab {
    background-color: #1A1D29;
    padding: 8px 16px;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}
QTabBar::tab:selected {
    background-color: #2563EB;
    color: white;
}
/* 状态栏 */
QStatusBar {
    background-color: #1A1D29;
    color: #94A3B8;
}
/* 标签文字 */
QLabel#SubLabel {
    color: #94A3B8;
    font-size: 12px;
}
/* 分组框 */
QGroupBox {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    margin-top: 18px;
    padding-top: 4px;
}
QGroupBox::title {
    color: #8B949E;
    font-weight: 600;
    padding-left: 8px;
    padding-right: 8px;
    padding-top: 4px;
    padding-bottom: 4px;
    top: -10px;
    left: 8px;
    background-color: #161B22;
    margin-left: 4px;
    margin-right: 4px;
}
/* 表格 */
QTableWidget {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    gridline-color: #21262D;
}
QTableWidget::item {
    padding: 4px;
    border: none;
}
QTableWidget::item:selected {
    background-color: #2563EB;
    color: white;
}
QHeaderView::section {
    background-color: #161B22;
    color: #8B949E;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #30363D;
    font-weight: 600;
}
QHeaderView::section:hover {
    background-color: #21262D;
}
/* 滚动条 */
QScrollBar:vertical {
    background-color: #161B22;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #3B82F6;
    border-radius: 4px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background-color: transparent;
}
/* 文本编辑框 */
QTextEdit {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E2E8F0;
}
QTextEdit:focus {
    border-color: #3B82F6;
    outline: none;
}
/* 行编辑框 */
QLineEdit {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    padding: 4px 8px;
    color: #E2E8F0;
}
QLineEdit:focus {
    border-color: #3B82F6;
    outline: none;
}
QLineEdit::placeholder {
    color: #484F58;
}
/* 数字输入框 */
QSpinBox {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E2E8F0;
}
QSpinBox::up-button, QSpinBox::down-button {
    background-color: #21262D;
    border: none;
}
QSpinBox::up-arrow, QSpinBox::down-arrow {
    color: #E2E8F0;
}
/* 进度条 */
QProgressBar {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #2563EB;
    border-radius: 4px;
}
"""

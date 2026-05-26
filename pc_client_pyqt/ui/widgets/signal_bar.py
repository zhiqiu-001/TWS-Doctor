#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""信号强度柱状图组件"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import Qt


class SignalBarWidget(QWidget):
    """信号强度柱状图"""
    
    def __init__(self, rssi, parent=None):
        super().__init__(parent)
        self.rssi = rssi
        self.setFixedSize(50, 14)
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        bars = 4
        bar_width = 3
        bar_spacing = 4
        max_height = 12
        
        for i in range(bars):
            x = i * (bar_width + bar_spacing)
            height = (i + 1) * max_height // bars
            y = max_height - height
            
            if self.rssi > -50:
                color = QColor("#00ff88") if i < 4 else QColor("#2a2d32")
            elif self.rssi > -70:
                color = QColor("#00d4ff") if i < 3 else QColor("#2a2d32")
            elif self.rssi > -80:
                color = QColor("#ffaa00") if i < 2 else QColor("#2a2d32")
            else:
                color = QColor("#ff4444") if i < 1 else QColor("#2a2d32")
            
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(x, y, bar_width, height)

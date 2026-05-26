#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""状态指示灯组件"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QBrush
from PyQt6.QtCore import Qt, QTimer


class StatusIndicator(QWidget):
    """状态指示灯组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self._color = Qt.GlobalColor.gray
        self._pulse = False
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_pulse)
        self._pulse_opacity = 1.0
    
    def set_color(self, color):
        self._color = color
        self._pulse_opacity = 1.0
        self.update()
    
    def set_pulse(self, enable):
        self._pulse = enable
        if enable:
            self._pulse_timer.start(200)
        else:
            self._pulse_timer.stop()
            self._pulse_opacity = 1.0
            self.update()
    
    def _update_pulse(self):
        self._pulse_opacity = 0.4 if self._pulse_opacity > 0.4 else 1.0
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setOpacity(self._pulse_opacity)
        painter.setBrush(QBrush(self._color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 12, 12)

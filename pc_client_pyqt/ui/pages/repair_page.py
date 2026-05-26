#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复工具页面"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QLabel, QGridLayout
)
from PyQt6.QtCore import pyqtSignal

from ui.widgets.repair_card import RepairCard


class RepairPage(QWidget):
    """修复工具页面"""
    
    repair_action = pyqtSignal(str)
    device_selected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self._devices = []
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 目标设备选择
        device_group = QGroupBox("目标设备")
        device_layout = QHBoxLayout(device_group)
        
        self._device_combo = QComboBox()
        self._device_combo.addItem("请选择设备")
        self._device_combo.currentTextChanged.connect(self._on_device_changed)
        self._device_combo.setStyleSheet("""
            QComboBox {
                background-color: #1A1D29;
                border: 1px solid #2D3142;
                border-radius: 6px;
                padding: 4px 8px;
                color: #E2E8F0;
                min-width: 200px;
            }
        """)
        self._device_combo.view().setStyleSheet("""
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
        device_layout.addWidget(self._device_combo)
        
        layout.addWidget(device_group)
        
        # 修复功能卡片
        cards_widget = QWidget()
        cards_layout = QGridLayout(cards_widget)
        cards_layout.setSpacing(12)
        cards_layout.setContentsMargins(0, 0, 0, 0)
        
        self._card_single = RepairCard(
            "单耳补配",
            "修复单耳配对信息，恢复与另一侧的连接",
            "🎧",
            "执行修复"
        )
        self._card_single.action_triggered.connect(self.repair_action.emit)
        cards_layout.addWidget(self._card_single, 0, 0)
        
        self._card_sync = RepairCard(
            "双耳同步修复",
            "同步左右耳数据，修复主从耳状态异常问题",
            "🔄",
            "执行修复"
        )
        self._card_sync.action_triggered.connect(self.repair_action.emit)
        cards_layout.addWidget(self._card_sync, 0, 1)
        
        self._card_reset = RepairCard(
            "底层配对重置",
            "清除耳机底层配对信息，重置配对状态",
            "🔃",
            "执行修复"
        )
        self._card_reset.action_triggered.connect(self.repair_action.emit)
        cards_layout.addWidget(self._card_reset, 1, 0)
        
        self._card_reconnect = RepairCard(
            "左右耳互联重建",
            "重建左右耳之间的互联关系，修复断联问题",
            "🔗",
            "执行修复"
        )
        self._card_reconnect.action_triggered.connect(self.repair_action.emit)
        cards_layout.addWidget(self._card_reconnect, 1, 1)
        
        layout.addWidget(cards_widget)
        
        # 操作状态
        status_group = QGroupBox("操作状态")
        status_layout = QVBoxLayout(status_group)
        
        self._repair_status_text = QLabel("等待操作...")
        self._repair_status_text.setStyleSheet("color: #888;")
        
        status_layout.addWidget(self._repair_status_text)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        self._card_single.set_enabled(False)
        self._card_sync.set_enabled(False)
        self._card_reset.set_enabled(False)
        self._card_reconnect.set_enabled(False)
        self._device_combo.setEnabled(False)
    
    def _on_device_changed(self, text):
        if text != "请选择设备":
            mac = text.split(" ")[0]
            self.device_selected.emit(mac)
    
    def update_devices(self, devices):
        """更新设备列表"""
        current_text = self._device_combo.currentText()
        self._device_combo.clear()
        self._device_combo.addItem("请选择设备")
        
        for device in devices:
            display_text = f"{device['mac']} ({device['name']})"
            self._device_combo.addItem(display_text)
        
        if current_text:
            index = self._device_combo.findText(current_text)
            if index >= 0:
                self._device_combo.setCurrentIndex(index)
    
    def select_device(self, mac, name):
        """选择指定设备"""
        display_text = f"{mac} ({name})"
        index = self._device_combo.findText(display_text)
        if index >= 0:
            self._device_combo.setCurrentIndex(index)
    
    def set_enabled(self, enabled):
        """设置页面控件状态"""
        self._card_single.set_enabled(enabled)
        self._card_sync.set_enabled(enabled)
        self._card_reset.set_enabled(enabled)
        self._card_reconnect.set_enabled(enabled)
        self._device_combo.setEnabled(enabled)
    
    def set_action_status(self, action, status):
        """设置操作状态"""
        self._repair_status_text.setText(status)
        if action == "单耳补配":
            if status.startswith("正在执行"):
                self._card_single.set_executing()
            else:
                self._card_single.complete()
        elif action == "双耳同步修复":
            if status.startswith("正在执行"):
                self._card_sync.set_executing()
            else:
                self._card_sync.complete()
        elif action == "底层配对重置":
            if status.startswith("正在执行"):
                self._card_reset.set_executing()
            else:
                self._card_reset.complete()
        elif action == "左右耳互联重建":
            if status.startswith("正在执行"):
                self._card_reconnect.set_executing()
            else:
                self._card_reconnect.complete()
    
    def reset_all_cards(self):
        """重置所有卡片状态"""
        self._card_single.complete()
        self._card_sync.complete()
        self._card_reset.complete()
        self._card_reconnect.complete()
        self._repair_status_text.setText("等待操作...")
        self._repair_status_text.setStyleSheet("color: #888;")

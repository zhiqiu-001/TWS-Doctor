#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bose TWS 辅助工具页面"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QProgressBar,
    QFormLayout, QLineEdit, QFrame
)
from PyQt6.QtGui import QBrush, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QTimer


class BoseTWSPage(QWidget):
    """Bose TWS 辅助工具页面"""
    
    connect_device = pyqtSignal(str)
    disconnect_device = pyqtSignal()
    clear_pairing = pyqtSignal()
    read_battery = pyqtSignal()
    read_firmware = pyqtSignal()
    log_clear = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._devices = []
        self._connected_device = None
        self._battery_info = {}
        self._firmware_info = {}
        self._init_ui()
    
    def _init_ui(self):
        # 主布局：上下结构
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)
        
        # 上半部分：左右布局（比例1.5:1 = 3:2）
        top_layout = QHBoxLayout()
        top_layout.setSpacing(12)
        
        # 左边：设备列表区域
        device_group = QGroupBox("已扫描设备")
        device_layout = QVBoxLayout(device_group)
        
        self._device_table = QTableWidget(0, 4)
        self._device_table.setHorizontalHeaderLabels(["设备名称", "MAC 地址", "信号强度", "操作"])
        self._device_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self._device_table.setColumnWidth(0, 180)
        self._device_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self._device_table.setColumnWidth(1, 140)
        self._device_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self._device_table.setColumnWidth(2, 90)
        self._device_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self._device_table.setColumnWidth(3, 70)
        self._device_table.verticalHeader().setVisible(False)
        self._device_table.verticalHeader().setDefaultSectionSize(28)
        self._device_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._device_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._device_table.setShowGrid(False)
        self._device_table.itemSelectionChanged.connect(self._on_device_selected)
        
        device_layout.addWidget(self._device_table)
        top_layout.addWidget(device_group, 3)  # 左侧占3份
        
        # 右边：操作区域（垂直布局）
        right_layout = QVBoxLayout()
        right_layout.setSpacing(12)
        
        # 连接状态区域
        status_group = QGroupBox("连接状态")
        status_layout = QHBoxLayout(status_group)
        
        self._connection_status = QLabel("未连接")
        self._connection_status.setStyleSheet("color: #ff4444; font-weight: bold; font-size: 14px;")
        status_layout.addWidget(self._connection_status)
        
        self._connect_btn = QPushButton("连接")
        self._connect_btn.setFixedHeight(28)
        self._connect_btn.clicked.connect(self._on_connect_clicked)
        self._connect_btn.setEnabled(False)
        
        self._disconnect_btn = QPushButton("断开")
        self._disconnect_btn.setFixedHeight(28)
        self._disconnect_btn.clicked.connect(self._on_disconnect_clicked)
        self._disconnect_btn.setEnabled(False)
        self._disconnect_btn.setStyleSheet("background-color: #dc3545;")
        
        status_layout.addWidget(self._connect_btn)
        status_layout.addWidget(self._disconnect_btn)
        status_layout.addStretch()
        right_layout.addWidget(status_group)
        
        # 设备信息区域
        info_group = QGroupBox("设备信息")
        info_layout = QFormLayout(info_group)
        info_layout.setSpacing(8)
        
        self._battery_level_left = QLineEdit()
        self._battery_level_left.setReadOnly(True)
        self._battery_level_left.setStyleSheet("background-color: #161B22; border: 1px solid #30363D;")
        
        self._battery_level_right = QLineEdit()
        self._battery_level_right.setReadOnly(True)
        self._battery_level_right.setStyleSheet("background-color: #161B22; border: 1px solid #30363D;")
        
        self._firmware_version = QLineEdit()
        self._firmware_version.setReadOnly(True)
        self._firmware_version.setStyleSheet("background-color: #161B22; border: 1px solid #30363D;")
        
        self._device_model = QLineEdit()
        self._device_model.setReadOnly(True)
        self._device_model.setStyleSheet("background-color: #161B22; border: 1px solid #30363D;")
        
        info_layout.addRow(QLabel("左耳电量:"), self._battery_level_left)
        info_layout.addRow(QLabel("右耳电量:"), self._battery_level_right)
        info_layout.addRow(QLabel("固件版本:"), self._firmware_version)
        info_layout.addRow(QLabel("设备型号:"), self._device_model)
        right_layout.addWidget(info_group)
        
        # 功能按钮区域
        func_group = QGroupBox("操作功能")
        func_layout = QHBoxLayout(func_group)
        func_layout.setSpacing(10)
        
        self._clear_pairing_btn = QPushButton("清空配对列表")
        self._clear_pairing_btn.setFixedHeight(32)
        self._clear_pairing_btn.clicked.connect(self._on_clear_pairing)
        self._clear_pairing_btn.setEnabled(False)
        func_layout.addWidget(self._clear_pairing_btn)
        
        self._read_battery_btn = QPushButton("读取电池信息")
        self._read_battery_btn.setFixedHeight(32)
        self._read_battery_btn.clicked.connect(self._on_read_battery)
        self._read_battery_btn.setEnabled(False)
        func_layout.addWidget(self._read_battery_btn)
        
        self._read_firmware_btn = QPushButton("读取固件版本")
        self._read_firmware_btn.setFixedHeight(32)
        self._read_firmware_btn.clicked.connect(self._on_read_firmware)
        self._read_firmware_btn.setEnabled(False)
        func_layout.addWidget(self._read_firmware_btn)
        
        func_layout.addStretch()
        right_layout.addWidget(func_group)
        
        # 进度条区域
        progress_group = QGroupBox("操作进度")
        progress_layout = QVBoxLayout(progress_group)
        
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(0)
        self._progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #161B22;
                border: 1px solid #30363D;
                border-radius: 4px;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: #2563EB;
                border-radius: 4px;
            }
        """)
        
        self._progress_label = QLabel("等待操作...")
        self._progress_label.setStyleSheet("color: #888; font-size: 12px;")
        
        progress_layout.addWidget(self._progress_bar)
        progress_layout.addWidget(self._progress_label)
        right_layout.addWidget(progress_group)
        
        right_layout.addStretch()
        top_layout.addLayout(right_layout, 2)  # 右侧占2份
        
        main_layout.addLayout(top_layout)
        
        # 下半部分：日志输出区域
        log_group = QGroupBox("操作日志")
        log_layout = QVBoxLayout(log_group)
        
        clear_log_btn = QPushButton("清空日志")
        clear_log_btn.setFixedHeight(24)
        clear_log_btn.setStyleSheet("padding: 3px 12px; background-color: #2a2d32;")
        clear_log_btn.clicked.connect(self.log_clear.emit)
        
        log_layout.addWidget(clear_log_btn)
        
        self._log_text = QTextEdit()
        self._log_text.setReadOnly(True)
        self._log_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        log_layout.addWidget(self._log_text)
        
        main_layout.addWidget(log_group)
    
    def _on_device_selected(self):
        """设备选中事件处理"""
        selected_items = self._device_table.selectedItems()
        if selected_items and not self._connected_device:
            self._connect_btn.setEnabled(True)
        else:
            if not self._connected_device:
                self._connect_btn.setEnabled(False)
    
    def _on_connect_clicked(self):
        selected_items = self._device_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            mac = self._device_table.item(row, 1).text()
            self._connect_btn.setEnabled(False)
            self._connection_status.setText("连接中...")
            self._connection_status.setStyleSheet("color: #0d6efd; font-weight: bold;")
            self.add_log("INFO", f"正在连接设备: {mac}")
            self.connect_device.emit(mac)
    
    def _on_disconnect_clicked(self):
        self._disconnect_btn.setEnabled(False)
        self._connection_status.setText("断开中...")
        self._connection_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        self.add_log("INFO", "正在断开连接")
        self.disconnect_device.emit()
    
    def _on_clear_pairing(self):
        self._clear_pairing_btn.setEnabled(False)
        self._progress_label.setText("正在清空配对列表...")
        self._progress_bar.setValue(0)
        self._start_progress_timer()
        self.add_log("INFO", "开始清空配对列表")
        self.clear_pairing.emit()
    
    def _on_read_battery(self):
        self._read_battery_btn.setEnabled(False)
        self._progress_label.setText("正在读取电池信息...")
        self._progress_bar.setValue(0)
        self._start_progress_timer()
        self.add_log("INFO", "开始读取电池信息")
        self.read_battery.emit()
    
    def _on_read_firmware(self):
        self._read_firmware_btn.setEnabled(False)
        self._progress_label.setText("正在读取固件版本...")
        self._progress_bar.setValue(0)
        self._start_progress_timer()
        self.add_log("INFO", "开始读取固件版本")
        self.read_firmware.emit()
    
    def _start_progress_timer(self):
        if hasattr(self, '_progress_timer'):
            self._progress_timer.stop()
        
        self._progress_value = 0
        self._progress_timer = QTimer()
        self._progress_timer.timeout.connect(self._update_progress)
        self._progress_timer.start(100)
    
    def _update_progress(self):
        self._progress_value += 5
        if self._progress_value >= 100:
            self._progress_value = 95
        self._progress_bar.setValue(self._progress_value)
    
    def _stop_progress_timer(self):
        if hasattr(self, '_progress_timer'):
            self._progress_timer.stop()
        self._progress_bar.setValue(100)
    
    def update_devices(self, devices):
        """更新设备列表"""
        self._devices = devices
        self._device_table.setRowCount(0)
        
        for device in devices:
            row = self._device_table.rowCount()
            self._device_table.insertRow(row)
            
            name_item = QTableWidgetItem(device["name"])
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._device_table.setItem(row, 0, name_item)
            
            mac_item = QTableWidgetItem(device["mac"])
            mac_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._device_table.setItem(row, 1, mac_item)
            
            rssi_item = QTableWidgetItem(f"{device['rssi']} dBm")
            rssi_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            if device["rssi"] > -50:
                rssi_item.setForeground(QBrush(QColor("#00ff88")))
            elif device["rssi"] > -70:
                rssi_item.setForeground(QBrush(QColor("#00d4ff")))
            else:
                rssi_item.setForeground(QBrush(QColor("#ff4444")))
            self._device_table.setItem(row, 2, rssi_item)
            
            # 添加连接按钮
            connect_btn = QPushButton("连接")
            connect_btn.setFixedHeight(22)
            connect_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2563EB;
                    border: none;
                    border-radius: 4px;
                    padding: 2px 8px;
                    color: white;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #3B82F6;
                }
                QPushButton:disabled {
                    background-color: #334155;
                    color: #94A3B8;
                }
            """)
            connect_btn.clicked.connect(lambda checked, mac=device["mac"]: self._on_row_connect(mac))
            connect_btn.setEnabled(not self._connected_device)
            self._device_table.setCellWidget(row, 3, connect_btn)
    
    def _on_row_connect(self, mac):
        """行内连接按钮点击处理"""
        self._connect_btn.setEnabled(False)
        self._connection_status.setText("连接中...")
        self._connection_status.setStyleSheet("color: #0d6efd; font-weight: bold;")
        self.add_log("INFO", f"正在连接设备: {mac}")
        self.connect_device.emit(mac)
    
    def set_connected(self, device_info):
        """设置连接状态"""
        self._connected_device = device_info
        self._connection_status.setText("已连接")
        self._connection_status.setStyleSheet("color: #00ff88; font-weight: bold;")
        self._connect_btn.setEnabled(False)
        self._disconnect_btn.setEnabled(True)
        self._clear_pairing_btn.setEnabled(True)
        self._read_battery_btn.setEnabled(True)
        self._read_firmware_btn.setEnabled(True)
        self.add_log("SUCCESS", f"成功连接到: {device_info.get('name', 'Unknown')}")
        
        if device_info.get('model'):
            self._device_model.setText(device_info['model'])
    
    def set_disconnected(self):
        """设置断开状态"""
        self._connected_device = None
        self._connection_status.setText("未连接")
        self._connection_status.setStyleSheet("color: #ff4444; font-weight: bold;")
        self._connect_btn.setEnabled(True if self._devices else False)
        self._disconnect_btn.setEnabled(False)
        self._clear_pairing_btn.setEnabled(False)
        self._read_battery_btn.setEnabled(False)
        self._read_firmware_btn.setEnabled(False)
        self._stop_progress_timer()
        self.add_log("INFO", "已断开连接")
    
    def update_battery_info(self, left_level, right_level):
        """更新电池信息"""
        self._battery_level_left.setText(f"{left_level}%")
        self._battery_level_right.setText(f"{right_level}%")
        self._stop_progress_timer()
        self._progress_label.setText("电池读取完成")
        self._read_battery_btn.setEnabled(True)
        self.add_log("SUCCESS", f"电池信息 - 左耳: {left_level}%, 右耳: {right_level}%")
    
    def update_firmware_info(self, version, model=None):
        """更新固件信息"""
        self._firmware_version.setText(version)
        if model:
            self._device_model.setText(model)
        self._stop_progress_timer()
        self._progress_label.setText("固件读取完成")
        self._read_firmware_btn.setEnabled(True)
        self.add_log("SUCCESS", f"固件版本: {version}")
    
    def set_clear_pairing_result(self, success):
        """设置清空配对结果"""
        self._stop_progress_timer()
        if success:
            self._progress_label.setText("配对列表清空完成")
            self.add_log("SUCCESS", "配对列表已清空")
        else:
            self._progress_label.setText("清空配对失败")
            self.add_log("ERROR", "清空配对列表失败")
        self._clear_pairing_btn.setEnabled(True)
    
    def add_log(self, level, message):
        """添加日志"""
        from datetime import datetime
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        color_map = {
            "INFO": "#0d6efd",
            "SUCCESS": "#00ff88",
            "WARNING": "#ffaa00",
            "ERROR": "#ff4444",
        }
        color = color_map.get(level, "#e0e0e0")
        log_line = f'<span style="color: #666;">[{now}]</span> ' \
                   f'<span style="color: {color}; font-weight: 600;">[{level}]</span> ' \
                   f'<span style="color: #e0e0e0;">{message}</span><br>'
        self._log_text.append(log_line)
        QTimer.singleShot(0, self._scroll_log_to_bottom)
    
    def _scroll_log_to_bottom(self):
        scroll_bar = self._log_text.verticalScrollBar()
        scroll_bar.setValue(scroll_bar.maximum())
    
    def clear_log(self):
        """清空日志"""
        self._log_text.clear()
    
    def set_scan_enabled(self, enabled):
        """设置扫描状态"""
        if enabled and not self._connected_device:
            self._connect_btn.setEnabled(True if self._devices else False)
        else:
            self._connect_btn.setEnabled(False)
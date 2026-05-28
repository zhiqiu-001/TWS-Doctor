#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""设备扫描页面"""

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit,
    QLineEdit, QComboBox
)
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from ui.widgets.signal_bar import SignalBarWidget


class ScanPage(QWidget):
    """设备扫描页面"""
    
    scan_started = pyqtSignal(int)
    scan_stopped = pyqtSignal()
    device_selected = pyqtSignal(str)
    log_search = pyqtSignal(str, str)
    log_export = pyqtSignal()
    log_clear = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self._devices = []
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # 扫描控制区域
        control_group = QGroupBox("扫描控制")
        control_layout = QHBoxLayout(control_group)
        control_layout.setSpacing(10)
        
        count_layout = QHBoxLayout()
        count_layout.setSpacing(6)
        count_label = QLabel("扫描数量：")
        count_label.setStyleSheet("color: #888;")
        self._count_spin = QSpinBox()
        self._count_spin.setRange(1, 100)
        self._count_spin.setValue(10)
        count_layout.addWidget(count_label)
        count_layout.addWidget(self._count_spin)
        
        self._scan_btn = QPushButton("开始扫描")
        self._scan_btn.setFixedHeight(28)
        self._scan_btn.clicked.connect(self._on_scan_clicked)
        
        self._clear_btn = QPushButton("清空列表")
        self._clear_btn.setFixedHeight(28)
        self._clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2d32;
                border: none;
                border-radius: 4px;
                padding: 4px 14px;
                color: #e0e0e0;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #3a3f45;
            }
        """)
        self._clear_btn.clicked.connect(self._clear_device_list)
        
        control_layout.addLayout(count_layout)
        control_layout.addWidget(self._scan_btn)
        control_layout.addWidget(self._clear_btn)
        control_layout.addStretch()
        
        layout.addWidget(control_group)
        
        # 设备列表区域
        list_group = QGroupBox("设备列表")
        list_layout = QVBoxLayout(list_group)

        self._device_table = QTableWidget(0, 6)

        self._device_table.setHorizontalHeaderLabels([
            "序号",
            "设备名称",
            "MAC 地址",
            "地址类型",
            "信号强度",
            "设备类型"
        ])

        # 序号
        self._device_table.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.Fixed
        )
        self._device_table.setColumnWidth(0, 45)

        # 设备名称
        self._device_table.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.Fixed
        )
        self._device_table.setColumnWidth(1, 200)

        # MAC
        self._device_table.horizontalHeader().setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.Fixed
        )
        self._device_table.setColumnWidth(2, 150)

        # 地址类型
        self._device_table.horizontalHeader().setSectionResizeMode(
            3,
            QHeaderView.ResizeMode.Fixed
        )
        self._device_table.setColumnWidth(3, 90)

        # 信号强度
        self._device_table.horizontalHeader().setSectionResizeMode(
            4,
            QHeaderView.ResizeMode.Fixed
        )
        self._device_table.setColumnWidth(4, 135)

        # 设备类型
        self._device_table.horizontalHeader().setSectionResizeMode(
            5,
            QHeaderView.ResizeMode.Fixed
        )
        self._device_table.setColumnWidth(5, 85)

        self._device_table.verticalHeader().setVisible(False)
        self._device_table.verticalHeader().setDefaultSectionSize(28)

        self._device_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self._device_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self._device_table.setShowGrid(False)

        self._device_table.doubleClicked.connect(
            self._on_device_double_clicked
        )

        self._add_empty_state_to_table()
        
        list_layout.addWidget(self._device_table)
        
        # 列表底部状态
        list_bottom_layout = QHBoxLayout()
        list_bottom_layout.setSpacing(10)
        
        self._scan_result_label = QLabel("扫描结果：0 个设备")
        self._scan_result_label.setStyleSheet("color: #666; font-size: 11px;")
        
        self._last_update_label = QLabel("")
        self._last_update_label.setStyleSheet("color: #666; font-size: 11px;")
        
        list_bottom_layout.addWidget(self._scan_result_label)
        list_bottom_layout.addStretch()
        list_bottom_layout.addWidget(self._last_update_label)
        
        list_layout.addLayout(list_bottom_layout)
        
        layout.addWidget(list_group)
        
        # 日志输出区域
        log_group = QGroupBox("日志输出")
        log_layout = QVBoxLayout(log_group)
        
        # 日志工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(8)
        
        time_label = QLabel("时间筛选：")
        time_label.setStyleSheet("color: #888;")
        
        self._time_combo = QComboBox()
        self._time_combo.addItems(["全部", "最近 10 分钟", "最近 1 小时", "今天"])
        self._time_combo.setStyleSheet("min-width: 120px;")
        
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
        
        self._scan_btn.setEnabled(False)
        self._clear_btn.setEnabled(False)
        self._count_spin.setEnabled(False)
    
    def _add_empty_state_to_table(self):
        self._device_table.setRowCount(1)
        item = QTableWidgetItem("未扫描到蓝牙设备，请点击「开始扫描」")
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        item.setForeground(QBrush(QColor("#666")))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self._device_table.setItem(0, 1, item)
        self._device_table.setSpan(0, 1, 1, 4)
    
    def _on_scan_clicked(self):
        if self._scan_btn.text() == "开始扫描":
            self._scan_btn.setText("停止扫描")
            self._scan_btn.setEnabled(False)
            self.scan_started.emit(self._count_spin.value())
        else:
            self._scan_btn.setText("开始扫描")
            self._scan_btn.setEnabled(True)
            self.scan_stopped.emit()
    
    def _clear_device_list(self):
        self._device_table.setRowCount(0)
        self._add_empty_state_to_table()
        self._scan_result_label.setText("扫描结果：0 个设备")
    
    def _on_device_double_clicked(self, index):
        if self._device_table.rowCount() == 1 and self._device_table.item(0, 1) and self._device_table.item(0, 1).text().startswith("未扫描到"):
            return
        mac = self._device_table.item(index.row(), 2).text()
        self.device_selected.emit(mac)
    
    def _on_search_clicked(self):
        keyword = self._keyword_edit.text().strip()
        time_filter = self._time_combo.currentText()
        self.log_search.emit(keyword, time_filter)
    
    def update_devices(self, devices):
        """更新设备列表"""
        self._devices = devices
        self._device_table.setRowCount(0)
        
        if not devices:
            self._add_empty_state_to_table()
            return
        
        for i, device in enumerate(devices, 1):
            row = self._device_table.rowCount()
            self._device_table.insertRow(row)
            
            # 序号
            index_item = QTableWidgetItem(str(i))
            index_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            index_item.setForeground(QBrush(QColor("#888")))
            index_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._device_table.setItem(row, 0, index_item)
            
            # 设备名称
            name_item = QTableWidgetItem(device["name"])
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._device_table.setItem(row, 1, name_item)
            
            # MAC 地址
            mac_item = QTableWidgetItem(device["mac"])
            mac_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            self._device_table.setItem(row, 2, mac_item)

            # 地址类型
            addr_type_text = (
                "PUBLIC"
                if device.get("addr_type", 0) == 0
                else "RANDOM"
            )

            addr_type_item = QTableWidgetItem(addr_type_text)
            addr_type_item.setFlags(
                Qt.ItemFlag.ItemIsEnabled |
                Qt.ItemFlag.ItemIsSelectable
            )

            self._device_table.setItem(row, 3, addr_type_item)
            
            # 信号强度
            rssi_widget = QWidget()
            rssi_layout = QHBoxLayout(rssi_widget)
            rssi_layout.setContentsMargins(5, 0, 0, 0)
            rssi_layout.setSpacing(8)
            rssi_layout.addWidget(SignalBarWidget(device["rssi"]))
            
            rssi_value = QLabel(f"{device['rssi']} dBm")
            if device["rssi"] > -50:
                rssi_value.setStyleSheet("color: #00ff88;")
            elif device["rssi"] > -70:
                rssi_value.setStyleSheet("color: #00d4ff;")
            elif device["rssi"] > -80:
                rssi_value.setStyleSheet("color: #ffaa00;")
            else:
                rssi_value.setStyleSheet("color: #ff4444;")
            
            rssi_layout.addWidget(rssi_value)
            rssi_layout.addStretch()
            
            self._device_table.setCellWidget(row, 4, rssi_widget)
            
            # 设备类型
            type_item = QTableWidgetItem(device["type"])
            type_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            type_item.setForeground(QBrush(QColor("#0d6efd")))
            self._device_table.setItem(row, 5, type_item)
        
        self._scan_result_label.setText(f"扫描结果：{len(devices)} 个设备")
        self._last_update_time = datetime.now().strftime("%H:%M:%S")
        self._last_update_label.setText(f"最后更新：{self._last_update_time}")
    
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
    
    def set_scan_enabled(self, enabled):
        """设置扫描按钮状态"""
        self._scan_btn.setEnabled(enabled)
        self._clear_btn.setEnabled(enabled)
        self._count_spin.setEnabled(enabled)
    
    def set_scanning(self, scanning):
        """设置扫描状态"""
        if scanning:
            self._scan_btn.setText("停止扫描")
            self._scan_btn.setEnabled(False)
        else:
            self._scan_btn.setText("开始扫描")
            self._scan_btn.setEnabled(True)
    
    def get_selected_device(self):
        """获取选中的设备"""
        selected_items = self._device_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            return {
                "name": self._device_table.item(row, 1).text(),
                "mac": self._device_table.item(row, 2).text()
            }
        return None
    
    def update_scan_count(self, count):
        """更新扫描数量"""
        self._scan_result_label.setText(f"扫描结果：{count} 个设备")

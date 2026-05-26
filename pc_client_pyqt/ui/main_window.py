#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""主窗口（1:1 还原设计 UI 版）"""

import sys
import os
import serial
import serial.tools.list_ports
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QStatusBar, QTabWidget, QFrame, QToolButton, QMessageBox,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from ui.pages.scan_page import ScanPage
from ui.pages.repair_page import RepairPage
from ui.pages.log_page import LogPage
from ui.widgets.status_indicator import StatusIndicator


class SerialReaderThread(QThread):
    """串口数据接收线程"""
    
    data_received = pyqtSignal(object, object)
    
    def __init__(self, serial_port):
        super().__init__()
        self._serial = serial_port
        self._running = True
    
    def run(self):
        while self._running and self._serial.is_open:
            try:
                if self._serial.in_waiting > 0:
                    data = self._serial.readline().decode('utf-8', errors='ignore').strip()
                    if data:
                        # 尝试解析协议包
                        from core.protocol import parse_packet, PacketType
                        try:
                            packet_type, parsed_data = parse_packet(data)
                            if packet_type and packet_type != PacketType.UNKNOWN:
                                self.data_received.emit(packet_type, parsed_data)
                        except:
                            # 非协议格式的数据不做解析
                            pass
            except Exception as e:
                pass
    
    def stop(self):
        self._running = False


# ========== 全局样式（贴近设计稿深色风格） ==========
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
    margin-top: 0.5em;
}
QGroupBox::title {
    color: #8B949E;
    font-weight: 600;
    padding-left: 8px;
    padding-right: 8px;
}
/* 表格 */
QTableWidget {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    gridline-color: #21262D;
}
QTableWidget::item {
    background-color: #161B22;
    color: #E2E8F0;
}
QTableWidget::item:selected {
    background-color: #238636;
    color: white;
}
QHeaderView::section {
    background-color: #21262D;
    color: #8B949E;
    border: none;
    padding: 4px;
    font-weight: 600;
}
/* 文本框 */
QLineEdit {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 6px;
    padding: 4px 8px;
    color: #E2E8F0;
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
/* 文本编辑器 */
QTextEdit {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #E2E8F0;
}
QTextEdit QScrollBar:vertical {
    background-color: #161B22;
    width: 8px;
}
QTextEdit QScrollBar::handle:vertical {
    background-color: #30363D;
    border-radius: 4px;
}
"""


class MainWindow(QMainWindow):
    """主窗口（1:1 设计还原）"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESP32 TWS 蓝牙耳机修复工具 v1.0.0")
        self.setGeometry(100, 100, 1280, 800)
        self.setStyleSheet(STYLE_SHEET)

        self._serial_connected = False
        self._scanning = False
        self._repairing = False
        self._selected_device = None
        self._devices = []
        self._all_logs = []

        self._init_ui()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. 顶部标题栏
        main_layout.addWidget(self._build_title_bar())

        # 2. 主体：左侧状态 + 右侧 Tab 区
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(12, 12, 12, 12)
        body_layout.setSpacing(12)

        # 左侧（串口+状态卡片）
        left_card = self._build_left_card()
        body_layout.addWidget(left_card, stretch=1)

        # 右侧（Tab页面）
        right_widget = self._build_right_tabs()
        body_layout.addWidget(right_widget, stretch=3)

        main_layout.addLayout(body_layout)

        # 3. 底部状态栏
        self._status_bar = QStatusBar()
        self._status_bar.showMessage("就绪")
        self.setStatusBar(self._status_bar)

    def _build_title_bar(self):
        bar = QWidget()
        bar.setObjectName("TitleBar")
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("ESP32 TWS 蓝牙耳机修复工具")
        title.setObjectName("TitleLabel")
        layout.addWidget(title)
        layout.addStretch()

        version = QLabel("v1.0.0")
        version.setObjectName("SubLabel")
        layout.addWidget(version)
        return bar

    def _build_left_card(self):
        card = QWidget()
        card.setObjectName("Card")
        card.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # 串口标题
        lbl = QLabel("串口连接")
        lbl.setStyleSheet("font-size:14px; font-weight:bold;")
        layout.addWidget(lbl)

        # 串口选择
        self._port_combo = QComboBox()
        self._port_combo.addItems(["COM7 - USB-SERIAL CH340 v1.0.0"])
        self._port_combo.setCurrentText("COM7 - USB-SERIAL CH340 v1.0.0")
        self._port_combo.setStyleSheet("""
            QComboBox {
                background-color: #1A1D29;
                border: 1px solid #2D3142;
                border-radius: 6px;
                padding: 4px 8px;
                color: #E2E8F0;
                min-width: 200px;
            }
        """)
        self._port_combo.view().setStyleSheet("""
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
        layout.addWidget(self._port_combo)

        # 按钮行：刷新、连接
        btn_layout = QHBoxLayout()
        self._refresh_btn = QPushButton("刷新")
        self._refresh_btn.clicked.connect(self._refresh_ports)
        self._connect_btn = QPushButton("连接")
        self._connect_btn.clicked.connect(self._toggle_connection)
        btn_layout.addWidget(self._refresh_btn)
        btn_layout.addWidget(self._connect_btn)
        layout.addLayout(btn_layout)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color:#2D3142;")
        layout.addWidget(line)

        # 状态指示
        status_lbl = QLabel("设备状态")
        status_lbl.setStyleSheet("font-size:14px; font-weight:bold;")
        layout.addWidget(status_lbl)

        status_layout = QHBoxLayout()
        self._status_indicator = StatusIndicator()
        self._status_indicator.set_color(Qt.GlobalColor.gray)
        self._status_label = QLabel("未连接")
        self._status_label.setStyleSheet("color:#888; font-weight:600;")
        status_layout.addWidget(self._status_indicator)
        status_layout.addWidget(self._status_label)
        layout.addLayout(status_layout)

        self._hint_label = QLabel("请连接 ESP32 设备")
        self._hint_label.setObjectName("SubLabel")
        layout.addWidget(self._hint_label)

        layout.addStretch()
        return card

    def _build_right_tabs(self):
        self._tab_widget = QTabWidget()

        self._scan_page = ScanPage()
        self._scan_page.scan_started.connect(self._on_scan_started)
        self._scan_page.scan_stopped.connect(self._on_scan_stopped)
        self._scan_page.device_selected.connect(self._on_device_selected)
        self._scan_page.log_search.connect(self._search_logs)
        self._scan_page.log_export.connect(self._export_logs)
        self._scan_page.log_clear.connect(self._clear_logs)
        self._tab_widget.addTab(self._scan_page, "设备扫描")

        self._repair_page = RepairPage()
        self._repair_page.repair_action.connect(self._on_repair_action)
        self._repair_page.device_selected.connect(self._on_device_selected)
        self._tab_widget.addTab(self._repair_page, "修复工具")

        self._log_page = LogPage()
        self._log_page.log_search.connect(self._search_logs_full)
        self._log_page.log_export.connect(self._export_logs)
        self._log_page.log_clear.connect(self._clear_logs)
        self._tab_widget.addTab(self._log_page, "日志")

        return self._tab_widget

    # ========== 连接相关 ==========

    def _toggle_connection(self):
        if self._serial_connected:
            self._disconnect_serial()
        else:
            self._connect_serial()

    def _connect_serial(self):
        self._status_indicator.set_color(Qt.GlobalColor.blue)
        self._status_indicator.set_pulse(True)
        self._status_label.setText("连接中")
        self._status_label.setStyleSheet("color: #0d6efd;")

        port_name = self._port_combo.currentText().split(' - ')[0]

        self._hint_label.setText(f"正在连接 {port_name}...")
        self._connect_btn.setText("断开")

        try:
            self._serial = serial.Serial(
                port=port_name,
                baudrate=115200,
                timeout=1,
                parity='N',
                stopbits=1,
                bytesize=8
            )

            # 创建串口接收线程
            self._serial_thread = SerialReaderThread(self._serial)
            self._serial_thread.data_received.connect(self._handle_serial_data)
            self._serial_thread.start()

            QTimer.singleShot(500, self._on_connect_success)

        except Exception as e:
            QTimer.singleShot(
                0,
                lambda e=e: self._on_connect_failed(str(e))
            )

    def _on_connect_success(self):
        self._serial_connected = True
        self._status_indicator.set_color(Qt.GlobalColor.green)
        self._status_indicator.set_pulse(False)
        self._status_label.setText("已就绪")
        self._status_label.setStyleSheet("color: #00ff88;")
        port_name = self._port_combo.currentText().split(' - ')[0]
        self._hint_label.setText(f"已连接到 {port_name}")
        self._scan_page.set_scan_enabled(True)
        self._repair_page.set_enabled(True)
        self.add_log("SUCCESS", f"串口 {port_name} 打开成功")
        self.add_log("SUCCESS", "ESP32 设备连接成功")
    
    def _on_connect_failed(self, error_msg):
        self._status_indicator.set_color(Qt.GlobalColor.red)
        self._status_indicator.set_pulse(False)
        self._status_label.setText("连接失败")
        self._status_label.setStyleSheet("color: #ff4444;")
        self._hint_label.setText(f"错误: {error_msg}")
        self._connect_btn.setText("连接")
        self.add_log("ERROR", f"串口连接失败: {error_msg}")

    def _disconnect_serial(self):
        self._serial_connected = False
        
        # 停止串口线程并关闭串口
        if hasattr(self, '_serial_thread'):
            self._serial_thread.stop()
            self._serial_thread.wait()
        
        if hasattr(self, '_serial') and self._serial.is_open:
            self._serial.close()
        
        self._status_indicator.set_color(Qt.GlobalColor.gray)
        self._status_indicator.set_pulse(False)
        self._status_label.setText("未连接")
        self._status_label.setStyleSheet("color: #888;")
        self._hint_label.setText("请连接 ESP32 设备")
        self._connect_btn.setText("连接")
        self._scan_page.set_scan_enabled(False)
        self._repair_page.set_enabled(False)
        self.add_log("INFO", "串口连接已断开")
    
    def _handle_serial_data(self, packet_type, data):
        """处理从串口接收到的数据"""
        from core.protocol import PacketType
        
        # 处理BLE扫描结果
        if packet_type == PacketType.SCAN_BLE:
            # 检查是否已达到扫描数量限制
            if hasattr(self, '_scan_count_limit') and len(self._devices) >= self._scan_count_limit:
                return
            
            device = {
                "name": data.get("name", "Unknown"),
                "mac": data.get("addr", "").upper(),
                "rssi": data.get("rssi", 0),
                "type": "BLE"
            }
            
            # 检查是否已存在相同MAC的设备（去重）
            if device["mac"] and not any(d['mac'] == device['mac'] for d in self._devices):
                self._devices.append(device)
                self.add_log("SCAN", f"发现设备: {device['name']} ({device['mac']})")
                # 更新设备列表UI
                self.update_devices_from_serial(self._devices)
        
        # 处理扫描状态
        elif packet_type == PacketType.STATUS_SCANNING:
            count = data.get("count", 0)
            self._scan_count = count
            self._scan_page.update_scan_count(count)
        
        elif packet_type == PacketType.STATUS_IDLE:
            self._scan_count = 0
            self._scan_page.update_scan_count(0)

    # ========== 扫描相关 ==========
    def _on_scan_started(self, count):
        self._scanning = True
        self._scan_count_limit = count  # 保存扫描数量限制
        self._devices = []  # 清空设备列表
        self.add_log("INFO", f"开始扫描，数量限制: {count}")
        self._send_command(f"CMD|SCAN_START|{count}")

    def _on_scan_stopped(self):
        self._scanning = False
        self.add_log("INFO", "停止扫描")
        self._send_command("CMD|SCAN_STOP")
        self._scan_page.set_scanning(False)

    def _send_command(self, command):
        if self._serial_connected and hasattr(self, '_serial'):
            try:
                self._serial.write((command + '\n').encode('utf-8'))
            except Exception as e:
                self.add_log("ERROR", f"发送命令失败: {str(e)}")

    def update_devices_from_serial(self, devices):
        self._devices = devices
        self._scan_page.update_devices(devices)
        self._repair_page.update_devices(devices)
        self._scan_page.set_scanning(False)

    def _on_device_selected(self, mac):
        self._selected_device = mac
        device = next((d for d in self._devices if d['mac'] == mac), None)
        if device:
            self.add_log("INFO", f"选中设备：{device['name']} ({mac})")

    # ========== 修复相关 ==========
    def _on_repair_action(self, action):
        if not self._selected_device:
            QMessageBox.warning(self, "警告", "请先选择目标设备")
            return
        self._repairing = True
        self._status_indicator.set_color(Qt.GlobalColor.yellow)
        self._status_indicator.set_pulse(True)
        self._status_label.setText("修复中")
        self._status_label.setStyleSheet("color: #ffaa00;")
        self._repair_page.set_action_status(action, f"正在执行：{action}...")
        self._progress = 0
        self._progress_timer = QTimer()
        self._progress_timer.timeout.connect(self._update_repair_progress)
        self._progress_timer.start(200)
        self.add_log("INFO", f"开始执行修复操作：{action}")

    def _update_repair_progress(self):
        self._progress += 10
        if self._progress >= 100:
            self._progress_timer.stop()
            self._on_repair_complete()

    def _on_repair_complete(self):
        self._repairing = False
        if self._serial_connected:
            self._status_indicator.set_color(Qt.GlobalColor.green)
            self._status_indicator.set_pulse(False)
            self._status_label.setText("已就绪")
            self._status_label.setStyleSheet("color: #00ff88;")
        self._repair_page.reset_all_cards()
        self.add_log("SUCCESS", "修复操作完成")
        QMessageBox.information(self, "操作完成", "修复完成！")

    # ========== 日志相关 ==========
    def add_log(self, level, message):
        now = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        self._all_logs.append({"timestamp": now, "level": level, "message": message})
        color_map = {
            "INFO": "#0d6efd",
            "SUCCESS": "#00ff88",
            "WARNING": "#ffaa00",
            "ERROR": "#ff4444",
            "SCAN": "#aa88ff",
        }
        color = color_map.get(level, "#e0e0e0")
        log_line = f'<span style="color: #666;">[{now}]</span> ' \
                   f'<span style="color: {color}; font-weight: 600;">[{level}]</span> ' \
                   f'<span style="color: #e0e0e0;">{message}</span><br>'
        self._scan_page.add_log(log_line)
        self._log_page.add_log(log_line)

    def _search_logs(self, keyword, time_filter):
        filtered = self._filter_logs(keyword, time_filter)
        self._scan_page.clear_log()
        for log in filtered:
            self._scan_page.add_log(self._format_log_line(log))
        self.add_log("INFO", f"搜索完成，找到 {len(filtered)} 条匹配日志")

    def _search_logs_full(self, keyword, time_filter):
        filtered = self._filter_logs(keyword, time_filter)
        self._log_page.clear_log()
        for log in filtered:
            self._log_page.add_log(self._format_log_line(log))
        self.add_log("INFO", f"搜索完成，找到 {len(filtered)} 条匹配日志")

    def _filter_logs(self, keyword, time_filter):
        filtered = []
        for log in self._all_logs:
            if keyword and keyword.lower() not in log["message"].lower() and keyword.lower() not in log["level"].lower():
                continue
            filtered.append(log)
        return filtered

    def _format_log_line(self, log):
        color_map = {
            "INFO": "#0d6efd",
            "SUCCESS": "#00ff88",
            "WARNING": "#ffaa00",
            "ERROR": "#ff4444",
            "SCAN": "#aa88ff",
        }
        color = color_map.get(log["level"], "#e0e0e0")
        return f'<span style="color: #666;">[{log["timestamp"]}]</span> ' \
               f'<span style="color: {color}; font-weight: 600;">[{log["level"]}]</span> ' \
               f'<span style="color: #e0e0e0;">{log["message"]}</span><br>'

    def _export_logs(self):
        if not self._all_logs:
            QMessageBox.information(self, "提示", "没有日志可以导出")
            return
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        filename = f"esp32_tws_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(desktop, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                for log in self._all_logs:
                    f.write(f"[{log['timestamp']}] [{log['level']}] {log['message']}\n")
            QMessageBox.information(self, "成功", f"日志已导出到:\n{filepath}")
            self.add_log("SUCCESS", f"日志已导出到 {filepath}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"导出日志失败: {str(e)}")
            self.add_log("ERROR", f"导出日志失败: {str(e)}")

    def _clear_logs(self):
        reply = QMessageBox.question(self, "确认", "确定要清空所有日志吗？",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._scan_page.clear_log()
            self._log_page.clear_log()
            self._all_logs = []
            self.add_log("INFO", "日志已清空")
    
    def _refresh_ports(self):
        """刷新串口列表"""
        self.add_log("INFO", "正在刷新串口列表...")
        try:
            ports = serial.tools.list_ports.comports()
            port_list = [f"{p.device} - {p.description}" for p in ports]
            
            current_port = self._port_combo.currentText()
            self._port_combo.clear()
            
            if port_list:
                self._port_combo.addItems(port_list)
                if current_port in port_list:
                    self._port_combo.setCurrentText(current_port)
                self.add_log("SUCCESS", f"已刷新 {len(port_list)} 个串口")
            else:
                self._port_combo.addItem("未找到串口设备")
                self.add_log("WARNING", "未检测到可用串口")
        except Exception as e:
            self.add_log("ERROR", f"刷新串口列表失败: {str(e)}")
    
    def closeEvent(self, event):
        """窗口关闭事件处理"""
        if self._serial_connected:
            self._disconnect_serial()
        event.accept()
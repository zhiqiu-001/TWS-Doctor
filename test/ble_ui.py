import sys
import re
import threading
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QTextEdit, QLabel, QMessageBox, QGroupBox, QGridLayout, QSplitter,
    QStatusBar, QFrame
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QAbstractItemView

import serial
import serial.tools.list_ports


class SerialWorker(QObject):
    data_received = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.running = False

    def open_port(self, port_name, baud=115200):
        if self.serial_port and self.serial_port.is_open:
            self.close_port()
        try:
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.1
            )
            self.running = True
            self.connected.emit()
            threading.Thread(target=self._read_loop, daemon=True).start()
        except Exception as e:
            self.error_occurred.emit(f"Failed to open port: {str(e)}")

    def close_port(self):
        self.running = False
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
            except:
                pass
        self.disconnected.emit()

    def send_command(self, cmd):
        if self.serial_port and self.serial_port.is_open:
            try:
                full_cmd = cmd.strip() + '\n'
                self.serial_port.write(full_cmd.encode())
            except Exception as e:
                self.error_occurred.emit(f"Send failed: {str(e)}")

    def _read_loop(self):
        buffer = ""
        while self.running:
            try:
                if self.serial_port and self.serial_port.is_open:
                    data = self.serial_port.read(1024)
                    if data:
                        try:
                            text = data.decode('utf-8', errors='replace')
                            buffer += text
                            while '\n' in buffer:
                                line, buffer = buffer.split('\n', 1)
                                line = line.strip('\r').strip()
                                if line:
                                    self.data_received.emit(line)
                        except:
                            pass
                    else:
                        import time
                        time.sleep(0.01)
                else:
                    import time
                    time.sleep(0.1)
            except Exception as e:
                self.error_occurred.emit(f"Read error: {str(e)}")
                break


class BLEUIController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = SerialWorker()
        self.devices = {}
        self.device_rows = {}

        self.worker.data_received.connect(self._on_data)
        self.worker.error_occurred.connect(self._on_error)
        self.worker.connected.connect(self._on_connected)
        self.worker.disconnected.connect(self._on_disconnected)

        self._init_ui()
        self._refresh_ports()

    def _init_ui(self):
        self.setWindowTitle("ESP32-S3 BLE Security Client Controller")
        self.setMinimumSize(900, 650)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # Serial port group
        serial_group = QGroupBox("Serial Port")
        serial_layout = QGridLayout(serial_group)

        self.port_combo = QComboBox()
        self.port_combo.setMinimumWidth(250)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self._refresh_ports)

        self.open_btn = QPushButton("Open Port")
        self.open_btn.clicked.connect(self._toggle_port)
        self.open_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")

        serial_layout.addWidget(QLabel("Port:"), 0, 0)
        serial_layout.addWidget(self.port_combo, 0, 1)
        serial_layout.addWidget(self.refresh_btn, 0, 2)
        serial_layout.addWidget(self.open_btn, 0, 3)
        serial_layout.setColumnStretch(1, 1)

        main_layout.addWidget(serial_group)

        # Scan control group
        scan_group = QGroupBox("BLE Scan Control")
        scan_layout = QHBoxLayout(scan_group)

        self.scan_btn = QPushButton("Start Scan")
        self.scan_btn.clicked.connect(self._toggle_scan)
        self.scan_btn.setEnabled(False)
        self.scan_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")

        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self._disconnect_device)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 8px;")

        self.conn_status_label = QLabel("Status: Not connected")
        self.conn_status_label.setStyleSheet("color: gray; font-weight: bold;")

        scan_layout.addWidget(self.scan_btn)
        scan_layout.addWidget(self.disconnect_btn)
        scan_layout.addStretch()
        scan_layout.addWidget(self.conn_status_label)

        main_layout.addWidget(scan_group)

        # Device table
        table_group = QGroupBox("Discovered BLE Devices")
        table_layout = QVBoxLayout(table_group)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(5)
        self.device_table.setHorizontalHeaderLabels(["Addr Type", "Address", "RSSI", "Name", "Action"])
        self.device_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.device_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.device_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.device_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.device_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.device_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.device_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        table_layout.addWidget(self.device_table)
        main_layout.addWidget(table_group)

        # Log area
        log_group = QGroupBox("Event Log")
        log_layout = QVBoxLayout(log_group)

        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont("Consolas", 9))
        self.log_area.setMaximumHeight(200)

        log_layout.addWidget(self.log_area)

        # Clear log button
        log_btn_layout = QHBoxLayout()
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.log_area.clear)
        log_btn_layout.addStretch()
        log_btn_layout.addWidget(clear_log_btn)
        log_layout.addLayout(log_btn_layout)

        main_layout.addWidget(log_group)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _log(self, message, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "info": "black",
            "error": "red",
            "warn": "orange",
            "success": "green",
            "data": "blue",
            "device": "purple"
        }
        color = color_map.get(level, "black")
        self.log_area.append(f'<span style="color: {color};"><b>[{timestamp}]</b> {message}</span>')
        self.status_bar.showMessage(message, 5000)

    def _refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        if not ports:
            self.port_combo.addItem("No ports found")
        else:
            for p in sorted(ports):
                self.port_combo.addItem(f"{p.device} - {p.description}")
        self._log("Port list refreshed", "info")

    def _toggle_port(self):
        if self.worker.serial_port and self.worker.serial_port.is_open:
            self.worker.close_port()
        else:
            text = self.port_combo.currentText()
            if text and "No ports" not in text:
                port_name = text.split(" - ")[0]
                self.worker.open_port(port_name)
            else:
                QMessageBox.warning(self, "Error", "Please select a valid serial port")

    def _toggle_scan(self):
        if self.scan_btn.text() == "Start Scan":
            self.worker.send_command("AT+SCAN")
            self._log("Scan command sent", "info")
        else:
            self.worker.send_command("AT+SCANSTOP")
            self._log("Stop scan command sent", "info")

    def _disconnect_device(self):
        self.worker.send_command("AT+DISCONNECT")
        self._log("Disconnect command sent", "info")

    def _connect_to_device(self, addr_type, addr):
        self.worker.send_command(f"AT+CONNECT={addr_type},{addr}")
        self._log(f"Connecting to {addr}...", "info")

    def _on_connected(self):
        self.open_btn.setText("Close Port")
        self.open_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold;")
        self.scan_btn.setEnabled(True)
        self._log("Serial port opened successfully", "success")

    def _on_disconnected(self):
        self.open_btn.setText("Open Port")
        self.open_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        self.scan_btn.setText("Start Scan")
        self.scan_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(False)
        self.conn_status_label.setText("Status: Not connected")
        self.conn_status_label.setStyleSheet("color: gray; font-weight: bold;")
        self._log("Serial port closed", "warn")

    def _on_error(self, msg):
        self._log(msg, "error")

    def _on_data(self, line):
        if line.startswith("[DEVICE]"):
            self._handle_device(line)
        elif line.startswith("[SCAN]"):
            self._handle_scan(line)
        elif line.startswith("[CONNECTED]"):
            self._handle_connected(line)
        elif line.startswith("[OPEN]"):
            self._log(line, "success")
        elif line.startswith("[DISCONNECTED]"):
            self._handle_disconnected(line)
        elif line.startswith("[NOTIFY]"):
            self._log(line, "data")
        elif line.startswith("[AUTH_OK]"):
            self._log(f"Authentication successful: {line}", "success")
        elif line.startswith("[AUTH_FAIL]"):
            self._log(f"Authentication failed: {line}", "error")
        elif line.startswith("[ERROR]"):
            self._log(line, "error")
        elif line.startswith("[INIT]"):
            self._log(line, "success")
        elif line.startswith("[HELP]"):
            self._log(line, "info")
        elif line.strip():
            self._log(line, "info")

    def _handle_scan(self, line):
        if "started" in line.lower():
            self.scan_btn.setText("Stop Scan")
            self.scan_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold; padding: 8px;")
            self.devices.clear()
            self.device_rows.clear()
            self.device_table.setRowCount(0)
            self._log("BLE scanning started", "success")
        elif "stopped" in line.lower():
            self.scan_btn.setText("Start Scan")
            self.scan_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold; padding: 8px;")
            self._log("BLE scanning stopped", "warn")

    def _handle_device(self, line):
        # Parse: [DEVICE] addr_type=0 addr=7c:df:a1:40:01:dd rssi=-45 name=ESP_BLE50_SERVER
        pattern = r'\[DEVICE\] addr_type=(\d+) addr=([\da-fA-F:]+) rssi=(-?\d+) name=(.*)'
        match = re.match(pattern, line)
        if match:
            addr_type = match.group(1)
            addr = match.group(2).lower()
            rssi = int(match.group(3))
            name = match.group(4).strip()

            if addr in self.devices:
                row = self.device_rows[addr]
                self.devices[addr] = (addr_type, addr, rssi, name)
                self.device_table.setItem(row, 2, QTableWidgetItem(str(rssi)))
                if name:
                    self.device_table.setItem(row, 3, QTableWidgetItem(name))
            else:
                row = self.device_table.rowCount()
                self.device_table.insertRow(row)
                self.devices[addr] = (addr_type, addr, rssi, name)
                self.device_rows[addr] = row

                self.device_table.setItem(row, 0, QTableWidgetItem(addr_type))
                self.device_table.setItem(row, 1, QTableWidgetItem(addr))
                self.device_table.setItem(row, 2, QTableWidgetItem(str(rssi)))
                self.device_table.setItem(row, 3, QTableWidgetItem(name if name else "(no name)"))

                connect_btn = QPushButton("Connect")
                connect_btn.setStyleSheet(
                    "background-color: #4CAF50; color: white; font-weight: bold; padding: 4px 12px;"
                )
                connect_btn.clicked.connect(
                    lambda checked, t=addr_type, a=addr: self._connect_to_device(t, a)
                )
                self.device_table.setCellWidget(row, 4, connect_btn)

            # Update RSSI coloring
            rssi_item = self.device_table.item(row, 2)
            if rssi_item:
                if rssi >= -50:
                    rssi_item.setForeground(QColor("green"))
                elif rssi >= -70:
                    rssi_item.setForeground(QColor("orange"))
                else:
                    rssi_item.setForeground(QColor("red"))

            self._log(f"Found: {addr} ({name}) RSSI={rssi}", "device")

    def _handle_connected(self, line):
        # Parse: [CONNECTED] conn_id=0 addr=7c:df:a1:40:01:dd
        pattern = r'\[CONNECTED\] conn_id=(\d+) addr=([\da-fA-F:]+)'
        match = re.match(pattern, line)
        if match:
            addr = match.group(2).lower()
            self.conn_status_label.setText(f"Status: Connected to {addr}")
            self.conn_status_label.setStyleSheet("color: green; font-weight: bold;")
            self.disconnect_btn.setEnabled(True)
            self.scan_btn.setEnabled(False)
            self._log(f"Connected to {addr}", "success")
            self._disable_connect_buttons()

    def _handle_disconnected(self, line):
        self.conn_status_label.setText("Status: Disconnected")
        self.conn_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.disconnect_btn.setEnabled(False)
        self.scan_btn.setEnabled(True)
        self._log("Device disconnected", "warn")
        self._enable_connect_buttons()

    def _disable_connect_buttons(self):
        for row in range(self.device_table.rowCount()):
            widget = self.device_table.cellWidget(row, 4)
            if widget:
                widget.setEnabled(False)

    def _enable_connect_buttons(self):
        for row in range(self.device_table.rowCount()):
            widget = self.device_table.cellWidget(row, 4)
            if widget:
                widget.setEnabled(True)

    def closeEvent(self, event):
        self.worker.close_port()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BLEUIController()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
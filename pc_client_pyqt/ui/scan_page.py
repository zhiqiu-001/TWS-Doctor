from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QSpinBox, QLabel
)
from PyQt6.QtCore import pyqtSignal
from core.device_manager import DeviceManager, Device


class ScanPage(QWidget):
    scan_start = pyqtSignal(int)
    scan_stop = pyqtSignal()
    
    def __init__(self, device_manager: DeviceManager):
        super().__init__()
        self.device_manager = device_manager
        self.scanning = False
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QWidget()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        # 扫描数量设置
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("扫描数量:"))
        self.count_spin = QSpinBox()
        self.count_spin.setRange(0, 100)
        self.count_spin.setValue(10)
        self.count_spin.setToolTip("设置为0表示不限制数量")
        count_layout.addWidget(self.count_spin)
        toolbar_layout.addLayout(count_layout)
        
        toolbar_layout.addStretch()
        
        # 扫描控制按钮
        self.scan_btn = QPushButton("开始扫描")
        self.scan_btn.setCheckable(True)
        toolbar_layout.addWidget(self.scan_btn)
        
        self.clear_btn = QPushButton("清空列表")
        toolbar_layout.addWidget(self.clear_btn)
        
        layout.addWidget(toolbar)
        
        # 设备列表
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["设备名称", "MAC地址", "信号强度", "类型"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        
        layout.addWidget(self.table)
    
    def _connect_signals(self):
        self.device_manager.device_added.connect(self._on_device_added)
        self.device_manager.device_updated.connect(self._on_device_updated)
        self.device_manager.cleared.connect(self._on_cleared)
        self.clear_btn.clicked.connect(self.device_manager.clear)
        self.scan_btn.clicked.connect(self._on_scan_clicked)
    
    def set_scanning(self, scanning: bool):
        """设置扫描状态"""
        self.scanning = scanning
        self.scan_btn.setChecked(scanning)
        self.scan_btn.setText("停止扫描" if scanning else "开始扫描")
        self.count_spin.setEnabled(not scanning)
        self.clear_btn.setEnabled(not scanning)
    
    def _on_scan_clicked(self):
        if self.scanning:
            self.scan_stop.emit()
        else:
            count = self.count_spin.value()
            self.scan_start.emit(count)
    
    def _on_device_added(self, device: Device):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self._update_row(row, device)
    
    def _on_device_updated(self, device: Device):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 1).text() == device.addr:
                self._update_row(row, device)
                break
    
    def _update_row(self, row: int, device: Device):
        self.table.setItem(row, 0, QTableWidgetItem(device.name))
        self.table.setItem(row, 1, QTableWidgetItem(device.addr))
        self.table.setItem(row, 2, QTableWidgetItem(f"{device.rssi} dBm"))
        self.table.setItem(row, 3, QTableWidgetItem(device.type))
    
    def _on_cleared(self):
        self.table.setRowCount(0)

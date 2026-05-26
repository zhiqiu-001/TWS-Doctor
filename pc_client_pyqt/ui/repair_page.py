from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QGroupBox, QProgressBar
)
from PyQt6.QtCore import Qt
from core.repair_manager import RepairManager, RepairState


class RepairPage(QWidget):
    def __init__(self, repair_manager: RepairManager):
        super().__init__()
        self.repair_manager = repair_manager
        self._init_ui()
        self._connect_signals()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        status_group = QGroupBox("修复状态")
        status_layout = QVBoxLayout(status_group)
        
        self.state_label = QLabel("状态: 空闲")
        self.state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.state_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        status_layout.addWidget(self.state_label)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        status_layout.addWidget(self.progress)
        
        layout.addWidget(status_group)
        
        control_group = QGroupBox("修复操作")
        control_layout = QVBoxLayout(control_group)
        
        self.start_btn = QPushButton("开始修复")
        self.start_btn.setMinimumHeight(50)
        self.start_btn.setStyleSheet("font-size: 16px;")
        control_layout.addWidget(self.start_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setEnabled(False)
        control_layout.addWidget(self.reset_btn)
        
        control_layout.addStretch()
        layout.addWidget(control_group)
        
        layout.addStretch()
    
    def _connect_signals(self):
        self.start_btn.clicked.connect(self._on_start_repair)
        self.reset_btn.clicked.connect(self._on_reset)
        self.repair_manager.state_changed.connect(self._on_state_changed)
    
    def _on_start_repair(self):
        self.repair_manager.start_repair()
    
    def _on_reset(self):
        self.repair_manager.reset()
    
    def _on_state_changed(self, state: RepairState):
        if state == RepairState.IDLE:
            self.state_label.setText("状态: 空闲")
            self.state_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #aaa;")
            self.progress.setVisible(False)
            self.start_btn.setEnabled(True)
            self.reset_btn.setEnabled(False)
        elif state == RepairState.REPAIRING:
            self.state_label.setText("状态: 修复中...")
            self.state_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #4fc3f7;")
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)
            self.start_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
        elif state == RepairState.SUCCESS:
            self.state_label.setText("状态: 修复成功!")
            self.state_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #66bb6a;")
            self.progress.setVisible(False)
            self.start_btn.setEnabled(False)
            self.reset_btn.setEnabled(True)
        elif state == RepairState.FAILED:
            self.state_label.setText("状态: 修复失败")
            self.state_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #ef5350;")
            self.progress.setVisible(False)
            self.start_btn.setEnabled(False)
            self.reset_btn.setEnabled(True)

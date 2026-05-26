from PyQt6.QtCore import QObject, pyqtSignal
from enum import Enum


class RepairState(Enum):
    IDLE = "IDLE"
    REPAIRING = "REPAIRING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class RepairManager(QObject):
    state_changed = pyqtSignal(RepairState)
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.state = RepairState.IDLE
    
    def start_repair(self):
        self.state = RepairState.REPAIRING
        self.state_changed.emit(self.state)
        self.log_message.emit("Starting repair process...")
    
    def repair_success(self):
        self.state = RepairState.SUCCESS
        self.state_changed.emit(self.state)
        self.log_message.emit("Repair successful!")
    
    def repair_failed(self, reason: str):
        self.state = RepairState.FAILED
        self.state_changed.emit(self.state)
        self.log_message.emit(f"Repair failed: {reason}")
    
    def reset(self):
        self.state = RepairState.IDLE
        self.state_changed.emit(self.state)

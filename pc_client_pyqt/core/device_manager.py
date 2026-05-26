from PyQt6.QtCore import QObject, pyqtSignal
from dataclasses import dataclass
from typing import Dict


@dataclass
class Device:
    name: str
    addr: str
    rssi: int
    type: str


class DeviceManager(QObject):
    device_added = pyqtSignal(Device)
    device_updated = pyqtSignal(Device)
    cleared = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.devices: Dict[str, Device] = {}
    
    def add_device(self, name: str, addr: str, rssi: int, device_type: str):
        if addr in self.devices:
            device = self.devices[addr]
            device.rssi = rssi
            device.name = name
            self.device_updated.emit(device)
        else:
            device = Device(name, addr, rssi, device_type)
            self.devices[addr] = device
            self.device_added.emit(device)
    
    def clear(self):
        self.devices.clear()
        self.cleared.emit()
    
    def get_all_devices(self):
        return list(self.devices.values())

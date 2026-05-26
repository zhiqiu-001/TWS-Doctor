from PyQt6.QtCore import QObject
from core.protocol import PacketType
from core.device_manager import DeviceManager
from core.repair_manager import RepairManager


class PacketParser(QObject):
    def __init__(self, device_manager: DeviceManager, repair_manager: RepairManager):
        super().__init__()
        self.device_manager = device_manager
        self.repair_manager = repair_manager
    
    def handle_packet(self, packet_type, data):
        if packet_type == PacketType.SCAN_BLE:
            self.device_manager.add_device(
                data["name"],
                data["addr"],
                data["rssi"],
                "BLE"
            )
        elif packet_type == PacketType.SCAN_CLASSIC:
            self.device_manager.add_device(
                data["name"],
                data["addr"],
                data["rssi"],
                "CLASSIC"
            )
        elif packet_type == PacketType.REPAIR_START:
            self.repair_manager.start_repair()
        elif packet_type == PacketType.REPAIR_SUCCESS:
            self.repair_manager.repair_success()
        elif packet_type == PacketType.REPAIR_FAILED:
            self.repair_manager.repair_failed(data["reason"] if data else "Unknown")

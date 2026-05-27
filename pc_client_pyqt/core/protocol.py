from enum import Enum


class PacketType(Enum):
    SCAN_BLE = "SCAN|BLE"
    SCAN_CLASSIC = "SCAN|CLASSIC"
    REPAIR_START = "REPAIR|START"
    REPAIR_SUCCESS = "REPAIR|SUCCESS"
    REPAIR_FAILED = "REPAIR|FAILED"
    STATUS_SCANNING = "STATUS|SCANNING"
    STATUS_IDLE = "STATUS|IDLE"
    
    # Bose TWS 辅助工具相关
    BOSE_CONNECTED = "BOSE|CONNECTED"
    BOSE_DISCONNECTED = "BOSE|DISCONNECTED"
    BOSE_BATTERY = "BOSE|BATT"
    BOSE_FIRMWARE = "BOSE|FW"
    BOSE_CLEAR_PAIRING = "BOSE|CLEAR_PAIRING"
    BOSE_ERROR = "BOSE|ERROR"
    
    UNKNOWN = "UNKNOWN"


def parse_packet(data: str):
    data = data.strip()
    if not data:
        return None, None
    
    if data.startswith("SCAN|BLE|"):
        parts = data.split("|")
        if len(parts) >= 5:
            return PacketType.SCAN_BLE, {
                "name": parts[2],
                "addr": parts[3],
                "rssi": int(parts[4])
            }
    elif data.startswith("SCAN|CLASSIC|"):
        parts = data.split("|")
        if len(parts) >= 5:
            return PacketType.SCAN_CLASSIC, {
                "name": parts[2],
                "addr": parts[3],
                "rssi": int(parts[4])
            }
    elif data.startswith("REPAIR|START"):
        return PacketType.REPAIR_START, None
    elif data.startswith("REPAIR|SUCCESS"):
        return PacketType.REPAIR_SUCCESS, None
    elif data.startswith("REPAIR|FAILED|"):
        parts = data.split("|")
        reason = parts[2] if len(parts) >= 3 else "Unknown"
        return PacketType.REPAIR_FAILED, {"reason": reason}
    elif data.startswith("STATUS|SCANNING|"):
        parts = data.split("|")
        count = int(parts[2]) if len(parts) >= 3 else 0
        return PacketType.STATUS_SCANNING, {"count": count}
    elif data.startswith("STATUS|IDLE"):
        return PacketType.STATUS_IDLE, None
    
    # Bose TWS 辅助工具协议
    elif data.startswith("BOSE|CONNECTED|"):
        parts = data.split("|")
        if len(parts) >= 4:
            return PacketType.BOSE_CONNECTED, {
                "name": parts[2],
                "model": parts[3] if len(parts) >= 4 else ""
            }
    elif data.startswith("BOSE|DISCONNECTED"):
        return PacketType.BOSE_DISCONNECTED, None
    elif data.startswith("BOSE|BATT|"):
        parts = data.split("|")
        if len(parts) >= 4:
            return PacketType.BOSE_BATTERY, {
                "left": int(parts[2]),
                "right": int(parts[3])
            }
    elif data.startswith("BOSE|FW|"):
        parts = data.split("|")
        if len(parts) >= 3:
            return PacketType.BOSE_FIRMWARE, {
                "version": parts[2],
                "model": parts[3] if len(parts) >= 4 else ""
            }
    elif data.startswith("BOSE|CLEAR_PAIRING|"):
        parts = data.split("|")
        success = parts[2] == "OK" if len(parts) >= 3 else False
        return PacketType.BOSE_CLEAR_PAIRING, {"success": success}
    elif data.startswith("BOSE|ERROR|"):
        parts = data.split("|")
        error_msg = parts[2] if len(parts) >= 3 else "Unknown error"
        return PacketType.BOSE_ERROR, {"message": error_msg}
    
    return PacketType.UNKNOWN, data

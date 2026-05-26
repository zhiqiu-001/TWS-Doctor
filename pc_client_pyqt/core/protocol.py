from enum import Enum


class PacketType(Enum):
    SCAN_BLE = "SCAN|BLE"
    SCAN_CLASSIC = "SCAN|CLASSIC"
    REPAIR_START = "REPAIR|START"
    REPAIR_SUCCESS = "REPAIR|SUCCESS"
    REPAIR_FAILED = "REPAIR|FAILED"
    STATUS_SCANNING = "STATUS|SCANNING"
    STATUS_IDLE = "STATUS|IDLE"
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
    
    return PacketType.UNKNOWN, data

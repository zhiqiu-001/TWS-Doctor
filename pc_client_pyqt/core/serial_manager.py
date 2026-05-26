import serial
import serial.tools.list_ports
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from typing import Optional
from core.protocol import parse_packet


class SerialManager(QObject):
    data_received = pyqtSignal(object, object)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    error = pyqtSignal(str)
    log_message = pyqtSignal(str)  # 日志消息信号
    
    def __init__(self):
        super().__init__()
        self.serial: Optional[serial.Serial] = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._read_data)
    
    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port: str, baudrate: int = 115200):
        try:
            if self.serial and self.serial.is_open:
                self.disconnect()
            
            self.log_message.emit(f"打开串口: {port}, 波特率: {baudrate}")
            self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=0.1
            )
            self.log_message.emit("串口打开成功")
            
            # 立即读取缓冲区中可能存在的数据（ESP32可能已经发送了一些数据）
            self._read_data()
            
            self.timer.start(10)
            self.log_message.emit("开始监听串口数据...")
            self.connected.emit()
            return True
        except Exception as e:
            self.log_message.emit(f"连接失败: {str(e)}")
            self.error.emit(str(e))
            return False
    
    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.log_message.emit("关闭串口连接...")
            self.timer.stop()
            self.serial.close()
            self.serial = None
            self.log_message.emit("串口已关闭")
            self.disconnected.emit()
    
    def is_connected(self) -> bool:
        return self.serial is not None and self.serial.is_open
    
    def send_command(self, command: str):
        """发送命令到ESP32"""
        if self.serial and self.serial.is_open:
            try:
                self.log_message.emit(f"发送命令: {command}")
                self.serial.write((command + "\n").encode('utf-8'))
                return True
            except Exception as e:
                self.log_message.emit(f"发送失败: {str(e)}")
                self.error.emit(f"Send error: {str(e)}")
                return False
        return False
    
    def send_scan_start(self, count_limit: int = 0):
        """发送开始扫描命令"""
        command = f"CMD|SCAN_START|{count_limit}"
        return self.send_command(command)
    
    def send_scan_stop(self):
        """发送停止扫描命令"""
        return self.send_command("CMD|SCAN_STOP")
    
    def send_repair_start(self, target_addr: str):
        """发送开始修复命令"""
        command = f"CMD|REPAIR_START|{target_addr}"
        return self.send_command(command)
    
    def send_repair_stop(self):
        """发送停止修复命令"""
        return self.send_command("CMD|REPAIR_STOP")
    
    def _read_data(self):
        if self.serial and self.serial.is_open:
            try:
                while self.serial.in_waiting > 0:
                    line = self.serial.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        # 记录所有收到的数据到日志（包括ESP32启动日志、调试信息等）
                        self.log_message.emit(f"[ESP32] {line}")
                        # 尝试解析协议包
                        try:
                            packet_type, data = parse_packet(line)
                            if packet_type:
                                self.data_received.emit(packet_type, data)
                        except:
                            # 非协议格式的数据不做解析，只记录日志
                            pass
            except Exception as e:
                self.log_message.emit(f"读取错误: {str(e)}")
                self.error.emit(f"Read error: {str(e)}")

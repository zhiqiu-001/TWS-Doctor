# 硬件说明

## 支持的芯片

### ESP32-S3
- **支持：** BLE（低功耗蓝牙）
- **不支持：** 经典蓝牙（BR/EDR）
- **适用场景：** BLE TWS 耳机修复

### ESP32-WROOM（推荐）
- **支持：** BLE + 经典蓝牙
- **适用场景：** 所有类型的 TWS 耳机修复

## 引脚配置

### UART 通信
- TX: GPIO 1
- RX: GPIO 3
- 波特率: 115200

## 硬件连接

ESP32 通过 USB 串口连接到 PC，用于：
1. 固件烧录
2. 与上位机通信

## 编译和烧录

### 进入 firmware 目录
```bash
cd firmware_esp32s3
```

### 编译固件
```bash
idf.py build
```

### 烧录固件
```bash
idf.py flash
```

### 监控日志
```bash
idf.py monitor
```

# ESP32_TWS_Doctor

TWS 蓝牙耳机修复工具，基于 ESP32-S3 和 PyQt6。

## 目录结构

```
ESP32_TWS_Doctor/
├── README.md
├── LICENSE
├── .gitignore
├── docs/
│   ├── protocol.md
│   ├── tws_flow.md
│   ├── hardware.md
│   └── screenshots/
├── firmware_esp32s3/
│   ├── CMakeLists.txt
│   ├── sdkconfig
│   ├── partitions.csv
│   ├── main/
│   ├── components/
│   └── managed_components/
├── pc_client_pyqt/
│   ├── main.py
│   ├── requirements.txt
│   ├── ui/
│   ├── core/
│   └── assets/
└── tools/
```

## 快速开始

### 固件编译与烧录

```bash
cd firmware_esp32s3
idf.py build
idf.py flash monitor
```

### 上位机运行

```bash
cd pc_client_pyqt
pip install -r requirements.txt
python main.py
```

## 硬件说明

**注意**: 本项目使用 ESP32-S3，仅支持 BLE，不支持经典蓝牙。

对于经典蓝牙 TWS 的修复，建议使用 ESP32-WROOM。

## 文档

- [串口协议](docs/protocol.md)
- [TWS修复流程](docs/tws_flow.md)
- [硬件说明](docs/hardware.md)

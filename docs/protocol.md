# 串口协议文档

## 概述

ESP32 与 PC 上位机通过 UART 进行通信，波特率 115200。

## 协议格式

所有消息使用简单的管道符（|）分隔格式：

```
TYPE|SUBTYPE|PARAM1|PARAM2|...\n
```

## ESP32 → PC 消息

### SCAN|BLE 消息

BLE 扫描结果：

```
SCAN|BLE|<设备名称>|<MAC地址>|<信号强度>
```

示例：
```
SCAN|BLE|AirPods-L|AA:BB:CC:DD:EE:FF|-45
```

### SCAN|CLASSIC 消息

经典蓝牙扫描结果（ESP32-S3 不支持）：

```
SCAN|CLASSIC|<设备名称>|<MAC地址>|<信号强度>
```

示例：
```
SCAN|CLASSIC|QCY-T13|11:22:33:44:55:66|-60
```

### REPAIR|START 消息

修复过程开始：

```
REPAIR|START
```

### REPAIR|SUCCESS 消息

修复成功：

```
REPAIR|SUCCESS
```

### REPAIR|FAILED 消息

修复失败，带原因：

```
REPAIR|FAILED|<失败原因>
```

示例：
```
REPAIR|FAILED|Device not found
```

## PC → ESP32 消息

（待补充）

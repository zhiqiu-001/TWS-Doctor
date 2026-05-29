/**
 * @file uart_protocol.h
 * @brief 串口协议模块头文件
 * 
 * 支持两种协议格式：
 * 1. CMD| 格式（原有）：CMD|SCAN_START|..., CMD|BOSE_CONNECT|...
 * 2. AT+ 格式（兼容 test 代码）：AT+SCAN, AT+CONNECT=type,addr, AT+DISCONNECT
 * 
 * 上位机 ← ESP32 消息:
 * - SCAN|BLE|设备名称|MAC地址|ADDR_TYPE|RSSI    （原有）
 * - [DEVICE] addr_type=0 addr=xx:xx:... rssi=-45 name=xxx （test 兼容）
 * - [SCAN] Scanning started / [SCAN] Scanning stopped
 * - [CONNECTED] conn_id=0 addr=xx:xx:...
 * - [OPEN] ESP_GATTC_OPEN_EVT status=0
 * - [DISCONNECTED] reason=0x...
 * - [NOTIFY] handle=0xXXXX value=XX XX ...
 * - [AUTH_OK] / [AUTH_FAIL] reason=...
 * - [ERROR] ...
 * - [INIT] ...
 * - [HELP] ...
 * - BOSE|CONNECTED|名称|型号    （原有）
 * - BOSE|DISCONNECTED            （原有）
 * - BOSE|BATT|左|右              （原有）
 * - BOSE|FW|版本|型号            （原有）
 * - LOG|标签|内容                （原有）
 * 
 * 上位机 → ESP32 命令:
 * - AT+SCAN                        （兼容 test）
 * - AT+SCANSTOP                    （兼容 test）
 * - AT+CONNECT=type,addr           （兼容 test，如 AT+CONNECT=0,7c:df:a1:40:01:dd）
 * - AT+DISCONNECT                  （兼容 test）
 * - AT+HELP                        （兼容 test）
 * - CMD|SCAN_START|数量             （原有）
 * - CMD|SCAN_STOP                   （原有）
 * - CMD|BOSE_CONNECT|MAC|type|name  （原有）
 * - CMD|BOSE_DISCONNECT             （原有）
 * - （其他原有 CMD| 命令保持不变）
 */

#ifndef UART_PROTOCOL_H
#define UART_PROTOCOL_H

#include <stdbool.h>
#include <stdint.h>
#include "esp_err.h"
#include "esp_gap_ble_api.h"

/**
 * @brief 串口命令类型枚举
 */
typedef enum {
    CMD_SCAN_START,         /*!< 开始扫描命令 */
    CMD_SCAN_STOP,          /*!< 停止扫描命令 */
    CMD_REPAIR_START,       /*!< 开始修复命令 */
    CMD_REPAIR_STOP,        /*!< 停止修复命令 */
    CMD_GATTC_CONNECT,      /*!< GATTC 连接命令 */
    CMD_GATTC_DISCONNECT,   /*!< GATTC 断开命令 */
    CMD_GATTC_READ,         /*!< GATTC 读取命令 */
    CMD_GATTC_WRITE,        /*!< GATTC 写入命令 */
    CMD_GATTC_NOTIFY,       /*!< GATTC Notify 设置命令 */
    CMD_BOSE_CONNECT,       /*!< Bose 设备连接命令 */
    CMD_BOSE_DISCONNECT,    /*!< Bose 设备断开命令 */
    CMD_BOSE_CLEAR_PAIRING, /*!< Bose 清空配对命令 */
    CMD_BOSE_READ_BATT,     /*!< Bose 读取电池命令 */
    CMD_BOSE_READ_FW,       /*!< Bose 读取固件命令 */
    CMD_AT_SCAN,            /*!< AT+SCAN 命令 */
    CMD_AT_SCANSTOP,        /*!< AT+SCANSTOP 命令 */
    CMD_AT_CONNECT,         /*!< AT+CONNECT=type,addr 命令 */
    CMD_AT_DISCONNECT,      /*!< AT+DISCONNECT 命令 */
    CMD_AT_HELP,            /*!< AT+HELP 命令 */
    CMD_PING,               /*!< 握手/探活命令，重新发送 [INIT] */
    CMD_UNKNOWN             /*!< 未知命令 */
} uart_cmd_t;

/**
 * @brief 命令参数结构体
 */
typedef struct {
    int scan_count;        /*!< 扫描数量限制，0表示不限制 */
    char target_addr[18];  /*!< 目标设备MAC地址 */
    uint8_t addr_type;     /*!< BLE 地址类型 */
} uart_cmd_params_t;

/**
 * @brief 串口命令回调函数类型
 * @param cmd 命令类型
 * @param params 命令参数
 */
typedef void (*uart_cmd_callback_t)(uart_cmd_t cmd, uart_cmd_params_t *params);

/* ======================== 初始化 ======================== */

/**
 * @brief 初始化串口协议模块
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_init(void);

/**
 * @brief 设置命令回调函数
 * @param callback 回调函数指针
 */
void uart_protocol_set_callback(uart_cmd_callback_t callback);

/* ======================== 原始 CMD| 格式输出（保留） ======================== */

esp_err_t uart_protocol_send_ble_scan_result(const char *name, const char *addr, uint8_t addr_type, int rssi);
esp_err_t uart_protocol_send_bt_classic_scan_result(const char *name, const char *addr, int rssi);
esp_err_t uart_protocol_send_repair_start(void);
esp_err_t uart_protocol_send_repair_success(void);
esp_err_t uart_protocol_send_repair_failed(const char *reason);
esp_err_t uart_protocol_send_log(const char *tag, const char *message);
esp_err_t uart_protocol_send_scan_status(bool scanning, int count);
esp_err_t uart_protocol_send_bose_connected(const char *name, const char *model);
esp_err_t uart_protocol_send_bose_disconnected(void);
esp_err_t uart_protocol_send_bose_battery(int left_level, int right_level);
esp_err_t uart_protocol_send_bose_firmware(const char *version, const char *model);
esp_err_t uart_protocol_send_bose_clear_pairing(bool success);
esp_err_t uart_protocol_send_bose_error(const char *message);

/* ======================== test 兼容 [xxx] 格式输出 ======================== */

/**
 * @brief 发送 [DEVICE] 格式的设备发现消息
 * @param addr_type 地址类型（0=public, 1=random）
 * @param addr MAC地址字符串，如 "7c:df:a1:40:01:dd"
 * @param rssi 信号强度，如 -45
 * @param name 设备名称，如 "ESP_BLE50_SERVER"
 */
esp_err_t uart_protocol_send_device_found(uint8_t addr_type, const char *addr, int rssi, const char *name);

/**
 * @brief 发送 [SCAN] 格式的扫描状态消息
 * @param started true=扫描已开始, false=扫描已停止
 */
esp_err_t uart_protocol_send_scan_msg(bool started);

/**
 * @brief 发送 [CONNECTED] 格式的连接成功消息
 * @param conn_id 连接ID
 * @param addr 设备MAC地址
 */
esp_err_t uart_protocol_send_connected_msg(int conn_id, const char *addr);

/**
 * @brief 发送 [OPEN] 格式的 GATT open 事件消息
 * @param status 状态码
 */
esp_err_t uart_protocol_send_open_msg(int status);

/**
 * @brief 发送 [DISCONNECTED] 格式的断开消息
 * @param reason 断开原因（0x16=正常断开）
 */
esp_err_t uart_protocol_send_disconnected_msg(int reason);

/**
 * @brief 发送 [NOTIFY] 格式的通知消息
 * @param handle 特征值句柄
 * @param value 数据
 * @param value_len 数据长度
 */
esp_err_t uart_protocol_send_notify_msg(uint16_t handle, const uint8_t *value, uint16_t value_len);

/**
 * @brief 发送 [AUTH_OK] 验证成功消息
 * @param info 额外信息（可选）
 */
esp_err_t uart_protocol_send_auth_ok(const char *info);

/**
 * @brief 发送 [AUTH_FAIL] 验证失败消息
 * @param reason 失败原因
 */
esp_err_t uart_protocol_send_auth_fail(const char *reason);

/**
 * @brief 发送 [ERROR] 错误消息
 */
esp_err_t uart_protocol_send_error_msg(const char *message);

/**
 * @brief 发送 [INIT] 初始化完成消息
 */
esp_err_t uart_protocol_send_init_msg(const char *message);

/**
 * @brief 发送 [HELP] 帮助信息
 */
esp_err_t uart_protocol_send_help(void);

#endif /* UART_PROTOCOL_H */
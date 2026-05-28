/**
 * @file uart_protocol.h
 * @brief 串口协议模块头文件
 * 
 * 该模块负责ESP32与PC上位机之间的串口通信协议，
 * 定义了数据格式和通信命令。
 * 
 * 协议格式: TYPE|SUBTYPE|PARAM1|PARAM2|...\n
 * 
 * ESP32 → PC 消息:
 * - LOG|标签|消息内容
 * - SCAN|BLE|设备名称|MAC地址|RSSI
 * - SCAN|CLASSIC|设备名称|MAC地址|RSSI
 * - REPAIR|START
 * - REPAIR|SUCCESS
 * - REPAIR|FAILED|原因
 * - STATUS|SCANNING|数量
 * - STATUS|IDLE
 * - GATTC|CONNECTED
 * - GATTC|DISCONNECTED
 * - GATTC|SERVICE|UUID
 * - GATTC|CHAR|UUID|PROPS
 * - BOSE|CONNECTED|设备名称|设备型号
 * - BOSE|DISCONNECTED
 * - BOSE|BATT|左耳电量|右耳电量
 * - BOSE|FW|固件版本|设备型号
 * - BOSE|CLEAR_PAIRING|OK/FAIL
 * - BOSE|ERROR|错误信息
 * 
 * PC → ESP32 命令:
 * - CMD|SCAN_START|数量  (数量为0表示不限制)
 * - CMD|SCAN_STOP
 * - CMD|REPAIR_START|MAC地址
 * - CMD|REPAIR_STOP
 * - CMD|GATTC_CONNECT|MAC地址
 * - CMD|GATTC_DISCONNECT
 * - CMD|GATTC_READ|UUID
 * - CMD|GATTC_WRITE|UUID|HEX_DATA
 * - CMD|GATTC_NOTIFY|UUID|ENABLE
 * - CMD|BOSE_CONNECT|MAC地址
 * - CMD|BOSE_DISCONNECT
 * - CMD|BOSE_CLEAR_PAIRING
 * - CMD|BOSE_READ_BATT
 * - CMD|BOSE_READ_FW
 */

#ifndef UART_PROTOCOL_H
#define UART_PROTOCOL_H

#include <stdbool.h>
#include "esp_err.h"
#include "esp_gap_ble_api.h"   // 推荐加

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
    CMD_UNKNOWN             /*!< 未知命令 */
} uart_cmd_t;

/**
 * @brief 命令参数结构体
 */
typedef struct {
    int scan_count;        /*!< 扫描数量限制，0表示不限制 */
    char target_addr[18];  /*!< 目标设备MAC地址 */
    uint8_t addr_type;   // ★新增这一行
} uart_cmd_params_t;

/**
 * @brief 串口命令回调函数类型
 * @param cmd 命令类型
 * @param params 命令参数
 */
typedef void (*uart_cmd_callback_t)(uart_cmd_t cmd, uart_cmd_params_t *params);

/**
 * @brief 初始化串口协议模块
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_init(void);

/**
 * @brief 发送BLE扫描结果到上位机
 * @param name 设备名称
 * @param addr 设备MAC地址
 * @param addr_type BLE地址类型
 * @param rssi 信号强度
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_ble_scan_result(const char *name, const char *addr, uint8_t addr_type, int rssi);

/**
 * @brief 发送经典蓝牙扫描结果到上位机
 * @param name 设备名称
 * @param addr 设备MAC地址
 * @param rssi 信号强度
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_bt_classic_scan_result(const char *name, const char *addr, int rssi);

/**
 * @brief 发送修复开始通知到上位机
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_repair_start(void);

/**
 * @brief 发送修复成功通知到上位机
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_repair_success(void);

/**
 * @brief 发送修复失败通知到上位机
 * @param reason 失败原因
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_repair_failed(const char *reason);

/**
 * @brief 发送日志消息到上位机（协议格式）
 * @param tag 日志标签
 * @param message 日志消息
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_log(const char *tag, const char *message);

/**
 * @brief 发送扫描状态到上位机
 * @param scanning 是否正在扫描
 * @param count 已扫描到的设备数量
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_scan_status(bool scanning, int count);

/**
 * @brief 设置命令回调函数
 * @param callback 回调函数指针
 */
void uart_protocol_set_callback(uart_cmd_callback_t callback);

/**
 * @brief 发送Bose设备连接成功通知到上位机
 * @param name 设备名称
 * @param model 设备型号
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_bose_connected(const char *name, const char *model);

/**
 * @brief 发送Bose设备断开连接通知到上位机
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_bose_disconnected(void);

/**
 * @brief 发送Bose设备电池信息到上位机
 * @param left_level 左耳电量百分比
 * @param right_level 右耳电量百分比
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_bose_battery(int left_level, int right_level);

/**
 * @brief 发送Bose设备固件信息到上位机
 * @param version 固件版本号
 * @param model 设备型号
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_bose_firmware(const char *version, const char *model);

/**
 * @brief 发送Bose设备清空配对结果到上位机
 * @param success 是否成功
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_bose_clear_pairing(bool success);

/**
 * @brief 发送Bose设备错误信息到上位机
 * @param message 错误信息
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_bose_error(const char *message);

#endif

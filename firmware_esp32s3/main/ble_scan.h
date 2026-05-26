/**
 * @file ble_scan.h
 * @brief BLE扫描模块头文件
 * 
 * 该模块负责BLE设备的扫描功能，包括初始化BLE控制器、
 * 启动/停止扫描、处理扫描结果回调等功能。
 */

#ifndef BLE_SCAN_H
#define BLE_SCAN_H

#include <stdbool.h>
#include "esp_err.h"

/**
 * @brief BLE设备信息结构体
 */
typedef struct {
    char name[64];      /*!< 设备名称 */
    char addr[18];      /*!< 设备MAC地址，格式如 "AA:BB:CC:DD:EE:FF" */
    int rssi;           /*!< 信号强度（dBm） */
} ble_device_t;

/**
 * @brief BLE扫描回调函数类型
 * @param device 扫描到的BLE设备信息
 */
typedef void (*ble_scan_callback_t)(ble_device_t *device);

/**
 * @brief 初始化BLE扫描模块
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t ble_scan_init(void);

/**
 * @brief 启动BLE扫描
 * @param count_limit 扫描数量限制（0表示不限制）
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t ble_scan_start(int count_limit);

/**
 * @brief 停止BLE扫描
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t ble_scan_stop(void);

/**
 * @brief 设置扫描结果回调函数
 * @param callback 回调函数指针
 */
void ble_scan_set_callback(ble_scan_callback_t callback);

/**
 * @brief 获取当前扫描状态
 * @return true: 正在扫描, false: 未扫描
 */
bool ble_scan_is_scanning(void);

/**
 * @brief 获取当前已扫描到的设备数量
 * @return 设备数量
 */
int ble_scan_get_count(void);

#endif

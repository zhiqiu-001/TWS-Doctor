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
#include "esp_gap_ble_api.h"
#include "freertos/FreeRTOS.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief BLE设备信息结构体
 */
typedef struct {

    char name[64];

    /**
     * MAC字符串
     * "AA:BB:CC:DD:EE:FF"
     */
    char addr[18];

    /**
     * 原始 MAC 地址
     */
    esp_bd_addr_t bda;

    /**
     * BLE 地址类型
     *
     * 0 = public
     * 1 = random
     */
    esp_ble_addr_type_t addr_type;

    /**
     * RSSI
     */
    int rssi;

} ble_device_t;

/**
 * @brief BLE扫描回调函数类型
 * @param device 扫描到的BLE设备信息
 */
typedef void (*ble_scan_callback_t)(ble_device_t *device);

/**
 * @brief BLE扩展广播报告回调函数类型
 * @param report 扩展广播报告信息
 */
typedef void (*ble_scan_ext_report_callback_t)(esp_ble_gap_ext_adv_report_t *report);

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
 * @brief 等待扫描完全停止
 * 
 * 阻塞等待直到收到 ESP_GAP_BLE_SCAN_STOP_COMPLETE_EVT 事件，
 * 确保蓝牙控制器已完全停止扫描。
 * 如果扫描未在运行，则立即返回。
 * 
 * @param timeout 等待超时时间（FreeRTOS tick）
 * @return ESP_OK: 扫描已停止, ESP_ERR_TIMEOUT: 等待超时
 */
esp_err_t ble_scan_wait_for_stop(TickType_t timeout);

/**
 * @brief 设置扫描结果回调函数
 * @param callback 回调函数指针
 */
void ble_scan_set_callback(ble_scan_callback_t callback);

/**
 * @brief 设置扩展广播报告回调函数
 * @param callback 回调函数指针
 */
void ble_scan_set_ext_report_callback(ble_scan_ext_report_callback_t callback);

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

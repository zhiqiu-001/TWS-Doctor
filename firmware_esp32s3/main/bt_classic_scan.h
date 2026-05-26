/**
 * @file bt_classic_scan.h
 * @brief 经典蓝牙扫描模块头文件
 * 
 * 注意：ESP32-S3不支持经典蓝牙（BR/EDR），此模块仅作占位符，
 * 所有函数返回ESP_ERR_NOT_SUPPORTED。
 * 如需支持经典蓝牙，请使用ESP32-WROOM芯片。
 */

#ifndef BT_CLASSIC_SCAN_H
#define BT_CLASSIC_SCAN_H

#include "esp_err.h"

/**
 * @brief 经典蓝牙设备信息结构体
 */
typedef struct {
    char name[64];      /*!< 设备名称 */
    char addr[18];      /*!< 设备MAC地址 */
    int rssi;           /*!< 信号强度（dBm） */
} bt_classic_device_t;

/**
 * @brief 经典蓝牙扫描回调函数类型
 * @param device 扫描到的经典蓝牙设备信息
 */
typedef void (*bt_classic_scan_callback_t)(bt_classic_device_t *device);

/**
 * @brief 初始化经典蓝牙扫描模块
 * @note ESP32-S3不支持经典蓝牙，此函数仅作占位符
 * @return ESP_ERR_NOT_SUPPORTED
 */
esp_err_t bt_classic_scan_init(void);

/**
 * @brief 启动经典蓝牙扫描
 * @note ESP32-S3不支持经典蓝牙，此函数仅作占位符
 * @return ESP_ERR_NOT_SUPPORTED
 */
esp_err_t bt_classic_scan_start(void);

/**
 * @brief 停止经典蓝牙扫描
 * @note ESP32-S3不支持经典蓝牙，此函数仅作占位符
 * @return ESP_ERR_NOT_SUPPORTED
 */
esp_err_t bt_classic_scan_stop(void);

/**
 * @brief 设置扫描结果回调函数
 * @note ESP32-S3不支持经典蓝牙，此函数仅作占位符
 * @param callback 回调函数指针
 */
void bt_classic_scan_set_callback(bt_classic_scan_callback_t callback);

#endif

/**
 * @file bt_classic_scan.c
 * @brief 经典蓝牙扫描模块实现
 * 
 * 注意：ESP32-S3不支持经典蓝牙（BR/EDR），此模块仅作占位符，
 * 所有函数返回ESP_ERR_NOT_SUPPORTED。
 * 如需支持经典蓝牙，请使用ESP32-WROOM芯片。
 */

#include "bt_classic_scan.h"
#include "esp_log.h"

/* 日志标签 */
static const char *TAG = "BT_CLASSIC";

/**
 * @brief 初始化经典蓝牙扫描模块
 * @note ESP32-S3不支持经典蓝牙
 * @return ESP_ERR_NOT_SUPPORTED
 */
esp_err_t bt_classic_scan_init(void)
{
    ESP_LOGW(TAG, "ESP32-S3 does NOT support classic Bluetooth (BR/EDR)!");
    ESP_LOGW(TAG, "Only BLE functions are available.");
    return ESP_ERR_NOT_SUPPORTED;
}

/**
 * @brief 启动经典蓝牙扫描
 * @note ESP32-S3不支持经典蓝牙
 * @return ESP_ERR_NOT_SUPPORTED
 */
esp_err_t bt_classic_scan_start(void)
{
    ESP_LOGW(TAG, "Classic Bluetooth scan not supported on ESP32-S3");
    return ESP_ERR_NOT_SUPPORTED;
}

/**
 * @brief 停止经典蓝牙扫描
 * @note ESP32-S3不支持经典蓝牙
 * @return ESP_ERR_NOT_SUPPORTED
 */
esp_err_t bt_classic_scan_stop(void)
{
    ESP_LOGW(TAG, "Classic Bluetooth scan not supported on ESP32-S3");
    return ESP_ERR_NOT_SUPPORTED;
}

/**
 * @brief 设置扫描结果回调函数
 * @note ESP32-S3不支持经典蓝牙
 * @param callback 回调函数指针
 */
void bt_classic_scan_set_callback(bt_classic_scan_callback_t callback)
{
    ESP_LOGW(TAG, "Classic Bluetooth callback not supported on ESP32-S3");
}

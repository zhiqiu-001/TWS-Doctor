/**
 * @file bt_utils.c
 * @brief 蓝牙工具模块实现
 * 
 * 该模块提供蓝牙相关的通用工具函数，包括MAC地址转换、数据处理等功能。
 */

#include "bt_utils.h"
#include "esp_log.h"

/* 日志标签 */
static const char *TAG = "BT_UTILS";

/**
 * @brief 初始化蓝牙工具模块
 * 
 * 该函数初始化蓝牙工具模块，准备相关资源。
 * 
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t bt_utils_init(void)
{
    ESP_LOGI(TAG, "Bluetooth utils initialized");
    return ESP_OK;
}

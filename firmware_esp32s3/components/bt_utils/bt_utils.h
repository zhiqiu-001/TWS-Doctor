/**
 * @file bt_utils.h
 * @brief 蓝牙工具模块头文件
 * 
 * 该模块提供蓝牙相关的通用工具函数，包括MAC地址转换、数据处理等功能。
 */

#ifndef BT_UTILS_H
#define BT_UTILS_H

#include "esp_err.h"

/**
 * @brief 初始化蓝牙工具模块
 * 
 * 该函数初始化蓝牙工具模块，准备相关资源。
 * 
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t bt_utils_init(void);

#endif

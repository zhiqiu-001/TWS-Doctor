/**
 * @file logger.h
 * @brief 日志模块头文件
 * 
 * 该模块提供统一的日志接口，用于系统日志输出和调试信息记录。
 */

#ifndef LOGGER_H
#define LOGGER_H

#include "esp_err.h"

/**
 * @brief 初始化日志模块
 * 
 * 该函数初始化日志系统，配置日志输出级别和格式。
 * 
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t logger_init(void);

#endif

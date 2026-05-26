/**
 * @file logger.c
 * @brief 日志模块实现
 * 
 * 该模块提供统一的日志接口，用于系统日志输出和调试信息记录。
 */

#include "logger.h"
#include "esp_log.h"

/* 日志标签 */
static const char *TAG = "LOGGER";

/**
 * @brief 初始化日志模块
 * 
 * 该函数初始化日志系统，配置日志输出级别和格式。
 * 
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t logger_init(void)
{
    ESP_LOGI(TAG, "Logger initialized");
    return ESP_OK;
}

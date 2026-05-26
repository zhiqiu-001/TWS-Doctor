/**
 * @file tws_manager.c
 * @brief TWS耳机管理模块实现
 * 
 * 该模块负责TWS耳机的修复流程管理，包括状态管理、修复操作等功能。
 */

#include "tws_manager.h"
#include "esp_log.h"
#include "uart_protocol.h"

/* 日志标签 */
static const char *TAG = "TWS_MANAGER";

/* 当前TWS状态 */
static tws_state_t current_state = TWS_STATE_IDLE;

/**
 * @brief 初始化TWS管理模块
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t tws_manager_init(void)
{
    ESP_LOGI(TAG, "Initializing TWS manager");
    current_state = TWS_STATE_IDLE;
    return ESP_OK;
}

/**
 * @brief 开始TWS修复流程
 * @param type 修复类型
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t tws_manager_start_repair(repair_type_t type)
{
    ESP_LOGI(TAG, "Starting TWS repair, type: %d", type);
    current_state = TWS_STATE_REPAIRING;
    
    /* 发送修复开始通知到上位机 */
    uart_protocol_send_repair_start();
    return ESP_OK;
}

/**
 * @brief 停止TWS修复流程
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t tws_manager_stop_repair(void)
{
    ESP_LOGI(TAG, "Stopping TWS repair");
    current_state = TWS_STATE_IDLE;
    return ESP_OK;
}

/**
 * @brief 获取当前TWS状态
 * @return 当前状态
 */
tws_state_t tws_manager_get_state(void)
{
    return current_state;
}

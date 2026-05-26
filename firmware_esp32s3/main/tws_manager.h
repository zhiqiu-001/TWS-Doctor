/**
 * @file tws_manager.h
 * @brief TWS耳机管理模块头文件
 * 
 * 该模块负责TWS耳机的修复流程管理，包括状态管理、修复操作等功能。
 */

#ifndef TWS_MANAGER_H
#define TWS_MANAGER_H

#include "esp_err.h"

/**
 * @brief TWS修复状态枚举
 */
typedef enum {
    TWS_STATE_IDLE,          /*!< 空闲状态 */
    TWS_STATE_SCANNING,      /*!< 扫描中 */
    TWS_STATE_CONNECTING,    /*!< 连接中 */
    TWS_STATE_REPAIRING,     /*!< 修复中 */
    TWS_STATE_SUCCESS,       /*!< 修复成功 */
    TWS_STATE_FAILED         /*!< 修复失败 */
} tws_state_t;

/**
 * @brief 修复类型枚举
 */
typedef enum {
    REPAIR_TYPE_SCAN_ONLY,    /*!< 仅扫描 */
    REPAIR_TYPE_RESET_BOND,   /*!< 重置配对信息 */
    REPAIR_TYPE_RECONNECT     /*!< 重新连接 */
} repair_type_t;

/**
 * @brief 初始化TWS管理模块
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t tws_manager_init(void);

/**
 * @brief 开始TWS修复流程
 * @param type 修复类型
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t tws_manager_start_repair(repair_type_t type);

/**
 * @brief 停止TWS修复流程
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t tws_manager_stop_repair(void);

/**
 * @brief 获取当前TWS状态
 * @return 当前状态
 */
tws_state_t tws_manager_get_state(void);

#endif

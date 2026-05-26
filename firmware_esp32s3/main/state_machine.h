/**
 * @file state_machine.h
 * @brief 状态机模块头文件
 * 
 * 该模块负责系统状态管理和事件分发，协调各模块之间的协作。
 */

#ifndef STATE_MACHINE_H
#define STATE_MACHINE_H

#include "esp_err.h"

/**
 * @brief 初始化状态机模块
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t state_machine_init(void);

#endif

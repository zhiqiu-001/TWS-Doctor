/**
 * @file bond_manager.h
 * @brief 蓝牙配对管理模块头文件
 * 
 * 该模块负责管理蓝牙设备的配对信息（bonding），
 * 包括清除配对、移除特定设备等功能。
 */

#ifndef BOND_MANAGER_H
#define BOND_MANAGER_H

#include "esp_err.h"

/**
 * @brief 初始化配对管理模块
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t bond_manager_init(void);

/**
 * @brief 清除所有配对设备
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t bond_manager_clear_all(void);

/**
 * @brief 移除指定MAC地址的配对设备
 * @param addr 设备MAC地址
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t bond_manager_remove_device(const char *addr);

#endif

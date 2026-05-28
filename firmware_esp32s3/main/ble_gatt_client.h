/**
 * @file ble_gatt_client.h
 * @brief BLE GATT Client 模块头文件
 *
 * 该模块实现 ESP32-S3 作为 BLE Client 连接到 Bose 耳机的功能：
 * - 自动连接指定 MAC
 * - 发现所有 Service/Characteristic UUID
 * - 打印 characteristic properties
 * - 支持 Read / Write / Notify
 *
 * 使用 Bluedroid 协议栈，兼容 ESP-IDF v5.x
 */

#ifndef BLE_GATT_CLIENT_H
#define BLE_GATT_CLIENT_H

#include <stdbool.h>
#include "esp_err.h"
#include "esp_bt_defs.h"
#include "esp_gatt_defs.h"

/**
 * @brief Characteristic 信息结构体
 */
typedef struct {
    esp_bt_uuid_t char_uuid;          /**< Characteristic UUID */
    uint16_t char_handle;             /**< Characteristic 句柄 */
    esp_gatt_char_prop_t properties;  /**< 属性（读/写/通知等） */
    uint16_t descr_handle;            /**< CCCD 描述符句柄（用于 notify/indicate） */
} ble_gatt_char_info_t;

/**
 * @brief Service 信息结构体
 */
typedef struct {
    esp_bt_uuid_t service_uuid;       /**< Service UUID */
    uint16_t start_handle;            /**< Service 起始句柄 */
    uint16_t end_handle;              /**< Service 结束句柄 */
    uint8_t char_count;               /**< 包含的 Characteristic 数量 */
    ble_gatt_char_info_t *chars;      /**< Characteristic 信息数组 */
} ble_gatt_service_info_t;

/**
 * @brief 连接状态枚举
 */
typedef enum {
    BLE_GATTC_STATE_IDLE,            /**< 空闲状态 */
    BLE_GATTC_STATE_CONNECTING,      /**< 连接中 */
    BLE_GATTC_STATE_CONNECTED,       /**< 已连接 */
    BLE_GATTC_STATE_DISCONNECTING,   /**< 断开连接中 */
    BLE_GATTC_STATE_DISCONNECTED     /**< 已断开 */
} ble_gattc_state_t;

/**
 * @brief 连接状态回调函数类型
 * @param state 当前状态
 * @param addr 目标设备地址
 */
typedef void (*ble_gattc_state_callback_t)(ble_gattc_state_t state, const esp_bd_addr_t addr);

/**
 * @brief 数据接收回调函数类型（Notify/Indicate）
 * @param char_uuid Characteristic UUID
 * @param data 数据指针
 * @param len 数据长度
 */
typedef void (*ble_gattc_data_callback_t)(const esp_bt_uuid_t *char_uuid, const uint8_t *data, uint16_t len);

/**
 * @brief 初始化 BLE GATT Client
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t ble_gatt_client_init(void);

/**
 * @brief 连接到指定 Bose 耳机
 * @param addr 目标设备 MAC 地址
 * @param addr_type 目标设备地址类型（public/random）
 * @return ESP_OK: 发起连接请求成功, 其他: 失败
 */
esp_err_t ble_gatt_client_connect(const esp_bd_addr_t addr, esp_ble_addr_type_t addr_type);

/**
 * @brief 断开连接
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t ble_gatt_client_disconnect(void);

/**
 * @brief 设置连接状态回调
 * @param callback 回调函数指针
 */
void ble_gatt_client_set_state_callback(ble_gattc_state_callback_t callback);

/**
 * @brief 设置数据接收回调（Notify/Indicate）
 * @param callback 回调函数指针
 */
void ble_gatt_client_set_data_callback(ble_gattc_data_callback_t callback);

/**
 * @brief 读取 Characteristic
 * @param char_uuid 目标 Characteristic UUID
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t ble_gatt_client_read_char(const esp_bt_uuid_t *char_uuid);

/**
 * @brief 写入 Characteristic
 * @param char_uuid 目标 Characteristic UUID
 * @param data 数据指针
 * @param len 数据长度
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t ble_gatt_client_write_char(const esp_bt_uuid_t *char_uuid, const uint8_t *data, uint16_t len);

/**
 * @brief 订阅 Notify/Indicate
 * @param char_uuid 目标 Characteristic UUID
 * @param enable true: 订阅, false: 取消订阅
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t ble_gatt_client_set_notify(const esp_bt_uuid_t *char_uuid, bool enable);

/**
 * @brief 获取当前连接状态
 * @return 当前状态
 */
ble_gattc_state_t ble_gatt_client_get_state(void);

/**
 * @brief 获取已发现的 Service 数量
 * @return Service 数量
 */
uint8_t ble_gatt_client_get_service_count(void);

/**
 * @brief 获取 Service 信息
 * @param index Service 索引
 * @return Service 信息指针，失败返回 NULL
 */
const ble_gatt_service_info_t *ble_gatt_client_get_service(uint8_t index);

#endif /* BLE_GATT_CLIENT_H */

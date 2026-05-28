/**
 * @file state_machine.c
 * @brief 状态机模块实现
 * 
 * 该模块负责系统状态管理和事件分发，协调各模块之间的协作。
 */

#include "state_machine.h"
#include "esp_log.h"
#include "ble_scan.h"
#include "uart_protocol.h"

/* 日志标签 */
static const char *TAG = "STATE_MACHINE";

/**
 * @brief BLE设备发现回调函数
 * @param device 发现的BLE设备信息
 */
static void on_ble_device_found(ble_device_t *device)
{
    ESP_LOGI(TAG,
             "Found BLE device: %s [%s] type=%d RSSI=%d",
             device->name,
             device->addr,
             device->addr_type,
             device->rssi);

    /**
     * 将扫描结果发送到上位机
     */
    uart_protocol_send_ble_scan_result(
        device->name,
        device->addr,
        device->addr_type,
        device->rssi
    );
}

/**
 * @brief 初始化状态机模块
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t state_machine_init(void)
{
    ESP_LOGI(TAG, "Initializing state machine");
    
    /* 设置BLE扫描回调函数 */
    ble_scan_set_callback(on_ble_device_found);
    
    return ESP_OK;
}

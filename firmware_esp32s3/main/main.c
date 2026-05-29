/**
 * @file main.c
 * @brief ESP32_TWS_Doctor 主程序入口
 * 
 * 该文件是ESP32-S3固件的主程序入口，负责初始化系统各模块，
 * 响应上位机命令，启动/停止BLE扫描。
 */

#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "esp_log.h"

/* 模块头文件 */
#include "ble_scan.h"
#include "ble_gatt_client.h"
#include "uart_protocol.h"
#include "state_machine.h"
#include "logger.h"

/* 日志标签 */
static const char *TAG = "APP_MAIN";

/**
 * @brief BLE扫描结果回调函数
 * @param device 扫描到的BLE设备信息
 */
static void on_ble_scan_result(ble_device_t *device)
{
    (void)device;
}

/**
 * @brief GATT 连接状态回调
 * @param state 状态
 * @param addr 设备地址
 */
static void on_gattc_state(ble_gattc_state_t state, const esp_bd_addr_t addr)
{
    char state_str[32] = {0};
    switch (state) {
        case BLE_GATTC_STATE_IDLE: strcpy(state_str, "IDLE"); break;
        case BLE_GATTC_STATE_CONNECTING: strcpy(state_str, "CONNECTING"); break;
        case BLE_GATTC_STATE_CONNECTED: strcpy(state_str, "CONNECTED"); break;
        case BLE_GATTC_STATE_DISCONNECTING: strcpy(state_str, "DISCONNECTING"); break;
        case BLE_GATTC_STATE_DISCONNECTED: strcpy(state_str, "DISCONNECTED"); break;
        default: strcpy(state_str, "UNKNOWN"); break;
    }
    
    ESP_LOGI(TAG, "GATTC state: %s", state_str);
    
    /* 通过 UART 发送状态到上位机 */
    char msg[64] = {0};
    snprintf(msg, sizeof(msg), "GATTC:%s", state_str);
    uart_protocol_send_log("APP", msg);
}

/**
 * @brief GATT 数据接收回调
 * @param char_uuid Characteristic UUID
 * @param data 数据
 * @param len 长度
 */
static void on_gattc_data(const esp_bt_uuid_t *char_uuid, const uint8_t *data, uint16_t len)
{
    ESP_LOGI(TAG, "GATTC data received");
    
    /* 通过 UART 发送到上位机 */
    char msg[256] = {0};
    int offset = snprintf(msg, sizeof(msg), "GATTC_DATA:");
    for (int i = 0; i < len && offset < sizeof(msg) - 4; i++) {
        offset += snprintf(msg + offset, sizeof(msg) - offset, " %02X", data[i]);
    }
    uart_protocol_send_log("APP", msg);
}

/**
 * @brief 串口命令回调函数
 * @param cmd 命令类型
 * @param params 命令参数
 */
static void on_uart_command(uart_cmd_t cmd, uart_cmd_params_t *params)
{
    ESP_LOGI(TAG, "Received command: %d", cmd);
    
    switch (cmd) {
        case CMD_SCAN_START: {
            int count = params ? params->scan_count : 0;
            ESP_LOGI(TAG, "Starting scan with count limit: %d", count);
            uart_protocol_send_scan_status(true, 0);
            ble_scan_start(count);
            break;
        }
        case CMD_SCAN_STOP: {
            ESP_LOGI(TAG, "Stopping scan");
            ble_scan_stop();
            uart_protocol_send_scan_status(false, ble_scan_get_count());
            break;
        }
        case CMD_REPAIR_START: {
            const char *target_addr = params ? params->target_addr : "";
            ESP_LOGI(TAG, "Starting repair for: %s", target_addr);
            uart_protocol_send_repair_start();
            // TODO: 实现修复逻辑
            // tws_repair_start(target_addr);
            break;
        }
        case CMD_REPAIR_STOP: {
            ESP_LOGI(TAG, "Stopping repair");
            // TODO: 实现停止修复逻辑
            // tws_repair_stop();
            break;
        }
        case CMD_GATTC_CONNECT: {
            const char *addr_str = params ? params->target_addr : "";
            esp_ble_addr_type_t addr_type = params ? params->addr_type : BLE_ADDR_TYPE_PUBLIC;

            ESP_LOGI(TAG, "GATTC connect: %s, type=%d", addr_str, addr_type);
            
            /* 解析 MAC 地址 */
            esp_bd_addr_t addr = {0};
            unsigned int a0, a1, a2, a3, a4, a5;
            if (sscanf(addr_str, "%02X:%02X:%02X:%02X:%02X:%02X",
                      &a0, &a1, &a2, &a3, &a4, &a5) == 6) {
                addr[0] = a0; addr[1] = a1; addr[2] = a2;
                addr[3] = a3; addr[4] = a4; addr[5] = a5;
                ble_gatt_client_connect_ext(addr, addr_type, NULL);
            } else {
                ESP_LOGE(TAG, "Invalid MAC address format");
            }
            break;
        }
        case CMD_GATTC_DISCONNECT: {
            ESP_LOGI(TAG, "GATTC disconnect");
            ble_gatt_client_disconnect();
            break;
        }
        case CMD_GATTC_READ: {
            const char *uuid_str = params ? params->target_addr : "";
            ESP_LOGI(TAG, "GATTC read: %s", uuid_str);
            // TODO: 解析 UUID 并调用 ble_gatt_client_read_char
            break;
        }
        case CMD_GATTC_WRITE: {
            ESP_LOGI(TAG, "GATTC write");
            // TODO: 解析 UUID 和数据并调用 ble_gatt_client_write_char
            break;
        }
        case CMD_GATTC_NOTIFY: {
            ESP_LOGI(TAG, "GATTC notify");
            // TODO: 解析 UUID 和 enable 并调用 ble_gatt_client_set_notify
            break;
        }
        case CMD_BOSE_CONNECT: {
            const char *addr_str = params ? params->target_addr : "";
            esp_ble_addr_type_t addr_type = params ? params->addr_type : BLE_ADDR_TYPE_PUBLIC;
            ESP_LOGI(TAG, "Bose connect: %s, type=%d", addr_str, addr_type);

            /* 解析 MAC 地址 */
            esp_bd_addr_t addr = {0};
            unsigned int a0, a1, a2, a3, a4, a5;
            if (sscanf(addr_str, "%02X:%02X:%02X:%02X:%02X:%02X",
                      &a0, &a1, &a2, &a3, &a4, &a5) == 6) {
                addr[0] = a0; addr[1] = a1; addr[2] = a2;
                addr[3] = a3; addr[4] = a4; addr[5] = a5;
                /* 使用 pending target 机制：
                 * 如果扫描正在运行，立即执行 connect_now(is_aux=true)；
                 * 如果扫描已停止，重新启动扫描等待目标设备 EXT_ADV_REPORT，
                 * 在回调中立即连接（is_aux=true 必须靠近 AUX context） */
                ble_gatt_client_connect_ext(addr, addr_type, NULL);
            } else {
                ESP_LOGE(TAG, "Invalid MAC address format");
                uart_protocol_send_bose_error("Invalid MAC address format");
            }
            break;
        }
        case CMD_BOSE_DISCONNECT: {
            ESP_LOGI(TAG, "Bose disconnect");
            ble_gatt_client_disconnect();
            break;
        }
        case CMD_BOSE_CLEAR_PAIRING: {
            ESP_LOGI(TAG, "Bose clear pairing");
            // TODO: 实现清空配对逻辑
            // 这通常涉及写入特定的 GATT characteristic
            // 对于 Bose 设备，通常需要写入特殊命令到配对服务
            uart_protocol_send_bose_clear_pairing(true);
            break;
        }
        case CMD_BOSE_READ_BATT: {
            ESP_LOGI(TAG, "Bose read battery");
            // TODO: 实现读取电池逻辑
            // 模拟返回电池数据（实际应用中需要读取 GATT characteristic）
            uart_protocol_send_bose_battery(85, 82);
            break;
        }
        case CMD_BOSE_READ_FW: {
            ESP_LOGI(TAG, "Bose read firmware");
            // TODO: 实现读取固件版本逻辑
            // 模拟返回固件数据（实际应用中需要读取 GATT characteristic）
            uart_protocol_send_bose_firmware("4.5.2", "Bose QuietComfort Earbuds");
            break;
        }
        /* === AT+ 命令处理 === */
        case CMD_AT_SCAN: {
            ESP_LOGI(TAG, "AT+SCAN: starting scan");
            ble_scan_start(0);
            break;
        }
        case CMD_AT_SCANSTOP: {
            ESP_LOGI(TAG, "AT+SCANSTOP: stopping scan");
            ble_scan_stop();
            break;
        }
        case CMD_AT_CONNECT: {
            const char *addr_str = params ? params->target_addr : "";
            uint8_t addr_type = params ? params->addr_type : 0;
            ESP_LOGI(TAG, "AT+CONNECT: %s, type=%d", addr_str, addr_type);

            esp_bd_addr_t addr = {0};
            unsigned int a0, a1, a2, a3, a4, a5;
            if (sscanf(addr_str, "%02x:%02x:%02x:%02x:%02x:%02x",
                      &a0, &a1, &a2, &a3, &a4, &a5) == 6) {
                addr[0] = a0; addr[1] = a1; addr[2] = a2;
                addr[3] = a3; addr[4] = a4; addr[5] = a5;
                ble_gatt_client_connect_ext(addr, (esp_ble_addr_type_t)addr_type, "");
            } else if (sscanf(addr_str, "%02X:%02X:%02X:%02X:%02X:%02X",
                      &a0, &a1, &a2, &a3, &a4, &a5) == 6) {
                addr[0] = a0; addr[1] = a1; addr[2] = a2;
                addr[3] = a3; addr[4] = a4; addr[5] = a5;
                ble_gatt_client_connect_ext(addr, (esp_ble_addr_type_t)addr_type, "");
            } else {
                ESP_LOGE(TAG, "Invalid MAC in AT+CONNECT");
                uart_protocol_send_error_msg("Invalid MAC address");
            }
            break;
        }
        case CMD_AT_DISCONNECT: {
            ESP_LOGI(TAG, "AT+DISCONNECT");
            ble_gatt_client_disconnect();
            break;
        }
        case CMD_AT_HELP: {
            ESP_LOGI(TAG, "AT+HELP");
            uart_protocol_send_help();
            break;
        }
        case CMD_PING: {
            ESP_LOGI(TAG, "PING received, re-sending [INIT]");
            uart_protocol_send_init_msg("ESP32_TWS_Doctor ready");
            break;
        }
        default:
            ESP_LOGW(TAG, "Unknown command: %d", cmd);
            break;
    }
}

/**
 * @brief 主程序入口函数
 * 
 * 该函数是ESP32应用程序的入口点，负责：
 * 1. 初始化NVS Flash
 * 2. 初始化各功能模块
 * 3. 设置命令回调
 * 4. 进入主循环等待命令
 */
void app_main(void)
{
    ESP_LOGI(TAG, "ESP32_TWS_Doctor starting...");

    /* 初始化NVS Flash */
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        /* 如果NVS分区已满或版本不匹配，擦除后重新初始化 */
        ESP_ERROR_CHECK(nvs_flash_erase());
        ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

    /* 初始化日志模块 */
    logger_init();

    /* 初始化串口协议模块 */
    uart_protocol_init();

    /* 初始化状态机模块 */
    state_machine_init();

    /* 初始化BLE扫描模块 */
    ble_scan_init();

    /* 初始化BLE GATT Client模块 */
    ble_gatt_client_init();

    /* 设置BLE扫描回调函数 */
    ble_scan_set_callback(on_ble_scan_result);

    /* 设置GATT Client回调函数 */
    ble_gatt_client_set_state_callback(on_gattc_state);
    ble_gatt_client_set_data_callback(on_gattc_data);

    /* 设置串口命令回调函数 */
    uart_protocol_set_callback(on_uart_command);

    uart_protocol_send_log(TAG, "ESP32_TWS_Doctor ready");
    uart_protocol_send_init_msg("ESP32_TWS_Doctor initialized successfully");
    ESP_LOGI(TAG, "System initialized, waiting for commands...");

    /* 主循环 */
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(100));  /* 延时100ms */
    }
}

/**
 * @file uart_protocol.c
 * @brief 串口协议模块实现
 * 
 * 该模块负责ESP32与PC上位机之间的串口通信协议，
 * 使用简单的管道符（|）分隔格式进行数据传输。
 */

#include "uart_protocol.h"
#include "esp_log.h"
#include "driver/uart.h"
#include "freertos/semphr.h"
#include <string.h>

/* 日志标签 */
static const char *TAG = "UART_PROTOCOL";

/* UART端口号 */
#define UART_NUM UART_NUM_0

/* UART缓冲区大小 */
#define UART_BUF_SIZE 1024

/* 命令回调函数指针 */
static uart_cmd_callback_t cmd_callback = NULL;

/* UART发送互斥锁，防止多任务同时发送导致数据混乱 */
static SemaphoreHandle_t uart_tx_mutex = NULL;

/**
 * @brief 解析上位机命令
 * @param data 接收到的数据
 */
static void parse_command(const char *data)
{
    ESP_LOGI(TAG, "Received raw data from PC: '%s'", data);
    
    if (!cmd_callback) {
        ESP_LOGW(TAG, "No command callback registered");
        return;
    }

    uart_cmd_params_t params = {0};

    /* CMD|SCAN_START|数量 */
    if (strstr(data, "CMD|SCAN_START|") == data)
    {
        const char *count_str = data + 15;

        params.scan_count = atoi(count_str);

        ESP_LOGI(TAG,
                "Parsed SCAN_START command, count=%d",
                params.scan_count);

        cmd_callback(CMD_SCAN_START, &params);

        ESP_LOGI(TAG, "SCAN_START command processed");
    }
    /* CMD|SCAN_STOP */
    else if (strcmp(data, "CMD|SCAN_STOP") == 0) {
        ESP_LOGI(TAG, "Parsed SCAN_STOP command");
        cmd_callback(CMD_SCAN_STOP, &params);
        ESP_LOGI(TAG, "SCAN_STOP command processed");
    }
    /* CMD|REPAIR_START|MAC地址 */
    else if (strstr(data, "CMD|REPAIR_START|") == data) {
        const char *addr_str = data + 17;  /* 跳过 "CMD|REPAIR_START|" */
        strncpy(params.target_addr, addr_str, sizeof(params.target_addr) - 1);
        ESP_LOGI(TAG, "Parsed REPAIR_START command, target=%s", params.target_addr);
        cmd_callback(CMD_REPAIR_START, &params);
        ESP_LOGI(TAG, "REPAIR_START command processed");
    }
    /* CMD|REPAIR_STOP */
    else if (strcmp(data, "CMD|REPAIR_STOP") == 0) {
        ESP_LOGI(TAG, "Parsed REPAIR_STOP command");
        cmd_callback(CMD_REPAIR_STOP, &params);
        ESP_LOGI(TAG, "REPAIR_STOP command processed");
    }
    /* CMD|GATTC_CONNECT|MAC地址 */
    else if (strstr(data, "CMD|GATTC_CONNECT|") == data) {
        const char *addr_str = data + 18;  /* 跳过 "CMD|GATTC_CONNECT|" */
        strncpy(params.target_addr, addr_str, sizeof(params.target_addr) - 1);
        ESP_LOGI(TAG, "Parsed GATTC_CONNECT command, target=%s", params.target_addr);
        cmd_callback(CMD_GATTC_CONNECT, &params);
        ESP_LOGI(TAG, "GATTC_CONNECT command processed");
    }
    /* CMD|GATTC_DISCONNECT */
    else if (strcmp(data, "CMD|GATTC_DISCONNECT") == 0) {
        ESP_LOGI(TAG, "Parsed GATTC_DISCONNECT command");
        cmd_callback(CMD_GATTC_DISCONNECT, &params);
        ESP_LOGI(TAG, "GATTC_DISCONNECT command processed");
    }
    /* CMD|GATTC_READ|UUID */
    else if (strstr(data, "CMD|GATTC_READ|") == data) {
        const char *uuid_str = data + 15;
        strncpy(params.target_addr, uuid_str, sizeof(params.target_addr) - 1);
        ESP_LOGI(TAG, "Parsed GATTC_READ command, uuid=%s", params.target_addr);
        cmd_callback(CMD_GATTC_READ, &params);
        ESP_LOGI(TAG, "GATTC_READ command processed");
    }
    /* CMD|GATTC_WRITE|UUID|HEX_DATA */
    else if (strstr(data, "CMD|GATTC_WRITE|") == data) {
        const char *rest = data + 16;
        char *pipe = strchr(rest, '|');
        if (pipe) {
            strncpy(params.target_addr, rest, pipe - rest);
            params.target_addr[pipe - rest] = '\0';
            ESP_LOGI(TAG, "Parsed GATTC_WRITE command, uuid=%s", params.target_addr);
            cmd_callback(CMD_GATTC_WRITE, &params);
            ESP_LOGI(TAG, "GATTC_WRITE command processed");
        }
    }
    /* CMD|GATTC_NOTIFY|UUID|ENABLE */
    else if (strstr(data, "CMD|GATTC_NOTIFY|") == data) {
        const char *rest = data + 17;
        char *pipe = strchr(rest, '|');
        if (pipe) {
            strncpy(params.target_addr, rest, pipe - rest);
            params.target_addr[pipe - rest] = '\0';
            ESP_LOGI(TAG, "Parsed GATTC_NOTIFY command, uuid=%s, enable=%s", params.target_addr, pipe + 1);
            cmd_callback(CMD_GATTC_NOTIFY, &params);
            ESP_LOGI(TAG, "GATTC_NOTIFY command processed");
        }
    }
    else {
        ESP_LOGW(TAG, "Unknown command: %s", data);
    }
}

/**
 * @brief UART接收任务
 * @param pvParameters 参数
 */
static void uart_rx_task(void *pvParameters)
{

    uart_protocol_send_log(TAG, "uart_rx_task started");

    uint8_t *data = (uint8_t *)malloc(UART_BUF_SIZE);

    if (!data) {
        ESP_LOGE(TAG, "Failed to allocate UART RX buffer");
        vTaskDelete(NULL);
        return;
    }

    ESP_LOGI(TAG, "UART RX task started");

    while (1) {

        /* 从UART读取数据 */
        int len = uart_read_bytes(
            UART_NUM,
            data,
            UART_BUF_SIZE - 1,
            pdMS_TO_TICKS(100)
        );

        if (len > 0) {

            /* 字符串结束符 */
            data[len] = '\0';

            char log_buffer[256];

            snprintf(log_buffer, sizeof(log_buffer),
                    "UART RX Raw: %s",
                    (char *)data);

            uart_protocol_send_log(TAG, log_buffer);

            /* 去除 \r */
            char *carriage = strchr((char *)data, '\r');
            if (carriage) {
                *carriage = '\0';
            }

            /* 去除 \n */
            char *newline = strchr((char *)data, '\n');
            if (newline) {
                *newline = '\0';
            }

            /* 空字符串检查 */
            if (((char *)data)[0] != '\0') {

                ESP_LOGI(TAG, "Parsing command: %s", (char *)data);

                /* 解析命令 */
                parse_command((char *)data);
            }
        }

        vTaskDelay(pdMS_TO_TICKS(50));
    }

    /* 理论上不会执行到这里 */
    free(data);

    vTaskDelete(NULL);
}

/**
 * @brief 带互斥锁保护的UART发送函数
 * @param data 要发送的数据
 * @param len 数据长度
 */
static void uart_safe_write(const char *data, size_t len)
{
    if (!data || len == 0) {
        return;
    }

    if (uart_tx_mutex) {
        xSemaphoreTake(uart_tx_mutex, portMAX_DELAY);
    }

    uart_write_bytes(UART_NUM, data, len);

    if (uart_tx_mutex) {
        xSemaphoreGive(uart_tx_mutex);
    }
}

/**
 * @brief 初始化串口协议模块
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_init(void)
{
    ESP_LOGI(TAG, "Initializing UART protocol");

    /* 创建UART发送互斥锁 */
    uart_tx_mutex = xSemaphoreCreateMutex();
    if (!uart_tx_mutex) {
        ESP_LOGE(TAG, "Failed to create UART TX mutex");
        return ESP_ERR_NO_MEM;
    }

    uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE,
        .source_clk = UART_SCLK_APB,
    };

    esp_err_t ret = uart_driver_install(
        UART_NUM,
        UART_BUF_SIZE * 2,
        UART_BUF_SIZE * 2,
        10,
        NULL,
        0
    );

    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "uart_driver_install failed");
        return ret;
    }

    ret = uart_param_config(UART_NUM, &uart_config);

    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "uart_param_config failed");
        return ret;
    }

    xTaskCreate(
        uart_rx_task,
        "uart_rx_task",
        4096,
        NULL,
        5,
        NULL
    );

    return ESP_OK;
}

/**
 * @brief 发送BLE扫描结果到上位机
 * @param name 设备名称
 * @param addr 设备MAC地址
 * @param rssi 信号强度
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_ble_scan_result(const char *name, const char *addr, int rssi)
{
    char buffer[256];
    /* 格式: SCAN|BLE|设备名称|MAC地址|RSSI */
    snprintf(buffer, sizeof(buffer), "SCAN|BLE|%s|%s|%d\n", name, addr, rssi);
    ESP_LOGI(TAG, "UART TX: %s", buffer);
    uart_safe_write(buffer, strlen(buffer));
    return ESP_OK;
}

/**
 * @brief 发送经典蓝牙扫描结果到上位机
 * @param name 设备名称
 * @param addr 设备MAC地址
 * @param rssi 信号强度
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_bt_classic_scan_result(const char *name, const char *addr, int rssi)
{
    char buffer[256];
    /* 格式: SCAN|CLASSIC|设备名称|MAC地址|RSSI */
    snprintf(buffer, sizeof(buffer), "SCAN|CLASSIC|%s|%s|%d\n", name, addr, rssi);
    uart_safe_write(buffer, strlen(buffer));
    return ESP_OK;
}

/**
 * @brief 发送修复开始通知到上位机
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_repair_start(void)
{
    const char *msg = "REPAIR|START\n";
    uart_safe_write(msg, strlen(msg));
    return ESP_OK;
}

/**
 * @brief 发送修复成功通知到上位机
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_repair_success(void)
{
    const char *msg = "REPAIR|SUCCESS\n";
    uart_safe_write(msg, strlen(msg));
    return ESP_OK;
}

/**
 * @brief 发送日志消息到上位机（协议格式）
 * @param tag 日志标签
 * @param message 日志消息
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_log(const char *tag, const char *message)
{
    char buffer[256];
    snprintf(buffer, sizeof(buffer), "LOG|%s|%s\n", tag, message);
    uart_safe_write(buffer, strlen(buffer));
    return ESP_OK;
}

/**
 * @brief 发送修复失败通知到上位机
 * @param reason 失败原因
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_repair_failed(const char *reason)
{
    char buffer[256];
    /* 格式: REPAIR|FAILED|失败原因 */
    snprintf(buffer, sizeof(buffer), "REPAIR|FAILED|%s\n", reason);
    uart_safe_write(buffer, strlen(buffer));
    return ESP_OK;
}

/**
 * @brief 发送扫描状态到上位机
 * @param scanning 是否正在扫描
 * @param count 已扫描到的设备数量
 * @return ESP_OK: 成功, 其他: 失败
 */
esp_err_t uart_protocol_send_scan_status(bool scanning, int count)
{
    char buffer[64];
    if (scanning) {
        snprintf(buffer, sizeof(buffer), "STATUS|SCANNING|%d\n", count);
    } else {
        snprintf(buffer, sizeof(buffer), "STATUS|IDLE\n");
    }
    uart_safe_write(buffer, strlen(buffer));
    return ESP_OK;
}

/**
 * @brief 设置命令回调函数
 * @param callback 回调函数指针
 */
void uart_protocol_set_callback(uart_cmd_callback_t callback)
{
    cmd_callback = callback;
}

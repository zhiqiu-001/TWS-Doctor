/**
 * @file ble_scan.c
 * @brief BLE扫描模块实现
 */

#include "ble_scan.h"

#include <string.h>
#include <stdio.h>

#include "esp_log.h"
#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_bt_device.h"
#include "esp_gap_ble_api.h"
#include "esp_gatt_common_api.h"

#include "uart_protocol.h"

static const char *TAG = "BLE_SCAN";

static ble_scan_callback_t scan_callback = NULL;

static bool scanning = false;

static int scan_count_limit = 0;

static int scan_count = 0;

/**
 * @brief BLE GAP事件处理函数
 */
static void gap_event_handler(esp_gap_ble_cb_event_t event,
                              esp_ble_gap_cb_param_t *param)
{
    switch (event) {

    /**
     * 扩展广播扫描结果事件
     */
    case ESP_GAP_BLE_EXT_ADV_REPORT_EVT: {

        esp_ble_gap_ext_adv_report_t *report =
            &param->ext_adv_report.params;

        ble_device_t device = {0};

        /**
         * RSSI
         */
        device.rssi = report->rssi;

        /**
         * MAC地址
         */
        snprintf(device.addr,
                 sizeof(device.addr),
                 "%02X:%02X:%02X:%02X:%02X:%02X",
                 report->addr[0],
                 report->addr[1],
                 report->addr[2],
                 report->addr[3],
                 report->addr[4],
                 report->addr[5]);

        /**
         * 获取设备名称
         */
        uint8_t name_len = 0;

        uint8_t *name =
            esp_ble_resolve_adv_data(
                report->adv_data,
                ESP_BLE_AD_TYPE_NAME_CMPL,
                &name_len);

        /**
         * 如果没有完整名称
         * 再尝试短名称
         */
        if (name == NULL) {

            name =
                esp_ble_resolve_adv_data(
                    report->adv_data,
                    ESP_BLE_AD_TYPE_NAME_SHORT,
                    &name_len);
        }

        /**
         * 复制名称
         */
        if (name && name_len > 0) {

            if (name_len >= sizeof(device.name)) {
                name_len = sizeof(device.name) - 1;
            }

            memcpy(device.name,
                   name,
                   name_len);

            device.name[name_len] = '\0';
        }

        ESP_LOGI(TAG,
                 "Device found [%d/%d]: name='%s', addr=%s, rssi=%d",
                 scan_count + 1,
                 scan_count_limit > 0 ?
                    scan_count_limit : 999,
                 device.name[0] ?
                    device.name : "(unknown)",
                 device.addr,
                 device.rssi);

        /**
         * 发给上位机（只发送有名称的设备）
         */
        if (device.name[0]) {
            ESP_LOGI(TAG, "Sending scan result to PC: SCAN|BLE|%s|%s|%d", 
                     device.name, device.addr, device.rssi);
            uart_protocol_send_ble_scan_result(
                device.name,
                device.addr,
                device.rssi
            );
        } else {
            ESP_LOGI(TAG, "Skipping device without name: %s", device.addr);
        }

        /**
         * 回调
         */
        if (scan_callback) {
            scan_callback(&device);
        }

        scan_count++;

        uart_protocol_send_scan_status(
            true,
            scan_count
        );

        /**
         * 达到数量限制
         */
        if (scan_count_limit > 0 &&
            scan_count >= scan_count_limit &&
            scanning) {

            ESP_LOGI(TAG,
                     "=== Scan count limit reached ===");

            ble_scan_stop();
        }

        break;
    }

    /**
     * 扫描停止事件
     */
    case ESP_GAP_BLE_SCAN_STOP_COMPLETE_EVT: {

        ESP_LOGI(TAG,
                 "BLE scan stop complete");

        uart_protocol_send_scan_status(
            false,
            scan_count
        );

        break;
    }

    default:
        break;
    }
}

/**
 * @brief 初始化BLE扫描模块
 */
esp_err_t ble_scan_init(void)
{
    ESP_LOGI(TAG,
             "Initializing BLE scan");

    esp_err_t ret;

    /**
     * 初始化蓝牙控制器
     */
    esp_bt_controller_config_t bt_cfg =
        BT_CONTROLLER_INIT_CONFIG_DEFAULT();

    ret = esp_bt_controller_init(&bt_cfg);

    if (ret != ESP_OK) {

        ESP_LOGE(TAG,
                 "esp_bt_controller_init failed: %s",
                 esp_err_to_name(ret));

        return ret;
    }

    /**
     * 启用BLE
     */
    ret = esp_bt_controller_enable(
            ESP_BT_MODE_BLE);

    if (ret != ESP_OK) {

        ESP_LOGE(TAG,
                 "esp_bt_controller_enable failed: %s",
                 esp_err_to_name(ret));

        return ret;
    }

    /**
     * 初始化Bluedroid
     */
    ret = esp_bluedroid_init();

    if (ret != ESP_OK) {

        ESP_LOGE(TAG,
                 "esp_bluedroid_init failed: %s",
                 esp_err_to_name(ret));

        return ret;
    }

    /**
     * 启用Bluedroid
     */
    ret = esp_bluedroid_enable();

    if (ret != ESP_OK) {

        ESP_LOGE(TAG,
                 "esp_bluedroid_enable failed: %s",
                 esp_err_to_name(ret));

        return ret;
    }

    /**
     * 注册GAP回调
     */
    ret = esp_ble_gap_register_callback(
            gap_event_handler);

    if (ret != ESP_OK) {

        ESP_LOGE(TAG,
                 "esp_ble_gap_register_callback failed: %s",
                 esp_err_to_name(ret));

        return ret;
    }

    ESP_LOGI(TAG,
             "BLE initialized successfully");

    return ESP_OK;
}

/**
 * @brief 启动BLE扫描
 */
esp_err_t ble_scan_start(int count_limit)
{
    ESP_LOGI(TAG,
             "=== Starting BLE scan ===");

    uart_protocol_send_scan_status(
        true,
        0
    );

    scanning = true;

    scan_count_limit = count_limit;

    scan_count = 0;

    /**
     * BLE5 扩展扫描参数
     */
    esp_ble_ext_scan_params_t ext_scan_params = {

        /**
         * 本机地址类型
         */
        .own_addr_type =
            BLE_ADDR_TYPE_PUBLIC,

        /**
         * 允许所有设备
         */
        .filter_policy =
            BLE_SCAN_FILTER_ALLOW_ALL,

        /**
         * 不过滤重复
         */
        .scan_duplicate =
            BLE_SCAN_DUPLICATE_DISABLE,

        /**
         * 同时支持：
         * 1. 普通广播
         * 2. coded phy
         */
        .cfg_mask =
            ESP_BLE_GAP_EXT_SCAN_CFG_UNCODE_MASK |
            ESP_BLE_GAP_EXT_SCAN_CFG_CODE_MASK,

        /**
         * 普通PHY
         */
        .uncoded_cfg = {

            /**
             * 主动扫描
             * 才能获取scan response
             */
            .scan_type =
                BLE_SCAN_TYPE_ACTIVE,

            .scan_interval = 0x50,

            .scan_window = 0x30,
        },

        /**
         * coded phy
         */
        .coded_cfg = {

            .scan_type =
                BLE_SCAN_TYPE_ACTIVE,

            .scan_interval = 0x50,

            .scan_window = 0x30,
        },
    };

    ESP_LOGI(TAG,
             "Setting ext scan params...");

    esp_err_t ret =
        esp_ble_gap_set_ext_scan_params(
            &ext_scan_params);

    if (ret != ESP_OK) {

        ESP_LOGE(TAG,
                 "esp_ble_gap_set_ext_scan_params failed: %s",
                 esp_err_to_name(ret));

        scanning = false;

        return ret;
    }

    ESP_LOGI(TAG,
             "Starting ext scan...");

    ret = esp_ble_gap_start_ext_scan(0, 0);

    if (ret != ESP_OK) {

        ESP_LOGE(TAG,
                 "esp_ble_gap_start_ext_scan failed: %s",
                 esp_err_to_name(ret));

        scanning = false;

        return ret;
    }

    ESP_LOGI(TAG,
             "BLE scan started successfully");

    uart_protocol_send_log(
        TAG,
        "BLE scan started"
    );

    return ESP_OK;
}

/**
 * @brief 停止BLE扫描
 */
esp_err_t ble_scan_stop(void)
{
    ESP_LOGI(TAG,
             "Stopping BLE scan");

    scanning = false;

    return esp_ble_gap_stop_ext_scan();
}

/**
 * @brief 设置扫描结果回调
 */
void ble_scan_set_callback(
    ble_scan_callback_t callback)
{
    scan_callback = callback;
}

/**
 * @brief 获取扫描状态
 */
bool ble_scan_is_scanning(void)
{
    return scanning;
}

/**
 * @brief 获取扫描数量
 */
int ble_scan_get_count(void)
{
    return scan_count;
}
/**
 * @file ble_scan.c
 * @brief BLE扫描模块实现
 */

#include "ble_scan.h"

#include <string.h>
#include <stdio.h>
#include <inttypes.h>

#include "esp_log.h"
#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_bt_device.h"
#include "esp_gap_ble_api.h"
#include "esp_gatt_common_api.h"
#include "freertos/FreeRTOS.h"
#include "freertos/semphr.h"

#include "uart_protocol.h"

static const char *TAG = "BLE_SCAN";

static ble_scan_callback_t scan_callback = NULL;
static ble_scan_ext_report_callback_t ext_report_callback = NULL;

static bool scanning = false;

static int scan_count_limit = 0;

static int scan_count = 0;

static SemaphoreHandle_t scan_stop_sem = NULL;
static bool scan_stop_pending = false;

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
         * 保存原始 MAC 地址
         */
        memcpy(device.bda,
            report->addr,
            ESP_BD_ADDR_LEN);

        /**
         * 保存 BLE 地址类型
         */
        device.addr_type =
            report->addr_type;

        /**
         * MAC字符串
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
         * 打印地址类型（非常重要）
         */
        ESP_LOGI(TAG,
                "Address type: %d (%s)",
                device.addr_type,
                device.addr_type == BLE_ADDR_TYPE_PUBLIC ?
                    "PUBLIC" : "RANDOM");

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

        /**
         * 发给上位机（包含 [DEVICE] 格式，无论是否有名称）
         */
        uart_protocol_send_ble_scan_result(
            device.name,
            device.addr,
            device.addr_type,
            device.rssi
        );
        uart_protocol_send_device_found(
            device.addr_type,
            device.addr,
            device.rssi,
            device.name[0] ? device.name : "(no name)"
        );

        /**
         * 回调
         */
        if (scan_callback) {
            scan_callback(&device);
        }

        if (ext_report_callback) {
            ext_report_callback(report);
        }

        scan_count++;

        /* 达到扫描数量限制时自动停止（仅触发一次） */
        if (scan_count_limit > 0 && scan_count >= scan_count_limit) {
            ESP_LOGI(TAG, "Scan count limit reached (%d), stopping scan", scan_count_limit);
            scan_count_limit = -1;
            esp_ble_gap_stop_ext_scan();
        }

        break;
    }

    /**
     * 扩展扫描开始完成事件
     */
    case ESP_GAP_BLE_EXT_SCAN_START_COMPLETE_EVT: {
        ESP_LOGI(TAG, "BLE ext scan start complete");
        uart_protocol_send_scan_msg(true);
        break;
    }

    /**
     * 扩展扫描停止完成事件
     */
    case ESP_GAP_BLE_EXT_SCAN_STOP_COMPLETE_EVT: {

        ESP_LOGI(TAG,
                 "BLE ext scan stop complete");

        scan_stop_pending = false;

        if (scan_stop_sem != NULL) {
            xSemaphoreGive(scan_stop_sem);
        }

        uart_protocol_send_scan_status(
            false,
            scan_count
        );
        uart_protocol_send_scan_msg(false);

        break;
    }

    /**
     * 扫描停止事件
     */
    case ESP_GAP_BLE_SCAN_STOP_COMPLETE_EVT: {

        ESP_LOGI(TAG,
                 "BLE scan stop complete");

        scan_stop_pending = false;

        if (scan_stop_sem != NULL) {
            xSemaphoreGive(scan_stop_sem);
        }

        uart_protocol_send_scan_status(
            false,
            scan_count
        );

        break;
    }

    /* ========== Security / Auth 事件处理（来源于 test 代码） ========== */

    case ESP_GAP_BLE_PASSKEY_REQ_EVT: {
        ESP_LOGI(TAG, "ESP_GAP_BLE_PASSKEY_REQ_EVT");
        esp_ble_passkey_reply(param->ble_security.ble_req.bd_addr, true, 0);
        break;
    }

    case ESP_GAP_BLE_NC_REQ_EVT: {
        ESP_LOGI(TAG, "ESP_GAP_BLE_NC_REQ_EVT, passkey=%" PRIu32,
                 param->ble_security.key_notif.passkey);
        esp_ble_confirm_reply(param->ble_security.ble_req.bd_addr, true);
        break;
    }

    case ESP_GAP_BLE_PASSKEY_NOTIF_EVT: {
        ESP_LOGI(TAG, "ESP_GAP_BLE_PASSKEY_NOTIF_EVT, passkey=%06" PRIu32,
                 param->ble_security.key_notif.passkey);
        break;
    }

    case ESP_GAP_BLE_KEY_EVT: {
        const char *key_type_str;
        switch (param->ble_security.ble_key.key_type) {
            case ESP_LE_KEY_PENC:  key_type_str = "ESP_LE_KEY_PENC";  break;
            case ESP_LE_KEY_PID:   key_type_str = "ESP_LE_KEY_PID";   break;
            case ESP_LE_KEY_PCSRK: key_type_str = "ESP_LE_KEY_PCSRK"; break;
            case ESP_LE_KEY_PLK:   key_type_str = "ESP_LE_KEY_PLK";   break;
            case ESP_LE_KEY_LLK:   key_type_str = "ESP_LE_KEY_LLK";   break;
            case ESP_LE_KEY_LENC:  key_type_str = "ESP_LE_KEY_LENC";  break;
            case ESP_LE_KEY_LID:   key_type_str = "ESP_LE_KEY_LID";   break;
            case ESP_LE_KEY_LCSRK: key_type_str = "ESP_LE_KEY_LCSRK"; break;
            default:               key_type_str = "UNKNOWN";          break;
        }
        ESP_LOGI(TAG, "ESP_GAP_BLE_KEY_EVT, key_type=%s", key_type_str);
        break;
    }

    case ESP_GAP_BLE_AUTH_CMPL_EVT: {
        esp_ble_auth_cmpl_t *auth = &param->ble_security.auth_cmpl;
        if (auth->success) {
            ESP_LOGI(TAG, "ESP_GAP_BLE_AUTH_CMPL_EVT: success");
            char bond_info[64];
            snprintf(bond_info, sizeof(bond_info),
                     "bd_addr=%02x:%02x:%02x:%02x:%02x:%02x",
                     auth->bd_addr[0], auth->bd_addr[1], auth->bd_addr[2],
                     auth->bd_addr[3], auth->bd_addr[4], auth->bd_addr[5]);
            uart_protocol_send_auth_ok(bond_info);
        } else {
            ESP_LOGE(TAG, "ESP_GAP_BLE_AUTH_CMPL_EVT: fail, reason=0x%x",
                     auth->fail_reason);
            char fail_info[64];
            snprintf(fail_info, sizeof(fail_info), "reason=0x%x", auth->fail_reason);
            uart_protocol_send_auth_fail(fail_info);
        }
        break;
    }

    case ESP_GAP_BLE_SEC_REQ_EVT: {
        ESP_LOGI(TAG, "ESP_GAP_BLE_SEC_REQ_EVT: accepting");
        esp_ble_gap_security_rsp(param->ble_security.ble_req.bd_addr, true);
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

    scan_stop_sem = xSemaphoreCreateBinary();

    if (scan_stop_sem == NULL) {

        ESP_LOGE(TAG,
                 "Failed to create scan stop semaphore");

        return ESP_ERR_NO_MEM;
    }

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

    scan_stop_pending = true;

    if (scan_stop_sem != NULL) {
        xSemaphoreTake(scan_stop_sem, 0);
    }

    return esp_ble_gap_stop_ext_scan();
}

esp_err_t ble_scan_wait_for_stop(TickType_t timeout)
{
    if (!scan_stop_pending) {
        return ESP_OK;
    }

    if (scan_stop_sem == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    if (xSemaphoreTake(scan_stop_sem, timeout) == pdTRUE) {
        return ESP_OK;
    }

    ESP_LOGW(TAG,
             "Wait for scan stop timed out");

    return ESP_ERR_TIMEOUT;
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
 * @brief 设置扩展广播报告回调
 */
void ble_scan_set_ext_report_callback(
    ble_scan_ext_report_callback_t callback)
{
    ext_report_callback = callback;
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
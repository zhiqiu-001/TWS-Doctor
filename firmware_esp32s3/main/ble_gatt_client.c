/**
 * @file ble_gatt_client.c
 * @brief BLE GATT Client 模块实现
 *
 * 该模块实现 ESP32-S3 作为 BLE Client 连接到 Bose 耳机的功能：
 * - 自动连接指定 MAC
 * - 发现所有 Service/Characteristic UUID
 * - 打印 characteristic properties
 * - 支持 Read / Write / Notify
 *
 * 使用 Bluedroid 协议栈，兼容 ESP-IDF v5.x
 */

#include "ble_gatt_client.h"
#include "esp_log.h"
#include "esp_bt.h"
#include "esp_bt_main.h"
#include "esp_gap_ble_api.h"
#include "esp_gattc_api.h"
#include "esp_gatt_common_api.h"
#include "uart_protocol.h"
#include <string.h>

/* 日志标签 */
static const char *TAG = "BLE_GATTC";

/* GATT 客户端应用 ID */
#define ESP_GATT_APP_ID 0x55

/* 最大 Service/Characteristic 数量 */
#define MAX_SERVICES 32
#define MAX_CHARS_PER_SERVICE 16
#define MAX_CHAR_RESULT 100
#define MAX_DESCR_RESULT 20

/* 全局状态变量 */
static esp_gatt_if_t g_gattc_if = 0;
static uint16_t g_conn_id = 0;
static ble_gattc_state_t g_state = BLE_GATTC_STATE_IDLE;
static esp_bd_addr_t g_target_addr = {0};
static bool g_is_connected = false;
static bool g_gattc_registered = false;

/* Service 信息存储 */
static ble_gatt_service_info_t g_services[MAX_SERVICES];
static uint8_t g_service_count = 0;

/* 回调函数 */
static ble_gattc_state_callback_t g_state_cb = NULL;
static ble_gattc_data_callback_t g_data_cb = NULL;

/**
 * @brief 打印 UUID
 */
static void print_uuid(const char *prefix, const esp_bt_uuid_t *uuid)
{
    if (uuid->len == ESP_UUID_LEN_16) {
        ESP_LOGI(TAG, "%sUUID: 0x%04X", prefix, uuid->uuid.uuid16);
    } else if (uuid->len == ESP_UUID_LEN_32) {
        ESP_LOGI(TAG, "%sUUID: 0x%08X", prefix, uuid->uuid.uuid32);
    } else if (uuid->len == ESP_UUID_LEN_128) {
        ESP_LOGI(TAG, "%sUUID: %02X%02X%02X%02X-%02X%02X-%02X%02X-%02X%02X-%02X%02X%02X%02X%02X%02X",
                 prefix,
                 uuid->uuid.uuid128[15], uuid->uuid.uuid128[14], uuid->uuid.uuid128[13], uuid->uuid.uuid128[12],
                 uuid->uuid.uuid128[11], uuid->uuid.uuid128[10], uuid->uuid.uuid128[9], uuid->uuid.uuid128[8],
                 uuid->uuid.uuid128[7], uuid->uuid.uuid128[6], uuid->uuid.uuid128[5], uuid->uuid.uuid128[4],
                 uuid->uuid.uuid128[3], uuid->uuid.uuid128[2], uuid->uuid.uuid128[1], uuid->uuid.uuid128[0]);
    }
}

/**
 * @brief 打印 Characteristic 属性
 */
static void print_char_properties(esp_gatt_char_prop_t properties)
{
    ESP_LOGI(TAG, "  Properties:");
    if (properties & ESP_GATT_CHAR_PROP_BIT_READ) {
        ESP_LOGI(TAG, "    - READ");
    }
    if (properties & ESP_GATT_CHAR_PROP_BIT_WRITE) {
        ESP_LOGI(TAG, "    - WRITE");
    }
    if (properties & ESP_GATT_CHAR_PROP_BIT_WRITE_NR) {
        ESP_LOGI(TAG, "    - WRITE_NO_RESPONSE");
    }
    if (properties & ESP_GATT_CHAR_PROP_BIT_NOTIFY) {
        ESP_LOGI(TAG, "    - NOTIFY");
    }
    if (properties & ESP_GATT_CHAR_PROP_BIT_INDICATE) {
        ESP_LOGI(TAG, "    - INDICATE");
    }
    if (properties & ESP_GATT_CHAR_PROP_BIT_BROADCAST) {
        ESP_LOGI(TAG, "    - BROADCAST");
    }
}

/**
 * @brief 更新状态并通知回调
 */
static void update_state(ble_gattc_state_t new_state)
{
    g_state = new_state;
    if (g_state_cb) {
        g_state_cb(g_state, g_target_addr);
    }
}

/**
 * @brief 查找 Characteristic 信息
 */
static ble_gatt_char_info_t *find_char_info(const esp_bt_uuid_t *char_uuid)
{
    for (uint8_t i = 0; i < g_service_count; i++) {
        for (uint8_t j = 0; j < g_services[i].char_count; j++) {
            if (g_services[i].chars[j].char_uuid.len == char_uuid->len) {
                if (char_uuid->len == ESP_UUID_LEN_16 && 
                    g_services[i].chars[j].char_uuid.uuid.uuid16 == char_uuid->uuid.uuid16) {
                    return &g_services[i].chars[j];
                }
            }
        }
    }
    return NULL;
}

/**
 * @brief 发现 Service 下的所有 Characteristic
 */
static esp_err_t discover_chars_for_service(uint8_t svc_idx)
{
    if (svc_idx >= g_service_count) {
        return ESP_FAIL;
    }
    
    ble_gatt_service_info_t *svc = &g_services[svc_idx];
    
    ESP_LOGI(TAG, "Discovering characteristics for service %d:", svc_idx + 1);
    print_uuid("  ", &svc->service_uuid);
    
    /* 分配结果缓冲区 */
    esp_gattc_char_elem_t *char_result = malloc(sizeof(esp_gattc_char_elem_t) * MAX_CHAR_RESULT);
    if (!char_result) {
        ESP_LOGE(TAG, "Failed to allocate char result buffer");
        return ESP_ERR_NO_MEM;
    }
    
    uint16_t count = MAX_CHAR_RESULT;
    uint16_t offset = 0;
    
    /* 同步获取所有 Characteristic */
    esp_gatt_status_t status = esp_ble_gattc_get_all_char(
        g_gattc_if, g_conn_id,
        svc->start_handle, svc->end_handle,
        char_result, &count, offset);
    
    if (status == ESP_GATT_OK) {
        ESP_LOGI(TAG, "  Found %d characteristics", count);
        svc->char_count = (count < MAX_CHARS_PER_SERVICE) ? count : MAX_CHARS_PER_SERVICE;
        
        for (uint16_t i = 0; i < svc->char_count; i++) {
            ble_gatt_char_info_t *ch = &svc->chars[i];
            memcpy(&ch->char_uuid, &char_result[i].uuid, sizeof(esp_bt_uuid_t));
            ch->char_handle = char_result[i].char_handle;
            ch->properties = char_result[i].properties;
            ch->descr_handle = 0;
            
            ESP_LOGI(TAG, "  Char[%d]:", i + 1);
            print_uuid("    ", &ch->char_uuid);
            ESP_LOGI(TAG, "    Handle: 0x%04X", ch->char_handle);
            print_char_properties(ch->properties);
            
            /* 获取 CCCD 描述符 */
            esp_gattc_descr_elem_t descr_result[MAX_DESCR_RESULT] = {0};
            uint16_t descr_count = MAX_DESCR_RESULT;
            
            status = esp_ble_gattc_get_all_descr(
                g_gattc_if, g_conn_id,
                ch->char_handle,
                descr_result, &descr_count, 0);
            
            if (status == ESP_GATT_OK) {
                for (uint16_t d = 0; d < descr_count; d++) {
                    if (descr_result[d].uuid.len == ESP_UUID_LEN_16 &&
                        descr_result[d].uuid.uuid.uuid16 == ESP_GATT_UUID_CHAR_CLIENT_CONFIG) {
                        ch->descr_handle = descr_result[d].handle;
                        ESP_LOGI(TAG, "    CCCD Handle: 0x%04X", ch->descr_handle);
                    }
                }
            }
        }
    } else {
        ESP_LOGE(TAG, "  esp_ble_gattc_get_all_char failed: %d", status);
    }
    
    free(char_result);
    return status;
}

/**
 * @brief 发现所有 Service
 */
static void discover_all_services(void)
{
    ESP_LOGI(TAG, "Starting service discovery...");
    
    /* 分配 Service 结果缓冲区 */
    esp_gattc_service_elem_t *service_result = malloc(sizeof(esp_gattc_service_elem_t) * MAX_SERVICES);
    if (!service_result) {
        ESP_LOGE(TAG, "Failed to allocate service result buffer");
        return;
    }
    
    uint16_t count = MAX_SERVICES;
    uint16_t offset = 0;
    
    /* 遍历所有 Service - 每次获取一个 */
    g_service_count = 0;
    
    while (g_service_count < MAX_SERVICES) {
        count = 1;  /* 每次只查一个 */
        esp_gatt_status_t status = esp_ble_gattc_get_service(
            g_gattc_if, g_conn_id,
            NULL,  /* 遍历所有 service */
            &service_result[g_service_count],
            &count, offset);
        
        if (status != ESP_GATT_OK || count == 0) {
            break;
        }
        
        ble_gatt_service_info_t *svc = &g_services[g_service_count];
        memcpy(&svc->service_uuid, &service_result[g_service_count].uuid, sizeof(esp_bt_uuid_t));
        svc->start_handle = service_result[g_service_count].start_handle;
        svc->end_handle = service_result[g_service_count].end_handle;
        svc->char_count = 0;
        
        ESP_LOGI(TAG, "Service[%d]:", g_service_count + 1);
        print_uuid("  ", &svc->service_uuid);
        ESP_LOGI(TAG, "  Handle: 0x%04X - 0x%04X", svc->start_handle, svc->end_handle);
        
        g_service_count++;
        offset++;  /* 移动到下一个 */
    }
    
    ESP_LOGI(TAG, "Total services found: %d", g_service_count);
    
    free(service_result);
    
    /* 发现每个 Service 的 Characteristic */
    for (uint8_t i = 0; i < g_service_count; i++) {
        discover_chars_for_service(i);
    }
    
    ESP_LOGI(TAG, "=== Service Discovery Complete ===");
    g_is_connected = true;
}

/**
 * @brief GATT 客户端事件处理回调
 */
static void gattc_event_handler(esp_gattc_cb_event_t event, esp_gatt_if_t gattc_if, esp_ble_gattc_cb_param_t *param)
{
    switch (event) {
        case ESP_GATTC_REG_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_REG_EVT, status=%d, app_id=%d", 
                     param->reg.status, param->reg.app_id);
            if (param->reg.status == ESP_GATT_OK) {
                g_gattc_if = gattc_if;
                g_gattc_registered = true;
            }
            break;
        }
        
        case ESP_GATTC_OPEN_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_OPEN_EVT, status=%d, conn_id=%d, mtu=%d",
                     param->open.status, param->open.conn_id, param->open.mtu);
            if (param->open.status == ESP_GATT_OK) {
                g_conn_id = param->open.conn_id;
                memcpy(g_target_addr, param->open.remote_bda, sizeof(esp_bd_addr_t));
                update_state(BLE_GATTC_STATE_CONNECTED);
                
                /* 发送 Bose 连接成功通知到上位机 */
                uart_protocol_send_bose_connected("Bose TWS Device", "Unknown");
                
                /* 开始发现服务 */
                discover_all_services();
            } else {
                ESP_LOGE(TAG, "Open failed, status=%d", param->open.status);
                uart_protocol_send_bose_error("Connection failed");
                update_state(BLE_GATTC_STATE_IDLE);
            }
            break;
        }
        
        case ESP_GATTC_CONNECT_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_CONNECT_EVT, conn_id=%d", param->connect.conn_id);
            break;
        }
        
        case ESP_GATTC_DISCONNECT_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_DISCONNECT_EVT, conn_id=%d, reason=0x%x",
                     param->disconnect.conn_id, param->disconnect.reason);
            g_conn_id = 0;
            g_is_connected = false;
            g_service_count = 0;
            update_state(BLE_GATTC_STATE_DISCONNECTED);
            
            /* 发送 Bose 断开连接通知到上位机 */
            uart_protocol_send_bose_disconnected();
            break;
        }
        
        case ESP_GATTC_SEARCH_RES_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_SEARCH_RES_EVT");
            break;
        }
        
        case ESP_GATTC_SEARCH_CMPL_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_SEARCH_CMPL_EVT, status=%d", param->search_cmpl.status);
            break;
        }
        
        case ESP_GATTC_READ_CHAR_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_READ_CHAR_EVT, status=%d, handle=0x%04X",
                     param->read.status, param->read.handle);
            if (param->read.status == ESP_GATT_OK && param->read.value_len > 0) {
                ESP_LOGI(TAG, "  Value (%d bytes):", param->read.value_len);
                for (int i = 0; i < param->read.value_len; i++) {
                    printf(" %02X", param->read.value[i]);
                }
                printf("\n");
            }
            break;
        }
        
        case ESP_GATTC_WRITE_CHAR_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_WRITE_CHAR_EVT, status=%d, handle=0x%04X",
                     param->write.status, param->write.handle);
            break;
        }
        
        case ESP_GATTC_NOTIFY_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_NOTIFY_EVT, handle=0x%04X, is_notify=%d, length=%d",
                     param->notify.handle, param->notify.is_notify, param->notify.value_len);
            ESP_LOGI(TAG, "  Value:");
            for (int i = 0; i < param->notify.value_len; i++) {
                printf(" %02X", param->notify.value[i]);
            }
            printf("\n");
            
            /* 查找对应的 Characteristic 并调用回调 */
            if (g_data_cb) {
                for (uint8_t i = 0; i < g_service_count; i++) {
                    for (uint8_t j = 0; j < g_services[i].char_count; j++) {
                        if (g_services[i].chars[j].char_handle == param->notify.handle) {
                            g_data_cb(&g_services[i].chars[j].char_uuid, 
                                     param->notify.value, param->notify.value_len);
                            break;
                        }
                    }
                }
            }
            break;
        }
        
        case ESP_GATTC_CFG_MTU_EVT: {
            ESP_LOGI(TAG, "ESP_GATTC_CFG_MTU_EVT, mtu=%d", param->cfg_mtu.mtu);
            break;
        }
        
        default:
            ESP_LOGI(TAG, "GATTC event: %d", event);
            break;
    }
}

esp_err_t ble_gatt_client_init(void)
{
    ESP_LOGI(TAG, "Initializing BLE GATT Client...");
    
    /* 先注册回调 */
    esp_err_t ret = esp_ble_gattc_register_callback(gattc_event_handler);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_ble_gattc_register_callback failed: %s",
                 esp_err_to_name(ret));
        return ret;
    }

    /* 再注册 APP */
    ret = esp_ble_gattc_app_register(ESP_GATT_APP_ID);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_ble_gattc_app_register failed: %s",
                 esp_err_to_name(ret));
        return ret;
    }

    ESP_LOGI(TAG, "BLE GATT Client init success");
    return ESP_OK;
}

esp_err_t ble_gatt_client_connect(const esp_bd_addr_t addr, esp_ble_addr_type_t addr_type)
{
    ESP_LOGI(TAG, "Connecting to device...");
    ESP_LOGI(TAG, "  Address: %02X:%02X:%02X:%02X:%02X:%02X",
             addr[0], addr[1], addr[2], addr[3], addr[4], addr[5]);
    ESP_LOGI(TAG, "  Address Type: %d", addr_type);

    if (!g_gattc_registered) {
        ESP_LOGE(TAG, "GATT client not registered");
        return ESP_ERR_INVALID_STATE;
    }
    
    memcpy(g_target_addr, addr, sizeof(esp_bd_addr_t));
    update_state(BLE_GATTC_STATE_CONNECTING);
    
    /* 打开 GATT 连接 - 使用增强型 API */
    esp_ble_gatt_creat_conn_params_t conn_params = {
        .own_addr_type = BLE_ADDR_TYPE_PUBLIC,
        .remote_addr_type = addr_type,
        .is_direct = true,
        .is_aux = false,
        .phy_mask = 0,
    };
    memcpy(conn_params.remote_bda, g_target_addr, sizeof(esp_bd_addr_t));

    esp_err_t ret = esp_ble_gattc_enh_open(g_gattc_if, &conn_params);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_ble_gattc_open failed: %s", esp_err_to_name(ret));
        update_state(BLE_GATTC_STATE_IDLE);
        return ret;
    }
    
    return ESP_OK;
}

esp_err_t ble_gatt_client_disconnect(void)
{
    ESP_LOGI(TAG, "Disconnecting...");
    
    if (g_conn_id == 0) {
        ESP_LOGW(TAG, "Not connected");
        return ESP_ERR_INVALID_STATE;
    }
    
    update_state(BLE_GATTC_STATE_DISCONNECTING);
    
    esp_err_t ret = esp_ble_gattc_close(g_gattc_if, g_conn_id);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_ble_gattc_close failed: %s", esp_err_to_name(ret));
        return ret;
    }
    
    return ESP_OK;
}

void ble_gatt_client_set_state_callback(ble_gattc_state_callback_t callback)
{
    g_state_cb = callback;
}

void ble_gatt_client_set_data_callback(ble_gattc_data_callback_t callback)
{
    g_data_cb = callback;
}

esp_err_t ble_gatt_client_read_char(const esp_bt_uuid_t *char_uuid)
{
    if (!g_is_connected) {
        ESP_LOGE(TAG, "Not connected");
        return ESP_ERR_INVALID_STATE;
    }
    
    ble_gatt_char_info_t *ch = find_char_info(char_uuid);
    if (!ch) {
        ESP_LOGE(TAG, "Characteristic not found");
        return ESP_ERR_NOT_FOUND;
    }
    
    ESP_LOGI(TAG, "Reading characteristic:");
    print_uuid("  ", char_uuid);
    
    esp_err_t ret = esp_ble_gattc_read_char(g_gattc_if, g_conn_id, ch->char_handle,
                                            ESP_GATT_AUTH_REQ_NONE);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_ble_gattc_read_char failed: %s", esp_err_to_name(ret));
    }
    
    return ret;
}

esp_err_t ble_gatt_client_write_char(const esp_bt_uuid_t *char_uuid, const uint8_t *data, uint16_t len)
{
    if (!g_is_connected) {
        ESP_LOGE(TAG, "Not connected");
        return ESP_ERR_INVALID_STATE;
    }
    
    ble_gatt_char_info_t *ch = find_char_info(char_uuid);
    if (!ch) {
        ESP_LOGE(TAG, "Characteristic not found");
        return ESP_ERR_NOT_FOUND;
    }
    
    ESP_LOGI(TAG, "Writing characteristic:");
    print_uuid("  ", char_uuid);
    ESP_LOGI(TAG, "  Data (%d bytes):", len);
    for (int i = 0; i < len; i++) {
        printf(" %02X", data[i]);
    }
    printf("\n");
    
    esp_err_t ret = esp_ble_gattc_write_char(g_gattc_if, g_conn_id, ch->char_handle,
                                              len, (uint8_t *)data,
                                              ESP_GATT_WRITE_TYPE_NO_RSP,
                                              ESP_GATT_AUTH_REQ_NONE);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_ble_gattc_write_char failed: %s", esp_err_to_name(ret));
    }
    
    return ret;
}

esp_err_t ble_gatt_client_set_notify(const esp_bt_uuid_t *char_uuid, bool enable)
{
    if (!g_is_connected) {
        ESP_LOGE(TAG, "Not connected");
        return ESP_ERR_INVALID_STATE;
    }
    
    ble_gatt_char_info_t *ch = find_char_info(char_uuid);
    if (!ch) {
        ESP_LOGE(TAG, "Characteristic not found");
        return ESP_ERR_NOT_FOUND;
    }
    
    if (ch->descr_handle == 0) {
        ESP_LOGE(TAG, "CCCD descriptor not found");
        return ESP_ERR_NOT_FOUND;
    }
    
    ESP_LOGI(TAG, "%s notify:", enable ? "Enabling" : "Disabling");
    print_uuid("  ", char_uuid);
    
    /* 先注册 notify */
    esp_err_t ret = esp_ble_gattc_register_for_notify(g_gattc_if, g_target_addr, ch->char_handle);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_ble_gattc_register_for_notify failed: %s", esp_err_to_name(ret));
    }
    
    /* 写入 CCCD 值 */
    uint8_t value[2] = {0};
    if (enable) {
        if (ch->properties & ESP_GATT_CHAR_PROP_BIT_NOTIFY) {
            value[0] = 0x01;
        } else if (ch->properties & ESP_GATT_CHAR_PROP_BIT_INDICATE) {
            value[0] = 0x02;
        }
    }
    
    ret = esp_ble_gattc_write_char_descr(g_gattc_if, g_conn_id, ch->descr_handle,
                                          sizeof(value), value,
                                          ESP_GATT_WRITE_TYPE_NO_RSP,
                                          ESP_GATT_AUTH_REQ_NONE);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "esp_ble_gattc_write_char_descr failed: %s", esp_err_to_name(ret));
    }
    
    return ret;
}

ble_gattc_state_t ble_gatt_client_get_state(void)
{
    return g_state;
}

uint8_t ble_gatt_client_get_service_count(void)
{
    return g_service_count;
}

const ble_gatt_service_info_t *ble_gatt_client_get_service(uint8_t index)
{
    if (index >= g_service_count) {
        return NULL;
    }
    return &g_services[index];
}

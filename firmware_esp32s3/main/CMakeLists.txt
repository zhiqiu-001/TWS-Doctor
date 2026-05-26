idf_component_register(
    SRCS "ble_gatt_client.c" "main.c"
         "ble_scan.c"
         "bt_classic_scan.c"
         "tws_manager.c"
         "bond_manager.c"
         "uart_protocol.c"
         "state_machine.c"
    INCLUDE_DIRS "."
    REQUIRES bt driver nvs_flash logger
)

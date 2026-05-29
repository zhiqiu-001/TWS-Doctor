$env:IDF_PATH = 'C:\Espressif\frameworks\esp-idf-v5.4.1'
$env:IDF_PYTHON_ENV_PATH = 'C:\Espressif\python_env\idf5.4_py3.11_env'
$env:PYTHONUTF8 = '1'
$env:ESP_ROM_ELF_DIR = '.'

# Use the older toolchain that matches ESP-IDF v5.4.1 expected version
$env:PATH = 'C:\Espressif\tools\cmake\3.30.2\bin;C:\Espressif\tools\ninja\1.12.1;C:\Espressif\tools\idf-git\2.44.0\bin;C:\Espressif\tools\idf-git\2.44.0\usr\bin;C:\Espressif\tools\xtensa-esp-elf\esp-14.2.0_20241119\xtensa-esp-elf\bin;C:\Espressif\python_env\idf5.4_py3.11_env\Scripts;C:\Espressif\frameworks\esp-idf-v5.4.1\tools;' + $env:PATH

Set-Location 'C:\Users\18980\Documents\GitHub\TWS-Doctor\firmware_esp32s3'

# Full clean first to remove old cached paths
& 'C:\Espressif\python_env\idf5.4_py3.11_env\Scripts\python.exe' 'C:\Espressif\frameworks\esp-idf-v5.4.1\tools\idf.py' fullclean

& 'C:\Espressif\python_env\idf5.4_py3.11_env\Scripts\python.exe' 'C:\Espressif\frameworks\esp-idf-v5.4.1\tools\idf.py' build
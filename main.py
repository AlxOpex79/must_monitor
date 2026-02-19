import requests
import time

# --- ВСТАВЬ СВОИ ДАННЫЕ МЕЖДУ КАВЫЧЕК ---
TOKEN = "8257997232:AAH2tUt_zQbBgbnG12U6jbD3KX807gWkAoY"
CHAT_ID = "-5285339655"
USER = "2774205@gmail.com"
PASS = "020352vO"

# Данные твоего Wi-Fi модуля
SN = "E0A25C000919"
KEY = "57B61F72"

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text})

last_status = True # Свет есть

send("✅ Бот мониторинга в Боярке запущен и на связи!")

while True:
    try:
        # Запрос к облаку PVPro
        res = requests.get(f"http://api.dessmonitor.com/v1/device/getDeviceData?sn={SN}").json()
        
        # Обычно в PVPro напряжение сети это параметр 'v_grid' или 'u_a'
        # Если API выдает ошибку, мы это поправим, когда увидим ответ сервера
        grid = res.get('v_grid', 220) 
        
        if grid < 50 and last_status:
            send("🔌Свет отключили!!!! Работаем от батарей.")
            last_status = False
        elif grid > 180 and not last_status:
            send("⚡️ Свет ДАЛИ! Начинаю зарядку.")
            last_status = True
            
    except Exception as e:
        print(f"Ошибка: {e}")
        
    time.sleep(60) # Проверка каждую минуту

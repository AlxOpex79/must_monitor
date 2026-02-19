import os
import requests
import time

# Данные из секретных настроек
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
USER = os.environ.get('PV_LOGIN')
PASS = os.environ.get('PV_PASS')

SN = "E0A25C000919"

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text})

last_status = True  # Свет есть
last_battery = 100

send("✅ Холов ворлдс и кожанные мешки!!! Ваш ЕНЕРГИЯ БОТ приветствует, и теперь будет следить за светом! БУГАГАГА!!!")

while True:
    try:
        # Запрос к облаку
        res = requests.get(f"http://api.dessmonitor.com/v1/device/getDeviceData?sn={SN}").json()
        
        # Вытаскиваем данные
        # 'v_grid' - напряжение сети, 'soc' - заряд батареи в %
        grid = res.get('v_grid', 220)
        battery = res.get('soc', 0) 
        
        # 1. Если свет ОТКЛЮЧИЛИ
        if grid < 50 and last_status:
            send(f"🔌 Свет в оя ОТКЛЮЧИЛИ! Работаем от батарей.\n🔋 Заряд: {battery}%")
            last_status = False
            
        # 2. Если свет ДАЛИ
        elif grid > 180 and not last_status:
            send(f"⚡️ Свет в оя ДАЛИ! Начинаю зарядку.\n🔋 Текущий заряд: {battery}%")
            last_status = True
            
        # 3. Предупреждение о низком заряде (если света нет и упало ниже 20%)
        if not last_status and battery <= 20 and last_battery > 20:
            send(f"⚠️ ВНИМАНИЕ! Батарея в оя почти разряжена: {battery}%!")
            
        last_battery = battery

    except Exception as e:
        print(f"Ошибка: {e}")
        
    time.sleep(60) # Проверка каждую минуту

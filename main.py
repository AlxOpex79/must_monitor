import os
import requests
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
SN = "E0A25C000919"

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text})

def get_data():
    try:
        # Пытаемся получить данные
        res = requests.get(f"http://api.dessmonitor.com/v1/device/getDeviceData?sn={SN}").json()
        data = res.get('datList', res) # Проверяем вложенность
        
        # Ищем вольтаж (пробуем разные ключи)
        grid = data.get('v_grid') or data.get('u_a') or data.get('vgrid', 220)
        
        # Ищем батарею (пробуем разные ключи)
        battery = data.get('soc') or data.get('capacity') or data.get('battery_soc', 0)
        
        return grid, battery
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return None, None

def check_messages():
    try:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1&timeout=1").json()
        if updates.get('result'):
            msg = updates['result'][0].get('message', {})
            text = msg.get('text', '').lower()
            
            if text == "статус":
                v, bat = get_data()
                send(f"📊 Состояние в оя:\n⚡️ Сеть: {v}V\n🔋 Батарея: {bat}%")
                # Подтверждаем получение, чтобы не спамить
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={updates['result'][0]['update_id'] + 1}")
    except:
        pass

last_status = True 

send("🚀 Дал я в штангу! Сорян, кожанные! Сейчас проверим. Пробуй команду 'статус'.")

while True:
    grid, battery = get_data()
    
    if grid is not None and isinstance(grid, (int, float)):
        if grid < 50 and last_status:
            send(f"🔌 Свет ОТКЛЮЧИЛИ!\n🔋 Заряд: {battery}%")
            last_status = False
        elif grid > 180 and not last_status:
            send(f"⚡️ Свет ДАЛИ!\n🔋 Заряд: {battery}%")
            last_status = True
    
    check_messages()
    time.sleep(5)

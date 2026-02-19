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
        res = requests.get(f"http://api.dessmonitor.com/v1/device/getDeviceData?sn={SN}").json()
        grid = res.get('v_grid', 220)
        battery = res.get('soc', 0)
        return grid, battery
    except:
        return None, None

def check_messages():
    try:
        # Проверяем последние сообщения в боте
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1").json()
        if updates['result']:
            last_msg = updates['result'][0]['message']['text']
            if last_msg.lower() == "статус":
                v, bat = get_data()
                send(f"📊 Текущее состояние в оя:\n⚡️ Сеть: {v}V\n🔋 Батарея: {bat}%")
                # "Очищаем" сообщение, чтобы не отвечать на него бесконечно
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={updates['result'][0]['update_id'] + 1}")
    except:
        pass

last_status = True 

send("✅ Кожанные мешки! Теперь я знаю про ваш свет ВСЕ и понимаю команду 'статус'!")

while True:
    grid, battery = get_data()
    
    if grid is not None:
        # Логика уведомлений при смене статуса света
        if grid < 50 and last_status:
            send(f"🔌 Свет ОТКЛЮЧИЛИ!\n🔋 Заряд: {battery}%")
            last_status = False
        elif grid > 180 and not last_status:
            send(f"⚡️ Свет ДАЛИ!\n🔋 Заряд: {battery}%")
            last_status = True
    
    # Проверяем, не спросил ли ты статус
    check_messages()
    
    time.sleep(10) # Уменьшил время ожидания до 10 сек, чтобы бот быстрее отвечал

import os
import requests
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
SN = "E0A25C000919"

def send(text):
    # Ограничим длину текста, чтобы Telegram не ругался
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": str(text)[:4000]})

def get_raw_data():
    try:
        # Получаем абсолютно все данные от инвертора
        res = requests.get(f"http://api.dessmonitor.com/v1/device/getDeviceData?sn={SN}").json()
        return res
    except Exception as e:
        return f"Ошибка связи: {e}"

def check_messages():
    try:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1&timeout=1").json()
        if updates.get('result'):
            msg = updates['result'][0].get('message', {})
            text = msg.get('text', '').lower()
            
            if text == "статус":
                raw_data = get_raw_data()
                # Бот пришлет "сырые" данные, чтобы мы нашли нужные ключи
                send(f"🔍 Ищу данные в оя...\nОтвет сервера: {raw_data}")
                
                # Подтверждаем, чтобы не повторять ответ
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={updates['result'][0]['update_id'] + 1}")
    except:
        pass

send("🛠 Чейто я кривой. Хотя, какой разраб, такой и Бот.  Пиши 'статус'!")

while True:
    check_messages()
    time.sleep(5)

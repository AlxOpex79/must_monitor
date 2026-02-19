import os
import requests
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
# Твой уникальный ключ из первого сообщения
KEY = "8c660f64483a48e89921473489830573" 
SN = "E0A25C000919"

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text})

def get_data():
    try:
        # Прямой запрос по ключу и серийнику
        url = f"http://api.dessmonitor.com/v1/device/getDeviceData?sn={SN}&key={KEY}"
        res = requests.get(url, timeout=15).json()
        
        data = res.get('datList', {})
        grid = data.get('v_grid', '???')
        battery = data.get('soc', '??')
        
        return grid, battery
    except Exception:
        return "Облако не пускает", "🛡"

def check_messages():
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1&timeout=1").json()
        if r.get('result'):
            msg = r['result'][0].get('message', {})
            if msg.get('text', '').lower() == "статус":
                v, bat = get_data()
                send(f"📊 Состояние дома:\n⚡️ Сеть: {v}V\n🔋 Батарея: {bat}%")
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={r['result'][0]['update_id'] + 1}")
    except: pass

send("⚡️ Бот перешел на упрощенный протокол. Жду 'статус'!")

while True:
    check_messages()
    time.sleep(5)

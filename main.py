import os
import requests
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
USER = os.environ.get('PV_LOGIN')
PASS = os.environ.get('PV_PASS')
SN = "E0A25C000919"

# Заголовки, чтобы прикинуться браузером
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text})

def get_data():
    try:
        # 1. Пробуем авторизоваться
        auth_url = f"http://api.dessmonitor.com/v1/public/login?loginName={USER}&password={PASS}"
        auth_res = requests.post(auth_url, headers=HEADERS, timeout=10).json()
        
        token = auth_res.get('datList', {}).get('tokenId')
        if not token:
            return "Ошибка логина (проверь PV_LOGIN/PV_PASS в Render)", "❌"

        # 2. Идем за данными
        data_url = f"http://api.dessmonitor.com/v1/device/getDeviceData?sn={SN}&tokenId={token}"
        res = requests.get(data_url, headers=HEADERS, timeout=10).json()
        
        details = res.get('datList', {})
        grid = details.get('v_grid', 'Нет сети')
        battery = details.get('soc', '??')
        
        return grid, battery
    except Exception as e:
        return f"Ошибка связи с облаком", "⚠️"

def check_messages():
    try:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1&timeout=1").json()
        if updates.get('result'):
            msg = updates['result'][0].get('message', {})
            if msg.get('text', '').lower() == "статус":
                v, bat = get_data()
                send(f"📊 Состояние :\n⚡️ Сеть: {v}V\n🔋 Батарея: {bat}%")
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={updates['result'][0]['update_id'] + 1}")
    except:
        pass

last_status = True
send("🛰 Поиграю в ИНВИЗИБЕЛМЕНА. Запущен в режиме 'невидимки'. Жду команду статус!")

while True:
    grid, battery = get_data()
    # Проверка света в фоне
    if isinstance(grid, (int, float)):
        if grid < 50 and last_status:
            send(f"🔌 Свет дома ОТКЛЮЧИЛИ!\n🔋 Заряд: {battery}%")
            last_status = False
        elif grid > 180 and not last_status:
            send(f"⚡️ Свет дома ДАЛИ!\n🔋 Заряд: {battery}%")
            last_status = True
            
    check_messages()
    time.sleep(10)

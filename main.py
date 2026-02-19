import os
import requests
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
USER = os.environ.get('PV_LOGIN')
PASS = os.environ.get('PV_PASS')
SN = "E0A25C000919"

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text})

def get_data():
    try:
        session = requests.Session()
        # НОВЫЙ АДРЕС: Используем поддомен 'server' вместо 'api'
        auth_url = "http://server.dessmonitor.com/v1/public/login"
        auth_data = {"loginName": USER, "password": PASS}
        
        auth_res = session.post(auth_url, json=auth_data, timeout=15).json()
        token = auth_res.get('datList', {}).get('tokenId')
        
        if not token:
            return "Ошибка логина (проверь данные в Render)", "❌"

        # Получаем данные через актуальный адрес
        data_url = f"http://server.dessmonitor.com/v1/device/getDeviceData?sn={SN}&tokenId={token}"
        data_res = session.get(data_url, timeout=15).json()
        
        datList = data_res.get('datList', {})
        grid = datList.get('v_grid', '???')
        battery = datList.get('soc', '??')
        
        return grid, battery
    except Exception as e:
        return f"Облако недоступно: {e}", "⚠️"

def check_messages():
    try:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1&timeout=1").json()
        if updates.get('result'):
            msg = updates['result'][0].get('message', {})
            if msg.get('text', '').lower() == "статус":
                v, bat = get_data()
                send(f"📊 Состояние дома:\n⚡️ Сеть: {v}V\n🔋 Батарея: {bat}%")
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={updates['result'][0]['update_id'] + 1}")
    except:
        pass

send("✅ Бот обновлен на новый сервер! Пробуй 'статус'.")

while True:
    check_messages()
    time.sleep(10)

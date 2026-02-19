import os
import httpx
import time
import requests

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
USER = os.environ.get('PV_LOGIN')
PASS = os.environ.get('PV_PASS')
SN = "E0A25C000919"

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text})

def get_data():
    # Используем httpx вместо requests для лучшей работы с HTTP/2
    with httpx.Client(http2=True, timeout=20.0) as client:
        try:
            # 1. Логинимся через другой шлюз
            auth_url = "http://server.dessmonitor.com/v1/public/login"
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15"
            }
            auth_payload = {"loginName": USER, "password": PASS}
            
            auth_res = client.post(auth_url, json=auth_payload, headers=headers)
            
            if auth_res.status_code != 200:
                return f"Сервер ответил кодом {auth_res.status_code}", "❌"
            
            data_json = auth_res.json()
            token = data_json.get('datList', {}).get('tokenId')
            
            if not token:
                return "Логин не прошел. Проверь PV_LOGIN в Render", "🔑"

            # 2. Получаем данные
            data_url = f"http://server.dessmonitor.com/v1/device/getDeviceData?sn={SN}&tokenId={token}"
            res = client.get(data_url, headers=headers)
            
            final_data = res.json().get('datList', {})
            grid = final_data.get('v_grid', '???')
            battery = final_data.get('soc', '??')
            
            return grid, battery
            
        except Exception as e:
            return f"Тех. ошибка: {str(e)[:50]}", "⚠️"

def check_messages():
    try:
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1&timeout=1").json()
        if r.get('result'):
            msg = r['result'][0].get('message', {})
            if msg.get('text', '').lower() == "статус":
                v, bat = get_data()
                send(f"📊 Состояние дома:\n⚡️ Сеть: {v}V\n🔋 Батарея: {bat}%")
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={r['result'][0]['update_id'] + 1}")
    except:
        pass

send("🚀 Бот  перезапущен. Пробуй 'статус' еще раз!")

while True:
    check_messages()
    time.sleep(5)

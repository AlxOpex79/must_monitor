import os
import requests
import time

# Берем твои секреты из настроек Render
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
        # 1. Сначала логинимся, чтобы сервер нас узнал
        auth_url = f"http://api.dessmonitor.com/v1/public/login?loginName={USER}&password={PASS}"
        auth_res = requests.post(auth_url).json()
        token = auth_res.get('datList', {}).get('tokenId')

        if not token:
            return "Ошибка авторизации (проверь логин/пароль)", ""

        # 2. Теперь с этим токеном идем за данными устройства
        data_url = f"http://api.dessmonitor.com/v1/device/getDeviceData?sn={SN}&tokenId={token}"
        res = requests.get(data_url).json()
        
        # Вытаскиваем конкретные цифры
        details = res.get('datList', {})
        grid = details.get('v_grid', '???')
        battery = details.get('soc', '???')
        
        return grid, battery
    except Exception as e:
        return f"Ошибка: {e}", ""

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

send("🔄 Я перезагружен с авторизацией. Пробуй 'статус'!")

while True:
    check_messages()
    time.sleep(5)

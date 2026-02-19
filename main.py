import os
import requests
import time

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
# Твоя ссылка от Google для обхода блокировок
GOOGLE_URL = "https://script.google.com/macros/s/AKfycbysv5SSHAIHe2Z6x-kkLm1ZSyThjquysReZzOdkrsHmLkLx0VBQ71ZZ38PsP4XggMM2/exec"

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                  json={"chat_id": CHAT_ID, "text": text})

def get_data():
    try:
        # Запрашиваем данные через Google
        res = requests.get(GOOGLE_URL, timeout=25).json()
        
        # Вытаскиваем значения из ответа
        datList = res.get('datList', {})
        if not datList:
            return "Облако пустое", "❓"
            
        grid = datList.get('v_grid', '???')
        battery = datList.get('soc', '??')
        
        return grid, battery
    except Exception as e:
        print(f"Error: {e}")
        return "Ошибка связи через Google", "⚠️"

def check_messages():
    try:
        # Проверка команд в Telegram
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1&timeout=1").json()
        if r.get('result'):
            msg = r['result'][0].get('message', {})
            if msg.get('text', '').lower() == "статус":
                v, bat = get_data()
                send(f"📊 Состояние дома:\n⚡️ Сеть: {v}V\n🔋 Батарея: {bat}%")
                # Подтверждаем получение сообщения
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={r['result'][0]['update_id'] + 1}")
    except:
        pass

send("🎯 Бот успешно переключен на мост через Google! Пиши 'статус'.")

while True:
    check_messages()
    time.sleep(5)

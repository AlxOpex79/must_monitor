import os
import requests
import time

# Загружаем настройки из Render
TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Твоя ссылка-мост от Google
GOOGLE_URL = "https://script.google.com/macros/s/AKfycbysv5SSHAIHe2Z6x-kkLm1ZSyThjquysReZzOdkrsHmLkLx0VBQ71ZZ38PsP4XggMM2/exec"

def send(text):
    """Отправка сообщения в Telegram"""
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", 
                      json={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def get_data():
    """Получение данных через Google Apps Script"""
    try:
        # ВАЖНО: добавили allow_redirects=True для работы с Google Scripts
        res = requests.get(GOOGLE_URL, timeout=25, allow_redirects=True).json()
        
        datList = res.get('datList', {})
        if not datList:
            return "Облако прислало пустой ответ", "❓"
            
        # Вытаскиваем вольтаж сети и заряд батареи
        grid = datList.get('v_grid', '???')
        battery = datList.get('soc', '??')
        
        return grid, battery
    except Exception as e:
        print(f"Ошибка получения данных: {e}")
        return "Ошибка связи через Google", "⚠️"

def check_messages():
    """Проверка новых сообщений в боте"""
    try:
        # Берем последнее сообщение
        r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1&timeout=1").json()
        if r.get('result'):
            update = r['result'][0]
            msg = update.get('message', {})
            text = msg.get('text', '').lower()
            update_id = update['update_id']

            # Если пришла команда 'статус'
            if text == "статус":
                v, bat = get_data()
                response = f"📊 Состояние дома:\n⚡️ Сеть: {v}V\n🔋 Батарея: {bat}%"
                send(response)
                
                # Помечаем сообщение как прочитанное
                requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={update_id + 1}")
    except:
        pass

# Приветственное сообщение при запуске
send("🚀 Бот  обновлен! Теперь мост Google должен работать. Жду команду 'статус'.")

# Основной цикл работы
while True:
    check_messages()
    time.sleep(5)  # Проверка каждые 5 секунд

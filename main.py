import os, requests, time

TOKEN = os.environ.get('BOT_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
USER = os.environ.get('PV_LOGIN')
PASS = os.environ.get('PV_PASS')

def send(text):
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT_ID, "text": text})

def get_status():
    try:
        # Проверяем только вход
        auth_url = "http://api.dessmonitor.com/v1/public/login"
        r = requests.post(auth_url, json={"loginName": USER, "password": PASS}, timeout=10)
        return f"Ответ сервера: {r.status_code}\nТекст: {r.text[:200]}"
    except Exception as e:
        return f"Ошибка: {e}"

send("🩺 Запускаю диагностику в оя. Пиши 'статус'!")

while True:
    try:
        updates = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=-1").json()
        if updates.get('result') and updates['result'][0]['message']['text'].lower() == "статус":
            res = get_status()
            send(res)
            requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={updates['result'][0]['update_id'] + 1}")
    except: pass
    time.sleep(5)

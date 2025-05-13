import os
import time
import requests
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
from zoneinfo import ZoneInfo  # desde Python 3.9+

load_dotenv()

def colombia_to_utc(hour, minute):
    """
    Convierte la hora de Colombia (UTC−5) a UTC.
    """
    utc_hour = (hour + 5) % 24
    print(f"⏰ Colombia time: {hour:02d}:{minute:02d} → UTC time: {utc_hour:02d}:{minute:02d}")
    return utc_hour, minute

def get_colombia_time_str():
    """
    Retorna el tiempo actual en zona horaria de Colombia como string.
    """
    return datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S %Z")

def wait_for_api(url, timeout=60):
    """
    Espera hasta que la API esté disponible o se alcance el timeout.
    """
    print("⏳ Waiting for API to become available...")
    for _ in range(timeout):
        try:
            response = requests.get(url)
            if response.status_code in [200, 404]:  # 404 también indica que el servidor respondió
                print("✅ API is up!")
                return True
        except Exception:
            pass
        time.sleep(1)
    print("❌ API did not become available in time.")
    return False

def call_api():
    url = "http://app:8000/api/v1/posts/run-posts"
    token = os.getenv("PERSONAL_ACCESS_TOKEN")

    headers = {
        "Authorization": token
    }

    try:
        response = requests.post(url, headers=headers)
        print(f"✅ Called {url} → Status: {response.status_code}, Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error calling {url}: {e}")

def check_alive():
    now = get_colombia_time_str()
    print(f"🟢 Scheduler is alive at {now}")
    send_telegram_message(f"🟢 Scheduler is alive at {now}")

def send_telegram_message(message):
    url = "http://app:8000/api/v1/telegram/send"
    token = os.getenv("PERSONAL_ACCESS_TOKEN")
    payload = {
        "message": message
    }
    headers = {
        "Authorization": token
    }

    try:
        response = requests.post(url, params=payload, headers=headers)
        print(f"📩 Sent message to Telegram: {message} → Status: {response.status_code}, Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error sending message to Telegram: {e}")

if __name__ == "__main__":
    print("🚀 Starting scheduler...")
    scheduler = BlockingScheduler()

    # Convertir horas de Colombia a UTC
    colombia_hours = [(9, 30), (12, 30), (16, 0)]
    for hour, minute in colombia_hours:
        utc_hour, utc_minute = colombia_to_utc(hour, minute)
        scheduler.add_job(call_api, 'cron', hour=utc_hour, minute=utc_minute)
        print(f"✅ Scheduled post at {hour:02d}:{minute:02d} COL → {utc_hour:02d}:{utc_minute:02d} UTC")

    # Verificación de vida cada 1 horas
    scheduler.add_job(check_alive, 'interval', hours=1)
    # scheduler.add_job(check_alive, 'interval', minutes=1)
    print("✅ Scheduled 'is alive' check every 1 hours")

    # Esperar a que API esté lista
    if wait_for_api("http://app:8000/docs"):
        send_telegram_message("🚀 Scheduler started successfully!")
    else:
        send_telegram_message("⚠️ Scheduler could not verify API availability.")

    scheduler.start()

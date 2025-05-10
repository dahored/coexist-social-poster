import requests
from apscheduler.schedulers.blocking import BlockingScheduler

def colombia_to_utc(hour, minute):
    """
    Convierte la hora de Colombia (UTC−5) a UTC.
    Suma 5 horas y ajusta si pasa de 24 usando módulo 24.
    
    Ejemplo:
        9:30 COL → 14:30 UTC
        12:30 COL → 17:30 UTC
        15:30 COL → 20:30 UTC
    """
    utc_hour = (hour + 5) % 24
    print(f"⏰ Colombia time: {hour:02d}:{minute:02d} → UTC time: {utc_hour:02d}:{minute:02d}")
    return utc_hour, minute

def call_api():
    """
    Llama a la API local para ejecutar la ruta /api/v1/posts/run-posts.
    """
    url = "http://app:8000/api/v1/posts/run-posts"
    try:
        response = requests.post(url)
        print(f"✅ Called {url} → Status: {response.status_code}, Response: {response.json()}")
    except Exception as e:
        print(f"❌ Error calling {url}: {e}")

if __name__ == "__main__":
    print("🚀 Starting scheduler...")
    scheduler = BlockingScheduler()

    # Definir horas de Colombia
    colombia_hours = [(9, 30), (12, 30), (16, 00)]

    # Agregar los jobs al scheduler convertidos a UTC
    for hour, minute in colombia_hours:
        utc_hour, utc_minute = colombia_to_utc(hour, minute)
        scheduler.add_job(call_api, 'cron', hour=utc_hour, minute=utc_minute)
        print(f"✅ Scheduled for {hour:02d}:{minute:02d} COL → {utc_hour:02d}:{utc_minute:02d} UTC")

    print("🚀 Scheduler started, will run at 9:30am, 12:30pm, 4:00pm COL daily")
    scheduler.start()

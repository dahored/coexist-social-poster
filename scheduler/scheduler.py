import os
from dotenv import load_dotenv
import requests
from apscheduler.schedulers.blocking import BlockingScheduler

load_dotenv()

def colombia_to_utc(hour, minute):
    utc_hour = (hour + 5) % 24
    print(f"⏰ Colombia time: {hour:02d}:{minute:02d} → UTC time: {utc_hour:02d}:{minute:02d}")
    return utc_hour, minute

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

if __name__ == "__main__":
    print("🚀 Starting scheduler...")
    scheduler = BlockingScheduler()

    colombia_hours = [(9, 30), (12, 30), (16, 0)]

    for hour, minute in colombia_hours:
        utc_hour, utc_minute = colombia_to_utc(hour, minute)
        scheduler.add_job(call_api, 'cron', hour=utc_hour, minute=utc_minute)
        print(f"✅ Scheduled for {hour:02d}:{minute:02d} COL → {utc_hour:02d}:{utc_minute:02d} UTC")

    print("🚀 Scheduler started, will run at 9:30am, 12:30pm, 4:00pm COL daily")
    scheduler.start()

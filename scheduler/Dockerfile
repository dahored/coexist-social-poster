FROM python:3.11-slim

WORKDIR /app

COPY scheduler.py .

RUN pip install --no-cache-dir requests apscheduler

CMD ["python", "-u", "scheduler.py"]

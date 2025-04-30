FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Crear carpetas necesarias
# RUN mkdir -p public/uploads/images public/uploads/temps

EXPOSE 8000

# CMD ["python", "index.py"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]


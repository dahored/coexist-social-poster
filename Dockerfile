FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar todos los archivos al contenedor
COPY . .

# Instalar las dependencias
# RUN apt-get update && apt-get install -y jpegoptim optipng && apt-get clean
RUN apt-get update && apt-get install -y pngquant jpegoptim && apt-get clean
RUN pip install --no-cache-dir -r requirements.txt

# Crear carpetas necesarias dentro del contenedor (solo si no se usan volúmenes en docker-compose)
RUN mkdir -p public/uploads/temps
RUN mkdir -p public/uploads/images

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar FastAPI con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

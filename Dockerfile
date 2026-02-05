FROM python:3.12-slim

# Prevenir escritura de archivos .pyc y buffer de salida
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    python3-dev \
    libpq-dev \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar proyecto
COPY . .

# Crear directorios para archivos estáticos y media
RUN mkdir -p /app/staticfiles /app/media

# Copiar y dar permisos al script de entrada
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Exponer puerto
EXPOSE 8000

# Script de inicio
ENTRYPOINT ["/entrypoint.sh"]

# Comando por defecto (puede ser sobrescrito por docker-compose)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

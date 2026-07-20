# Imagen oficial de Playwright: ya trae Chromium y sus dependencias de sistema
FROM mcr.microsoft.com/playwright/python:v1.48.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Railway inyecta el puerto en $PORT
CMD ["sh", "-c", "python gramet_app.py"]

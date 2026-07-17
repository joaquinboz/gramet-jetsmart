FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gramet_web.py .

ENV PORT=5000

CMD ["python", "gramet_web.py"]

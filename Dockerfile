FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY gramet_web.py .
COPY README.md .
COPY .gitignore .

ENV PORT=5000

CMD ["python", "gramet_web.py"]

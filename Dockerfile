# Використовуємо офіційний Python базовий образ
FROM python:3.10-slim

# Встановлюємо необхідні бібліотеки для роботи FastAPI
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код в робочу директорію контейнера
COPY . /app




# Запускаємо FastAPI додаток
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

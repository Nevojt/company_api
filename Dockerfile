# Використовуємо офіційний Python базовий образ
FROM python:3.12-slim
# Встановлюємо необхідні бібліотеки для роботи FastAPI
WORKDIR /api
COPY requirements.txt /api/
RUN pip install --no-cache-dir -r requirements.txt
# Копіюємо весь код в робочу директорію контейнера
COPY . /api




# Запускаємо FastAPI додаток
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

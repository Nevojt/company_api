# Використовуємо офіційний Python базовий образ
FROM python:3.10-slim

# Встановлюємо необхідні бібліотеки для роботи FastAPI
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код в робочу директорію контейнера
COPY . /app

# Вказуємо команду для запуску FastAPI через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
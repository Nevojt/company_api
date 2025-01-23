<<<<<<< HEAD
# Використовуємо офіційний Python базовий образ
FROM python:3.12-slim

# Встановлюємо необхідні бібліотеки для роботи FastAPI
WORKDIR /api
COPY requirements.txt /api/
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код в робочу директорію контейнера
COPY . /api

# Вказуємо команду для запуску FastAPI через uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
=======
# Use the official Python base image
FROM python:3.10-slim

# Install necessary libraries for PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code into the container
COPY . /app

# Command to run the FastAPI application
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
>>>>>>> b76081a8ec4b9a820a3d0f1adef71c7e7cef6824

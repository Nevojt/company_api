# Використовуємо офіційний Python базовий образ
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Оновлюємо та встановлюємо необхідні системні залежності
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Створюємо робочу директорію
WORKDIR /api

# Увімкнення компіляції байт-коду для швидшого запуску
ENV UV_COMPILE_BYTECODE=1

# Задаємо спосіб кешування залежностей
ENV UV_LINK_MODE=copy

# Встановлення залежностей, використовуючи кешовану директорію
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Копіюємо решту коду проєкту
ADD . /api

# Копіюємо .env файли
COPY .env /api/.env
COPY .env_start_app /api/.env_start_app

# Встановлюємо проєктні залежності
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Додаємо папку віртуального середовища на початок PATH
ENV PATH="/api/.venv/bin:$PATH"

# Скидаємо entrypoint, щоб Docker не використовував команду `uv` за замовчуванням
ENTRYPOINT []

# Запускаємо FastAPI додаток
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

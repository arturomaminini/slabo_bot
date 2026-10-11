FROM python:3.12-slim

WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY bot.py .

# Запускаем бота
CMD ["python", "bot.py"]


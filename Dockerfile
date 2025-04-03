# Використовуємо базовий образ Python
FROM python:3.10

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли вимог та встановлюємо залежності
COPY Pipfile Pipfile.lock ./
RUN pip install pipenv && pipenv install --system --deploy

# Копіюємо всі файли проекту
COPY . .

# Відкриваємо порт 3000
EXPOSE 3000

# Запускаємо веб-додаток
CMD ["python", "main.py"]
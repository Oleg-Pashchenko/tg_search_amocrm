# Используйте базовый образ Python
FROM python:3.11

# Установите зависимости
COPY requirements.txt /requirements.txt
WORKDIR ./site
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


CMD ["python", "-u", "site/app.py"]

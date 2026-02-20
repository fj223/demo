# Система расписания

Приложение на Flask для просмотра и экспорта расписания занятий.

## Установка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/fj223/demo.git
cd demo
```

### 2. Установить зависимости Python

```bash
pip install -r requirements.txt
```

### 3. Установить wkhtmltopdf (для экспорта PDF)

1. Скачать с [официального сайта](https://wkhtmltopdf.org/downloads.html)
2. Установить в `D:\wkhtmltopdf`
3. Добавить `D:\wkhtmltopdf\bin` в переменную среды PATH

## Запуск

```bash
python app.py
```

Открыть http://localhost:5000 в браузере.

## Docker

```bash
docker build -t timetable-app .
docker run -d -p 5000:5000 timetable-app
```

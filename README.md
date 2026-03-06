# Сервис для сокращения URL.

## Установка

### 1. Клонирование репозитория
```bash
git clone <url-репозитория>
cd shorting_api
```

## Запуск приложения с помощью Dockerfile

### Сборка образа
```bash
docker build -t shorting-api .
```

### Запуск образа
```bash
docker run -p 8000:8000 shorting-api
```

## Запуск приложения с помощью docker-compose

### Сборка образа
```bash
docker-compose build --no-cache
```

### Запуск образа
```bash
docker-compose up -d
```

### Остановка
```bash
docker-compose down
```

Swagger с эндпоинтами будет доступен по ссылке http://127.0.0.1:8000/docs. Однако на эндпоинт /{short_id} лучше переходить напрямую, не через сваггер, потому что переадресация работает только так.

## Тестирование

### Установка тестовых зависимостей
```bash
pip install -r requirements.txt
```

### Запуск всех тестов
```bash
pytest test_handlers.py -v
```

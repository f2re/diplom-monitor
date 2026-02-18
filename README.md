# DiplomMonitor - Weeks Until Diploma Tracker

🎓 Веб-приложение для отслеживания прогресса написания дипломной работы с визуализацией недель и авторизацией через Telegram.

## Возможности

- 📅 Визуализация прогресса по неделям в виде сетки
- 🎨 Цветовая индикация статуса недель (запланировано/выполнено/пропущено)
- 🔐 Авторизация через Telegram Bot
- 👥 Мультипользовательский режим с emoji-идентификаторами
- 🔔 Уведомления о прогрессе через Telegram
- 📊 Статистика и аналитика прогресса
- 🎯 Специальные периоды (каникулы, экзамены)

## Технологический стек

### Backend
- **FastAPI** - современный Python веб-фреймворк
- **PostgreSQL** - база данных
- **SQLAlchemy** - ORM
- **Alembic** - миграции БД
- **Pydantic** - валидация данных
- **python-telegram-bot** - интеграция с Telegram

### Frontend
- **Vue 3** - Progressive JavaScript Framework
- **Vite** - быстрая сборка и dev-сервер
- **Pinia** - state management
- **Axios** - HTTP клиент
- **Tailwind CSS** - utility-first CSS
- **Lucide Icons** - иконки

### DevOps
- **Docker** + **Docker Compose** - контейнеризация
- **Nginx** - reverse proxy и статика
- **Let's Encrypt** - SSL сертификаты

## Быстрый старт

### Требования
- Docker и Docker Compose
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/f2re/diplom-monitor.git
cd diplom-monitor
```

2. Создайте `.env` файл:
```bash
cp .env.example .env
```

3. Заполните `.env` файл:
```env
SECRET_KEY=your_super_secret_key_here  # Сгенерируйте: openssl rand -hex 32
TELEGRAM_BOT_TOKEN=123456789:AABBCC...  # Токен от @BotFather
TELEGRAM_BOT_NAME=your_bot_username     # Без @
```

4. Привяжите домен к боту в @BotFather:
```
/mybots → выберите бота → Edit Bot → Edit Domain
Укажите: ваш-домен.com
```

5. Запустите приложение:
```bash
# Development (с Vite dev server)
docker compose up -d

# Production (с оптимизированной сборкой)
docker compose -f docker-compose.yml up -d --build
```

6. Настройте nginx на хосте:
```bash
sudo cp nginx-https.conf /etc/nginx/sites-available/diplom.conf
sudo ln -sf /etc/nginx/sites-available/diplom.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

7. Получите SSL сертификат:
```bash
sudo certbot --nginx -d ваш-домен.com
```

## Структура проекта

```
diplom-monitor/
├── backend/
│   ├── app/
│   │   ├── api/          # API эндпоинты
│   │   ├── core/         # Конфиг, безопасность
│   │   ├── models/       # SQLAlchemy модели
│   │   ├── schemas/      # Pydantic схемы
│   │   └── main.py       # Точка входа FastAPI
│   ├── alembic/          # Миграции БД
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # Vue компоненты
│   │   ├── stores/       # Pinia stores
│   │   └── App.vue
│   ├── Dockerfile.prod   # Production сборка
│   └── nginx.conf        # Nginx для статики
├── docker-compose.yml
├── nginx-https.conf      # Главный nginx конфиг
└── .env.example
```

## API Документация

После запуска доступна по адресу:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Разработка

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Миграции БД
```bash
cd backend
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Production Deployment

1. Соберите production образы:
```bash
docker compose build --no-cache
```

2. Запустите:
```bash
docker compose up -d
```

3. Проверьте логи:
```bash
docker compose logs -f
```

4. Проверьте эндпоинты:
```bash
# Backend health
curl http://localhost:8000/health

# Frontend
curl http://localhost:5173

# Через nginx
curl https://ваш-домен.com/api/health
```

## Troubleshooting

### Backend не запускается
```bash
docker logs diplom-monitor-backend-1
# Проверьте переменные окружения в .env
```

### Frontend показывает 404 на /api/*
```bash
# Проверьте что nginx правильно проксирует
curl -v https://ваш-домен.com/api/health

# Проверьте backend напрямую
curl http://127.0.0.1:8000/health
```

### Telegram авторизация не работает
1. Проверьте что домен привязан в @BotFather
2. Проверьте TELEGRAM_BOT_TOKEN в .env
3. Проверьте что сайт доступен по HTTPS

## Лицензия

MIT

## Контакты

- GitHub: [@f2re](https://github.com/f2re)
- Репозиторий: [diplom-monitor](https://github.com/f2re/diplom-monitor)

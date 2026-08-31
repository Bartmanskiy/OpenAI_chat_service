# OpenAI Chat Service

Мінімальний REST API для роботи з chat-сесіями та OpenAI API.

## Технології

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* OpenAI Python SDK
* Pydantic

## Структура проєкту

```text
app/
├── main.py
├── api/
│   └── routes/
│       └── sessions.py
├── models/
│   ├── session.py
│   ├── message.py
│   └── __init__.py
├── schemas/
│   ├── session.py
│   ├── message.py
│   └── __init__.py
├── services/
│   ├── openai_service.py
│   └── pricing_service.py
├── db/
│   └── database.py
└── core/
    └── config.py

init_db.py
.env.example
.gitignore
README.md
```

## Встановлення та запуск

### 1. Створення virtual environment

```bash
python -m venv venv
```

Активація у Windows / Git Bash:

```bash
source venv/Scripts/activate
```

### 2. Встановлення залежностей

```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv openai pytest
```

### 3. Налаштування змінних середовища

Створіть файл `.env` на основі `.env.example`:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/openai_chat
```

`.env` не повинен додаватися до Git-репозиторію.

### 4. Ініціалізація бази даних

Переконайтеся, що PostgreSQL запущений, після чого виконайте:

```bash
python init_db.py
```

Скрипт створює необхідні таблиці PostgreSQL.

### 5. Запуск API

```bash
uvicorn app.main:app --reload
```

Swagger документація буде доступна за адресою:

`http://127.0.0.1:8000/docs`

## API

### POST /sessions

Створює нову chat session.

Приклад запиту:

```json
{
  "model": "gpt-5.6"
}
```

У відповідь повертається `session_id` та модель.

### POST /sessions/{session_id}/messages

Відправляє повідомлення користувача в конкретну session.

Приклад запиту:

```json
{
  "content": "Hello, how are you?"
}
```

Сервіс отримує попередню історію session з PostgreSQL та передає її разом із новим повідомленням до OpenAI.

При успішній відповіді endpoint повертає модельну відповідь, token usage та cost.

### POST /sessions/{session_id}/reset

Скидає поточний контекст session.

Reset не видаляє старі повідомлення з PostgreSQL. Замість цього збільшується `generation`, і наступні повідомлення належать до нової generation.

Приклад:

```bash
curl -X POST http://127.0.0.1:8000/sessions/{session_id}/reset
```

### GET /sessions/{session_id}

Повертає інформацію про session, історію повідомлень поточної generation, загальну кількість використаних токенів та накопичену вартість.

### GET /sessions/{session_id}/messages

Повертає повідомлення поточної generation конкретної session у хронологічному порядку.

## Приклади API-запитів

### 1. Створення session

```bash
curl -X POST http://127.0.0.1:8000/sessions \
  -H "Content-Type: application/json" \
  -d "{\"model\":\"gpt-5.6\"}"
```

### 2. Відправлення повідомлення

```bash
curl -X POST http://127.0.0.1:8000/sessions/{session_id}/messages \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"Hello!\"}"
```

### 3. Отримання session та історії

```bash
curl http://127.0.0.1:8000/sessions/{session_id}
```

### 4. Reset session

```bash
curl -X POST http://127.0.0.1:8000/sessions/{session_id}/reset
```

## База даних

Використовується PostgreSQL.

Основні таблиці:

* `sessions`
* `messages`

`sessions` містить інформацію про chat session, вибрану OpenAI-модель та поточну `generation`.

`messages` містить повідомлення користувача та відповіді асистента, а також token usage і вартість взаємодії.

`messages.session_id` є foreign key на `sessions.id` та має індекс для швидкого отримання історії конкретної session.

Ініціалізація таблиць виконується за допомогою:

```bash
python init_db.py
```

## Передача історії

PostgreSQL використовується як джерело історії діалогу.

Перед кожним запитом до OpenAI сервіс отримує попередні повідомлення поточної generation конкретної session, сортує їх за часом та передає їх разом із новим повідомленням користувача.

Таким чином, модель отримує контекст попереднього діалогу, а не лише останнє повідомлення.

## Usage та вартість

Для тестування використовується модель:

```text
gpt-5.6
```

У розрахунку вартості використовуються такі ставки:

* Input tokens — $4 / 1M tokens
* Output tokens — $20 / 1M tokens

Розрахунок вартості реалізований окремо у:

```text
app/services/pricing_service.py
```

Вартість розраховується на основі кількості input та output tokens.

Додаткові категорії usage, зокрема cached input tokens, у поточній реалізації не враховуються.

## Обробка помилок

API обробляє основні типові помилки:

* `404` — session не знайдена;
* `422` — некоректні вхідні дані;
* `429` — помилка OpenAI API, зокрема недостатня quota або rate limit;
* `500` — непередбачена внутрішня помилка.

## Тестування

Для запуску тестів:

```bash
pytest
```

Поточні тести покривають pricing-логіку, перевірку підтримуваних моделей та окремі сценарії роботи з session/reset.

## Відомі обмеження

* Для кожного запиту передається повна історія session. Автоматичне обрізання або summary довгих діалогів не реалізовано.
* Авторизація користувачів не реалізована, оскільки вона не входила у вимоги.
* Pricing зберігається як статична конфігурація та потребує ручного оновлення при зміні тарифів.
* Cached input та інші додаткові категорії usage не враховуються у поточному розрахунку вартості.
* Для створення та роботи з базою даних використовується простий `create_all()` скрипт; міграції бази даних не реалізовані.
* Під час розробки OpenAI API повертав `429 insufficient_quota`, тому повний успішний запит до моделі з реальним usage не вдалося протестувати на доступному API-акаунті.

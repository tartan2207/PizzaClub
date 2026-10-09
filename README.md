# PizzaClub — Сервіс Доставки Піци та Їжі 🍕🚀

Ласкаво просимо до **PizzaClub** — сучасного, високонавантаженого та безпечного REST API сервісу для онлайн-замовлення та доставки їжі. Проєкт побудований на базі **Django / Django REST Framework** з використанням **PostgreSQL** у якості основної бази даних та дотриманням кращих практик модульної архітектури.

## 🛠 Технологічний стек

* **Мова програмування:** Python 3.11+
* **Фреймворк:** Django 6.1+ / Django REST Framework (DRF)
* **База даних:** PostgreSQL
* **Автентифікація:** JWT (SimpleJWT)
* **Тестування:** `pytest`, `pytest-django`, `factory-boy`
* **Статичний аналіз та типізація:** `mypy` (з `django-stubs` та `djangorestframework-stubs`)
* **Документація API:** Swagger UI / ReDoc (`drf-yasg`)
* **Управління конфігурацією:** `django-environ`

## 📁 Структура проєкту

Проєкт реалізовано за модульною архітектурою з ізоляцією додатків у директорії `apps/` та конфігурації у `setting/config/`:

```text
PizzaClub/
├── apps/                   # Додатки бізнес-логіки
│   ├── users/              # Управління користувачами та профілями
│   ├── menu/               # Каталог страв, категорій та меню
│   ├── orders/             # Оформлення та відстеження замовлень
│   ├── delivery/           # Логістика та статуси доставки
│   └── reviews/            # Відгуки та рейтинги (із перевіркою покупок)
├── setting/
│   └── config/             # Налаштування Django (settings, urls, wsgi/asgi)
├── .env.example            # Шаблон змінних оточення
├── manage.py
├── mypy.ini                # Конфігурація стачного аналізатора типів MyPy
├── pytest.ini              # Конфігурація фреймворку тестування Pytest
└── pyproject.toml / requirements.txt
### Каталог Меню
* **Перегляд страв**, фільтрація за категоріями та пошук.

### Система Замовлень
* **Оформлення замовлень** із вибором адреси доставки та відстеженням статусів (`PENDING`, `DELIVERED` тощо).

### Відгуки та Рейтинги (`ReviewViewSet`)
* **Система відгуків із валідацією підтверджених покупок (Verified Purchase):** залишити відгук можна лише на страву із доставленого замовлення.
* **Обмеження унікальності:** `UniqueTogetherValidator` (один відгук на страву від одного користувача).
* **Автоматичне обмеження прав доступу:** `IsAdminOrOwnerReadOnly`.

### Health Check
* **Розширений ендпоінт перевірки стану системи (`/health/`)** з моніторингом підключення до PostgreSQL для Docker/Kubernetes.
## 🚀 Швидкий старт (Локальне розгортання)

### 1. Клонування репозиторію

```bash
git clone [https://github.com/your-username/PizzaClub.git](https://github.com/your-username/PizzaClub.git)
cd PizzaClub
### 3. Змінні оточення (`.env`)

Створіть файл `.env` у кореневій директорії на основі `.env.example`:

```env
DEBUG=True
SECRET_KEY=your-super-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database URL
DATABASE_URL=postgres://pizza_user:pizza_pass@localhost:5432/pizzaclub_db

### 5. Запуск сервера розробки

```bash
python manage.py runserver
Сервер буде доступний за адресою: `http://127.0.0.1:8000/`

---

## 📚 Документація API (Swagger / ReDoc)

Після запуску сервера документація доступна за наступними URL:

* **Swagger UI:** `http://127.0.0.1:8000/swagger/`
* **ReDoc:** `http://127.0.0.1:8000/redoc/`
* **Health Check:** `http://127.0.0.1:8000/health/`


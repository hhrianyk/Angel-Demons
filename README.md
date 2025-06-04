---

# ☕ Angel & Demons Cafe — Вебсайт з AR-меню

![Логотип](static/images/logo.png)

> **Інноваційний веб-додаток для кафе з онлайн-меню, системою замовлень і переглядом десертів у доповненій реальності.**

---

## 🚀 Особливості

* 🍰 **Онлайн-меню** з категоріями (десерти, напої тощо)
* 🛒 **Система замовлень** з підтвердженням і Telegram-сповіщенням
* 🔍 **AR-перегляд десертів** через камеру пристрою
* 📱 **Адаптивний дизайн** для всіх екранів
* 🤖 **Інтеграція з Telegram Bot API** для адміністратора

---

## 🛠️ Технології

| Компонент    | Технологія              |
| ------------ | ----------------------- |
| Backend      | Python + Flask          |
| Frontend     | HTML5, CSS3, JavaScript |
| База даних   | SQLite                  |
| AR           | MindAR + A-Frame        |
| Повідомлення | Telegram Bot API        |

---

## 📦 Встановлення

1. **Клонування репозиторію**

   ```bash
   git clone https://github.com/ваш-акаунт/cafeweb.git
   cd cafeweb
   ```

2. **Встановлення залежностей**

   ```bash
   pip install -r requirements.txt
   ```

3. **Налаштування Telegram-бота**

   * Створіть бота через [@BotFather](https://t.me/BotFather)
   * Додайте токен у `app.py`:

     ```python
     TELEGRAM_TOKEN = 'ваш_токен'
     TELEGRAM_CHAT_ID = 'ваш_chat_id'
     ```

4. **Запуск застосунку**

   ```bash
   python app.py
   ```

   або для режиму розробки:

   ```bash
   flask run --debug
   ```

5. **Відкрийте у браузері:**

   ```
   http://localhost:5000
   ```

---

## 🧁 AR Налаштування

1. **AR мітки:**

   * Розмістіть файли у `WEBAR/static/targets/`
   * Основний файл: `targets.mind`
   * Для створення: [MindAR Target Generator](https://hiukim.github.io/mind-ar-js/tools/)

2. **3D моделі десертів:**

   * Формати `.glb` або `.gltf`
   * Приклад: `cake.glb`
   * Розмістіть у `WEBAR/static/models/`

---

## 📁 Структура проєкту

```
cafeweb/
├── WEBAR/
│   └── static/
│       ├── targets/         # AR мітки
│       └── models/          # 3D моделі
├── static/
│   ├── css/                 # Стилі
│   ├── js/                  # Скрипти
│   └── images/              # Зображення
├── templates/
│   ├── base.html
│   ├── menu.html
│   ├── order.html
│   ├── ar.html
│   └── webar_scanner.html
├── app.py                   # Основна логіка
├── database.py              # Робота з БД
└── requirements.txt         # Залежності
```

---

## 🔗 Використання

| Сторінка     | URL-путь         | Призначення                     |
| ------------ | ---------------- | ------------------------------- |
| Меню         | `/menu`          | Перегляд десертів і напоїв      |
| Замовлення   | `/order`         | Оформлення замовлення           |
| AR-перегляд  | `/ar`            | Вибір AR-десерту                |
| AR-сканер    | `/webar_scanner` | Відображення 3D-моделі в камері |
| Повідомлення | —                | Надсилаються через Telegram Bot |

---
## 🗃️ Структура Бази Даних

```mermaid
erDiagram
    CATEGORIES ||--o{ MENU_ITEMS : contains
    ORDERS ||--o{ ORDER_ITEMS : has
    USERS ||--o{ ORDERS : places

    CATEGORIES {
        int id PK
        varchar(100) name
        text description
        varchar(50) icon
        timestamp created_at
    }
    
    MENU_ITEMS {
        int id PK
        int category_id FK
        varchar(100) name
        text description
        decimal(10,2) price
        varchar(100) image_name
        varchar(100) ar_model
        boolean is_featured
        int calories
        timestamp created_at
    }
    
    ORDERS {
        int id PK
        int user_id FK
        varchar(100) status
        decimal(10,2) total
        text delivery_address
        varchar(20) phone
        text notes
        timestamp created_at
    }
    
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int item_id FK
        int quantity
        decimal(10,2) price
        text special_requests
    }
    
    USERS {
        int id PK
        varchar(100) email
        varchar(100) name
        varchar(100) nft_token
        varchar(100) preferences
    } 
```


## 🖼️ Скріншоти (рекомендовано)

> 🔜 Додайте зображення інтерфейсу, меню та AR-перегляду

---

## 🧪 Розробка та розгортання

Для локальної розробки:

```bash
flask run --debug
```

Для продакшену:

* Використовуйте Gunicorn + Nginx
* Розгорніть на платформі як Heroku, Railway або VPS

---

## 📌 Badges (опційно)

> Додайте, наприклад:

```
![Python](https://img.shields.io/badge/python-3.10-blue)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=flat&logo=flask&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
```

---

## 👤 Автор

**Angel & Demons Cafe Team**
 )*

---

## 📄 Ліцензія

Цей проєкт ліцензовано під MIT License. Деталі — у файлі `LICENSE`.

© 2025 Angel & Demons Cafe. Усі права захищені.

---


Обовязковоа роби місця під картинки
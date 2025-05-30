
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
📧 Email: [example@cafe.com](mailto:example@cafe.com)
🌐 [Сайт-демо](https://example.com) *(за наявності)*

---

## 📄 Ліцензія

Цей проєкт ліцензовано під MIT License. Деталі — у файлі `LICENSE`.

© 2023 Angel & Demons Cafe. Усі права захищені.

---

> Якщо бажаєте — я можу додати шаблони для `.env`, Dockerfile або CI/CD.

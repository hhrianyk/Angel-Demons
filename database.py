import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()
    print("Start")
    # Створюємо таблиці з правильною структурою
    c.execute('''CREATE TABLE users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL UNIQUE,
                      email TEXT NOT NULL UNIQUE,
                      password_hash TEXT NOT NULL,
                      phone TEXT,
                      created_at TEXT NOT NULL,
                      is_admin BOOLEAN DEFAULT FALSE)''')

    c.execute('''CREATE TABLE categories
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      description TEXT)''')
    # Створення таблиці категорій
    c.execute('''CREATE TABLE IF NOT EXISTS categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT)''')

    # Створення таблиці меню
    c.execute('''CREATE TABLE IF NOT EXISTS menu_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category_id INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  description TEXT,
                  price REAL NOT NULL,
                  image_name TEXT,  # Новий стовпець для імені файлу зображення
                  FOREIGN KEY (category_id) REFERENCES categories (id))''')

    # Оновлюємо тестові дані
    c.execute("INSERT INTO menu_items (category_id, name, description, price, image_name) VALUES (?, ?, ?, ?, ?)",
              (1, 'Чорний макарон', 'Ніжний макарон з чорним шоколадом', 65, 'black_macaron.jpg'))

    # Створення таблиці замовлень
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_name TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  order_date TEXT NOT NULL,
                  total REAL NOT NULL)''')

    # Створення таблиці позицій замовлення
    c.execute('''CREATE TABLE IF NOT EXISTS order_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  order_id INTEGER NOT NULL,
                  item_name TEXT NOT NULL,
                  item_price REAL NOT NULL,
                  FOREIGN KEY (order_id) REFERENCES orders (id))''')

    # Перевірка наявності даних
    c.execute("SELECT COUNT(*) FROM categories")
    if c.fetchone()[0] == 0:
        # Додаємо категорії
        categories = [
            (1, 'Десерти', 'Чорно-білі десерти для витончених смаків'),
            (2, 'Напої', 'Гарячі та холодні напої з контрастними смаками')
        ]
        c.executemany("INSERT INTO categories VALUES (?, ?, ?)", categories)

        # Додаємо десерти
        desserts = [
            (1, 'Чорний макарон', 'Ніжний макарон з чорним шоколадом', 65),
            (1, 'Білий фондан', 'Фондан з білого шоколаду з малиновим соусом', 75),
            (1, 'Ангельський чізкейк', 'Легкий як перо білий чізкейк', 80),
            (1, 'Демонічний трюфель', 'Інтенсивний шоколад з перцем чилі', 70),
            (1, 'Дуальний еклер', 'Еклер з подвійною глазур\'ю', 68)
        ]
        c.executemany("INSERT INTO menu_items (category_id, name, description, price) VALUES (?, ?, ?, ?)", desserts)

        # Додаємо напої
        drinks = [
            (2, 'Еспресо Демона', 'Міцний еспресо з чорною карамеллю', 55),
            (2, 'Ангельський лате', 'Ніжний лате з квітковим ароматом', 60),
            (2, 'Дуальний капучино', 'Капучино з подвійним артом', 65),
            (2, 'Темний мокко', 'Шоколадний мокко з чорним шоколадом', 70),
            (2, 'Небесний фрапе', 'Холодний фрапе з блакитним кольором', 75)
        ]
        c.executemany("INSERT INTO menu_items (category_id, name, description, price) VALUES (?, ?, ?, ?)", drinks)

        conn.commit()
    print("Finish")
    conn.close()


def get_categories():
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()
    c.execute("SELECT * FROM categories")
    categories = c.fetchall()
    conn.close()
    return categories


def get_menu_items(category_id=None):
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()

    if category_id:
        c.execute("SELECT * FROM menu_items WHERE category_id=?", (category_id,))
    else:
        c.execute("SELECT * FROM menu_items")

    items = c.fetchall()
    conn.close()
    return items


def get_full_menu():
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()

    c.execute('''SELECT categories.name as category, 
                        menu_items.id,
                        menu_items.name, 
                        menu_items.description, 
                        menu_items.price 
                 FROM menu_items 
                 JOIN categories ON menu_items.category_id = categories.id''')

    menu = {}
    for item in c.fetchall():
        category = item[0]
        if category not in menu:
            menu[category] = []
        menu[category].append({
            'id': item[1],
            'name': item[2],
            'description': item[3],
            'price': item[4]
        })

    conn.close()
    return menu


def save_order(customer_name, phone, items, total):
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()

    # Зберігаємо замовлення
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO orders (customer_name, phone, order_date, total) VALUES (?, ?, ?, ?)",
              (customer_name, phone, order_date, total))
    order_id = c.lastrowid

    # Зберігаємо позиції замовлення
    for item_name in items:
        # Знаходимо ціну товару
        c.execute("SELECT price FROM menu_items WHERE name=?", (item_name,))
        item_price = c.fetchone()[0]

        c.execute("INSERT INTO order_items (order_id, item_name, item_price) VALUES (?, ?, ?)",
                  (order_id, item_name, item_price))

    conn.commit()
    conn.close()


def create_user(username, email, password, phone=None):
    """Створення нового користувача"""
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()

    # Хешування паролю
    password_hash = generate_password_hash(password)

    try:
        c.execute("INSERT INTO users (username, email, password_hash, phone, created_at) VALUES (?, ?, ?, ?, ?)",
                  (username, email, password_hash, phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Користувач з таким ім'ям або email вже існує
    finally:
        conn.close()


def get_user_by_username(username):
    """Отримання користувача за ім'ям"""
    conn = sqlite3.connect('cafe.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    return user
# Допоміжні функції для роботи з БД
def get_db():
    """Підключення до бази даних"""
    conn = sqlite3.connect('cafe.db')
    conn.row_factory = sqlite3.Row
    return conn

def verify_user(username, password):
    """Перевірка логіну та паролю"""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

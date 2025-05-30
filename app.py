from flask import *
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
from datetime import datetime
import requests
from threading import Thread
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Telegram налаштування
TELEGRAM_TOKEN = '7663765318:AAGcWrl-MlL8bdJnvRZuFaQan9Sv7bPoWI4'
TELEGRAM_CHAT_ID = ['982150223']
ADMIN_USER_IDS = set()


def init_db():
    """Повністю перестворює базу даних з правильною структурою"""
    if os.path.exists('cafe.db'):
        os.remove('cafe.db')

    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()

    # Створюємо таблиці з правильною структурою
    c.execute('''CREATE TABLE categories
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  description TEXT)''')

    c.execute('''CREATE TABLE menu_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  category_id INTEGER NOT NULL,
                  name TEXT NOT NULL,
                  description TEXT,
                  price REAL NOT NULL,
                  FOREIGN KEY (category_id) REFERENCES categories (id))''')

    c.execute('''CREATE TABLE orders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_name TEXT NOT NULL,
                  phone TEXT NOT NULL,
                  address TEXT,
                  notes TEXT,
                  total REAL NOT NULL,
                  order_date TEXT NOT NULL)''')

    c.execute('''CREATE TABLE order_items
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  order_id INTEGER NOT NULL,
                  item_name TEXT NOT NULL,
                  item_price REAL NOT NULL,
                  quantity INTEGER NOT NULL,
                  FOREIGN KEY (order_id) REFERENCES orders (id))''')

    # Додаємо тестові дані
    c.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
              ('Десерти', 'Чорно-білі десерти для витончених смаків'))
    c.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
              ('Напої', 'Гарячі та холодні напої з контрастними смаками'))

    c.execute("INSERT INTO menu_items (category_id, name, description, price) VALUES (?, ?, ?, ?)",
              (1, 'Чорний макарон', 'Ніжний макарон з чорним шоколадом', 65))
    c.execute("INSERT INTO menu_items (category_id, name, description, price) VALUES (?, ?, ?, ?)",
              (1, 'Білий фондан', 'Фондан з білого шоколаду з малиновим соусом', 75))
    c.execute("INSERT INTO menu_items (category_id, name, description, price) VALUES (?, ?, ?, ?)",
              (2, 'Еспресо Демона', 'Міцний еспресо з чорною карамеллю', 55))
    c.execute("INSERT INTO menu_items (category_id, name, description, price) VALUES (?, ?, ?, ?)",
              (2, 'Ангельський лате', 'Ніжний лате з квітковим ароматом', 60))

    conn.commit()
    conn.close()


def get_db():
    """Підключення до бази даних"""
    conn = sqlite3.connect('cafe.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_menu():
    """Отримання меню з бази даних"""
    conn = get_db()
    menu = {}

    categories = conn.execute("SELECT * FROM categories").fetchall()
    for category in categories:
        items = conn.execute(
            "SELECT * FROM menu_items WHERE category_id = ?",
            (category['id'],)
        ).fetchall()
        menu[category['name']] = items

    conn.close()
    return menu


def send_telegram_notification(order_data):
    """Надсилання сповіщення в Telegram"""
    try:
        message = f"""
        🍰 *Нове замовлення в Angel & Demons!* 🍰
        =============================
        👤 *Клієнт:* {order_data['name']}
        📞 *Телефон:* `{order_data['phone']}`
        🏠 *Адреса:* {order_data.get('address', 'Не вказано')}
        🕒 *Час:* {order_data['order_date']}
        =============================
        *Замовлення:*
        """

        for item in order_data['items']:
            message += f"\n- {item['name']} ×{item['quantity']} - {item['price'] * item['quantity']} грн"

        message += f"""
        =============================
        💵 *Сума:* {order_data['total']} грн
        📝 *Примітки:* {order_data.get('notes', 'Немає')}
        =============================
        🎉 *Гарного дня!*
        """

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        for Te in TELEGRAM_CHAT_ID:
            payload = {
                'chat_id': Te,
                'text': message,
                'parse_mode': 'Markdown'
            }

            requests.post(url, json=payload)

    except Exception as e:
        print(f"Помилка відправки в Telegram: {e}")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/menu')
def show_menu():
    menu = get_menu()
    return render_template('menu.html', menu=menu)


@app.route('/ar')
def ar_view():
    return render_template('ar.html')


@app.route('/webar/')
def full_ar_view():
    """Повноцінний AR перегляд"""
    return render_template('webar_scanner.html')

@app.route('/webar/targets/<path:filename>')
def serve_ar_targets(filename):
    """Віддача AR міток"""
    return send_from_directory('WEBAR/static/targets', filename)

@app.route('/webar/models/<path:filename>')
def serve_ar_models(filename):
    """Віддача 3D моделей"""
    return send_from_directory('WEBAR/static/models', filename)

@app.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        address = request.form.get('address', '')
        notes = request.form.get('notes', '')
        order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        items = []
        total = 0
        conn = get_db()

        for key, value in request.form.items():
            if key.startswith('quantity-') and request.form[key] != '0':
                item_id = key.replace('quantity-', '')
                quantity = int(request.form[key])

                item = conn.execute(
                    "SELECT id, name, price FROM menu_items WHERE id = ?",
                    (item_id,)
                ).fetchone()

                if item:
                    items.append({
                        'id': item['id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': quantity
                    })
                    total += item['price'] * quantity

        if items:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO orders (customer_name, phone, address, notes, total, order_date) VALUES (?, ?, ?, ?, ?, ?)",
                    (name, phone, address, notes, total, order_date)
                )
                order_id = cursor.lastrowid

                for item in items:
                    cursor.execute(
                        "INSERT INTO order_items (order_id, item_name, item_price, quantity) VALUES (?, ?, ?, ?)",
                        (order_id, item['name'], item['price'], item['quantity'])
                    )

                conn.commit()

                order_data = {
                    'name': name,
                    'phone': phone,
                    'address': address,
                    'notes': notes,
                    'order_date': order_date,
                    'items': items,
                    'total': total
                }

                Thread(target=send_telegram_notification, args=(order_data,)).start()

                flash('Ваше замовлення прийнято! Очікуйте дзвінка для підтвердження.', 'success')
                return redirect(url_for('order_confirmation'))
            except Exception as e:
                conn.rollback()
                flash('Сталася помилка при обробці замовлення. Спробуйте ще раз.', 'error')
                print(f"Database error: {e}")
            finally:
                conn.close()
        else:
            flash('Будь ласка, оберіть хоча б один товар.', 'error')
            conn.close()

        return redirect(url_for('order'))

    menu = get_menu()
    return render_template('order.html', menu=menu)


@app.route('/order/confirmation')
def order_confirmation():
    return render_template('order_confirmation.html')


if __name__ == '__main__':
    # Видаляємо та перестворюємо базу даних при кожному запуску під час розробки
    #init_db()
    app.run(debug=True)


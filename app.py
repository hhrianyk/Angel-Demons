from random import randint

from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify, \
    current_app
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
from datetime import datetime
import requests
from threading import Thread
import os
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user
from werkzeug.utils import secure_filename

from database import *

# Ініціалізація додатку
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
# Додати після ініціалізації app
login_manager = LoginManager(app)
login_manager.login_view = 'login'
# Конфігурація
TELEGRAM_TOKEN = '7663765318:AAGcWrl-MlL8bdJnvRZuFaQan9Sv7bPoWI4'
TELEGRAM_CHAT_ID = ['982150223', '921170769','824134740']
app.config['UPLOAD_FOLDER'] = 'static/images/menu'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}


# Допоміжні функції для роботи з БД
def get_db():
    """Підключення до бази даних"""
    conn = sqlite3.connect('cafe.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Ініціалізація бази даних"""
    conn = sqlite3.connect('cafe.db')
    c = conn.cursor()

    try:
        # Таблиця користувачів
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT NOT NULL UNIQUE,
                      email TEXT NOT NULL UNIQUE,
                      password_hash TEXT NOT NULL,
                      phone TEXT,
                      created_at TEXT NOT NULL,
                      is_admin BOOLEAN DEFAULT FALSE)''')

        # Таблиця категорій
        c.execute('''CREATE TABLE IF NOT EXISTS categories
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      description TEXT)''')

        # Таблиця товарів меню
        c.execute('''CREATE TABLE IF NOT EXISTS menu_items
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      category_id INTEGER NOT NULL,
                      name TEXT NOT NULL,
                      description TEXT,
                      price REAL NOT NULL,
                      image_name TEXT,
                      FOREIGN KEY (category_id) REFERENCES categories (id))''')

        # Таблиця замовлень
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      customer_name TEXT NOT NULL,
                      phone TEXT NOT NULL,
                      address TEXT,
                      notes TEXT,
                      total REAL NOT NULL,
                      order_date TEXT NOT NULL,
                      user_id INTEGER,
                      status TEXT DEFAULT 'new',
                      FOREIGN KEY (user_id) REFERENCES users (id))''')

        # Таблиця позицій замовлення
        c.execute('''CREATE TABLE IF NOT EXISTS order_items
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      order_id INTEGER NOT NULL,
                      item_id INTEGER NOT NULL,
                      item_name TEXT NOT NULL,
                      item_price REAL NOT NULL,
                      quantity INTEGER NOT NULL,
                      FOREIGN KEY (order_id) REFERENCES orders (id),
                      FOREIGN KEY (item_id) REFERENCES menu_items (id))''')

        # Перевірка наявності тестових даних
        c.execute("SELECT COUNT(*) FROM categories")
        if c.fetchone()[0] == 0:
            # Додаємо тестові категорії
            c.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
                      ('Десерти', 'Чорно-білі десерти для витончених смаків'))
            c.execute("INSERT INTO categories (name, description) VALUES (?, ?)",
                      ('Напої', 'Гарячі та холодні напої з контрастними смаками'))

            # Додаємо тестові товари
            menu_items = [
                (1, 'Чорний макарон', 'Ніжний макарон з чорним шоколадом', 65, 'black_macaron.jpg'),
                (1, 'Білий фондан', 'Фондан з білого шоколаду з малиновим соусом', 75, 'white_fondant.jpg'),
                (2, 'Еспресо Демона', 'Міцний еспресо з чорною карамеллю', 55, 'demon_espresso.jpg'),
                (2, 'Ангельський лате', 'Ніжний лате з квітковим ароматом', 60, 'angel_latte.jpg')
            ]
            c.executemany("""INSERT INTO menu_items 
                            (category_id, name, description, price, image_name) 
                            VALUES (?, ?, ?, ?, ?)""", menu_items)

            # Додаємо тестового адміністратора
            admin_hash = generate_password_hash('admin123')
            c.execute("""INSERT INTO users 
                        (username, email, password_hash, phone, created_at, is_admin) 
                        VALUES (?, ?, ?, ?, ?, ?)""",
                      ('admin', 'admin@example.com', admin_hash, '+380000000000',
                       datetime.now().strftime("%Y-%m-%d %H:%M:%S"), True))

        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Помилка при ініціалізації БД: {e}")
    finally:
        conn.close()


def get_menu():
    """Отримання меню з БД"""
    conn = get_db()
    menu = {}

    categories = conn.execute("SELECT * FROM categories").fetchall()
    for category in categories:
        items = conn.execute(
            "SELECT id, name, description, price, COALESCE(image_name, 'default.jpg') as image_name FROM menu_items WHERE category_id = ?",
            (category['id'],)
        ).fetchall()
        menu[category['name']] = items

    conn.close()
    return menu


# Оновлений маршрут для меню
@app.route('/menu')
def menu():
        categories = []

        with sqlite3.connect('cafe.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Отримуємо активні категорії
            cursor.execute("""
                SELECT id, *
                FROM categories 
 
            """)

            categories_data = cursor.fetchall()

            for category in categories_data:
                # Отримуємо товари для кожної категорії з таблиці menu_items
                cursor.execute("""
                                    SELECT id, name, description, price, image_name 
                                    FROM menu_items 
                                    WHERE category_id = ?
                                  
                                """, (category['id'],))

                items = []
                for item in cursor.fetchall():
                    items.append({
                        'id': item['id'],
                        'name': item['name'],
                        'description': item['description'],
                        'price': item['price'],
                        'image': item['image_name'] or 'placeholder.jpg'
                    })

                categories.append({
                    'id': category['id'],
                    'name': category['name'],
                    'description': category['description'],
                    'products': items  # Зберігаємо під ключем 'products' для сумісності з шаблоном
                })



        return render_template('menu.html', categories=categories)


def create_user(username, email, password, phone=None):
    """Створення нового користувача"""
    conn = get_db()
    password_hash = generate_password_hash(password)

    try:
        conn.execute("INSERT INTO users (username, email, password_hash, phone, created_at) VALUES (?, ?, ?, ?, ?)",
                     (username, email, password_hash, phone, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user_by_username(username):
    """Отримання користувача за ім'ям"""
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user



class User(UserMixin):
    def __init__(self, id, is_admin=False):
        self.id = id
        self.is_admin = is_admin
@login_manager.user_loader
@login_manager.user_loader
def load_user(user_id):
    conn = get_db()
    user_data = conn.execute('SELECT id, is_admin FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user_data:
        return User(id=user_data['id'], is_admin=user_data['is_admin'])
    return None


@app.route('/process_checkout', methods=['POST'])
def process_checkout():
    try:
        # Отримання даних форми
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        comments = request.form.get('comments', '').strip()

        if not all([name, phone, address]):
            return "Будь ласка, заповніть всі обов'язкові поля", 400

        # Отримуємо кошик
        cart = session.get('cart', [])
        if not cart:
            return "Ваш кошик порожній", 400

        # Готуємо дані для Telegram
        order_data = {
            'name': name,
            'phone': phone,
            'address': address,
            'notes': comments,
            'order_date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'items': [],
            'total': 0.0
        }

        # Додаємо товари з кошика
        for item in cart:
            order_data['items'].append({
                'name': item.get('name', 'Невідомий товар'),
                'price': float(item.get('price', 0)),
                'quantity': int(item.get('quantity', 1)),
                'sum': float(item.get('price', 0)) * int(item.get('quantity', 1))
            })

        # Розраховуємо загальну суму
        order_data['total'] = sum(item['sum'] for item in order_data['items'])

        # Відправляємо в Telegram
        send_telegram_notification(order_data)

        # Очищаємо кошик
        session.pop('cart', None)

        return redirect(url_for('order_confirmation'))

    except Exception as e:
        print(f"Помилка обробки замовлення: {e}")
        return "Сталася помилка при обробці замовлення", 500

    except Exception as e:
        print(f"Помилка обробки замовлення: {e}")
        return "Сталася помилка при обробці замовлення", 500



# Змінено ім'я функції на унікальне
@app.route('/order/confirmation')
def order_confirmation_page():
    return render_template('order_confirmation.html',
                         order_number=randint(10000, 99999),
                         now=datetime.now())

# Або якщо вам потрібен саме шлях /order/confirmation
@app.route('/order/confirmation')
def order_confirmation_alt():  # Змінив ім'я функції
    return render_template('order_confirmation.html',
                         order_number=randint(10000, 99999),
                         now=datetime.now())


def send_telegram_notification(order_data):
    try:
        message = f"""
        🍰 *Нове замовлення* 🍰
        --------------------------
        📦 *Номер замовлення:* {order_number}
        👤 *Клієнт:* {order_data['name']}
        📞 *Телефон:* `{order_data['phone']}`
        🏠 *Адреса:* {order_data['address']}
        🕒 *Час замовлення:* {order_data['order_date']}
        --------------------------
        *Замовлення:*
        """

        for item in order_data['items']:
            message += f"\n- {item['name']} ×{item['quantity']} = {item['sum']:.2f} грн"

        message += f"""
        --------------------------
        💵 *Загальна сума:* {order_data['total']:.2f} грн
        📝 *Коментар:* {order_data.get('notes', 'Немає')}
        --------------------------
        """

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        for chat_id in TELEGRAM_CHAT_ID:
            response = requests.post(url, json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            })
            print(f"Telegram response: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Помилка відправки в Telegram: {e}")

def calculate_total():
    cart_items = session.get('cart', [])
    try:
        # Перетворюємо ціни та кількість у числа
        total = sum(float(item['price']) * int(item['quantity']) for item in cart_items)
        return round(total, 2)
    except (ValueError, TypeError, KeyError) as e:
        print(f"Помилка розрахунку суми: {e}")
        return 0.0
# Декоратори для контролю доступу
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Будь ласка, увійдіть для доступу до цієї сторінки', 'warning')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Доступ заборонено. Потрібні права адміністратора', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# Маршрути авторизації
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')

        if create_user(username, email, password, phone):
            flash('Реєстрація успішна! Будь ласка, увійдіть.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Користувач з таким ім\'ям або email вже існує', 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = verify_user(username, password)
        if user:
            user_obj = User(user['id'])

            login_user(user_obj)  # Виправлено помилковий "lodef" на "login_user"
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash('Ви успішно увійшли!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Невірне ім\'я користувача або пароль', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    flash('Ви вийшли з акаунту', 'info')
    return redirect(url_for('index'))


# Основні маршрути
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')



@app.route('/order', methods=['GET', 'POST'])
@login_required
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

        try:
            # Збираємо товари з форми
            for key, value in request.form.items():
                if key.startswith('quantity-') and int(value) > 0:
                    item_id = key.replace('quantity-', '')
                    quantity = int(value)

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
                # Зберігаємо замовлення
                cursor = conn.cursor()
                cursor.execute(
                    """INSERT INTO orders 
                    (customer_name, phone, address, notes, total, order_date, user_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (name, phone, address, notes, total, order_date, session['user_id'])
                )
                order_id = cursor.lastrowid

                # Зберігаємо позиції замовлення
                for item in items:
                    cursor.execute(
                        """INSERT INTO order_items 
                        (order_id, item_id, item_name, item_price, quantity) 
                        VALUES (?, ?, ?, ?, ?)""",
                        (order_id, item['id'], item['name'], item['price'], item['quantity'])
                    )

                conn.commit()

                # Готуємо дані для Telegram
                order_data = {
                    'name': name,
                    'phone': phone,
                    'address': address,
                    'notes': notes,
                    'order_date': order_date,
                    'items': items,
                    'total': total
                }

                # Відправляємо сповіщення в Telegram (у фоні)
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
        menu = get_menu()
        return render_template('order.html', menu=menu)


@app.route('/order/confirmation')
def order_confirmation():
    return render_template('order_confirmation.html',
                         order_number=randint(10000, 99999),
                         now=datetime.now())




@app.route('/admin')
@admin_required
def admin_panel():
    conn = get_db()
    try:
        # Статистика для адмінпанелі
        orders_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        users_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        recent_orders = conn.execute(
            """SELECT o.id, o.customer_name, o.order_date, o.total, u.username 
               FROM orders o 
               LEFT JOIN users u ON o.user_id = u.id 
               ORDER BY o.order_date DESC 
               LIMIT 5"""
        ).fetchall()

        return render_template('admin_panel.html',
                               orders_count=orders_count,
                               users_count=users_count,
                               recent_orders=recent_orders)
    finally:
        conn.close()


# Статичні файли
@app.route('/images/menu/<filename>')
def serve_menu_image(filename):
    return send_from_directory('static/images/menu', filename)


# AR маршрути
@app.route('/ar')
def ar_view():
    return render_template('ar.html')


@app.route('/webar/')
def full_ar_view():
    return render_template('webar_scanner.html')


@app.route('/webar/targets/<path:filename>')
def serve_ar_targets(filename):
    return send_from_directory('WEBAR/static/targets', filename)


@app.route('/webar/models/<path:filename>')
def serve_ar_models(filename):
    return send_from_directory('WEBAR/static/models', filename)


@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total = 0

    # Перетворюємо список у словник для зручності
    cart_dict = {}
    for item in cart:
        if str(item['id']) in cart_dict:
            cart_dict[str(item['id'])]['quantity'] += item['quantity']
        else:
            cart_dict[str(item['id'])] = {
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity'],
                'image': item.get('image', 'placeholder.jpg')
            }
        total += item['price'] * item['quantity']
    global order_number
    order_number = randint(1, 99999)
    now = datetime.utcnow()
    return render_template('cart.html', cart_items=cart_dict.values(), total=total,random_number=order_number, now=now)


@app.route('/remove_from_cart', methods=['POST'])
@login_required

def remove_from_cart():
    item_id = request.form.get('item_id')
    if 'cart' in session:
        session['cart'] = [item for item in session['cart'] if str(item['id']) != item_id]
        session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/checkout')
@login_required
def checkout():
    if 'cart' not in session or not session['cart']:
        flash('Ваш кошик порожній', 'warning')
        return redirect(url_for('menu'))

    return render_template('checkout.html')

# Маршрут для додавання до кошика
@app.route('/add-to-cart', methods=['POST'])

def add_to_cart():
    try:
        data = request.get_json()
        item_id = data.get('id')
        quantity = int(data.get('quantity', 1))

        if not item_id:
            return jsonify({'status': 'error', 'message': 'Не вказано ID товару'}), 400

        # Отримуємо інформацію про товар з бази даних
        with sqlite3.connect('cafe.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, image_name FROM menu_items WHERE id = ?", (item_id,))
            item = cursor.fetchone()

            if not item:
                return jsonify({'status': 'error', 'message': 'Товар не знайдено'}), 404

            # Додаємо в кошик
            if 'cart' not in session:
                session['cart'] = []

            # Перевіряємо чи товар вже є в кошику
            existing_item = next((i for i in session['cart'] if i['id'] == item['id']), None)

            if existing_item:
                existing_item['quantity'] += quantity
            else:
                session['cart'].append({
                    'id': item['id'],
                    'name': item['name'],
                    'price': float(item['price']),
                    'quantity': quantity,
                    'image': item['image_name'] or 'placeholder.jpg'
                })

            session.modified = True

            return jsonify({
                'status': 'success',
                'cart_count': len(session['cart']),
                'message': f"{item['name']} додано до кошика"
            })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/toggle_favorite', methods=['POST'])
@login_required
def toggle_favorite():
    try:
        item_id = request.form.get('item_id')
        if not item_id:
            return jsonify({'success': False, 'message': 'Не вказано ID товару'}), 400

        conn = get_db()

        # Використовуємо current_user з Flask-Login замість session
        user_id = current_user.id

        # Перевіряємо, чи товар вже є в улюблених
        is_favorite = conn.execute('SELECT 1 FROM favorites WHERE user_id = ? AND item_id = ?',
                                   (user_id, item_id)).fetchone()

        if is_favorite:
            conn.execute('DELETE FROM favorites WHERE user_id = ? AND item_id = ?',
                         (user_id, item_id))
            action = 'removed'
        else:
            conn.execute('INSERT INTO favorites (user_id, item_id) VALUES (?, ?)',
                         (user_id, item_id))
            action = 'added'

        conn.commit()
        conn.close()
        return jsonify({'success': True, 'action': action})

    except Exception as e:
        print(f"Error in toggle_favorite: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/update-cart-item', methods=['POST'])
def update_cart_item():
    item_id = request.form.get('item_id')
    quantity = int(request.form.get('quantity', 1))

    if 'cart' in session:
        for item in session['cart']:
            if str(item['id']) == item_id:
                item['quantity'] = quantity
                break
        session.modified = True

    return redirect(url_for('view_cart'))


# Декоратор для перевірки авторизації
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


# Маршрут для профілю
@app.route('/profile')
@login_required
def profile():
    try:
        with sqlite3.connect('cafe.db') as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Отримуємо дані користувача
            cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
            user = cursor.fetchone()

            if not user:
                return redirect(url_for('logout'))

            # Отримуємо історію замовлень
            cursor.execute("""
                SELECT o.id, o.order_date, o.status, o.total, 
                       GROUP_CONCAT(mi.name || ' (×' || oi.quantity || ')', ', ') AS items
                FROM orders o
                JOIN order_items oi ON o.id = oi.order_id
                JOIN menu_items mi ON oi.item_id = mi.id
                WHERE o.user_id = ?
                GROUP BY o.id
                ORDER BY o.order_date DESC
                LIMIT 5
            """, (session['user_id'],))
            orders = cursor.fetchall()

        return render_template('profile.html', user=dict(user), orders=orders)

    except Exception as e:
        print(f"Error in profile route: {e}")
        return redirect(url_for('home'))





# Маршрут для скасування замовлення
@app.route('/cancel-order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    try:
        with sqlite3.connect('cafe.db') as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE orders 
                SET status = 'cancelled' 
                WHERE id = ? AND user_id = ? AND status = 'new'
            """, (order_id, session['user_id']))
            conn.commit()

            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Замовлення не знайдено або не може бути скасоване'})

            return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/get_favorites')
@login_required
def get_favorites():
    try:
        conn = get_db()
        favorites = conn.execute('SELECT item_id FROM favorites WHERE user_id = ?',
                               (current_user.id,)).fetchall()
        conn.close()
        return jsonify([item['item_id'] for item in favorites])
    except Exception as e:
        print(f"Error in get_favorites: {e}")
        return jsonify([])


@app.route('/admin/menu')
@admin_required
def admin_menu():
    conn = get_db()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    menu_items = conn.execute('''
        SELECT m.*, c.name as category_name 
        FROM menu_items m
        JOIN categories c ON m.category_id = c.id
    ''').fetchall()
    conn.close()
    return render_template('admin_menu.html', categories=categories, menu_items=menu_items)


@app.route('/admin/menu/add', methods=['GET', 'POST'])
@admin_required
def add_menu_item():
    if request.method == 'POST':
        category_id = request.form['category_id']
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])

        # Обробка зображення
        image = request.files['image']
        image_name = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_name = f"item_{int(datetime.now().timestamp())}_{filename}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))

        conn = get_db()
        conn.execute('''
            INSERT INTO menu_items (category_id, name, description, price, image_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (category_id, name, description, price, image_name))
        conn.commit()
        conn.close()

        flash('Пункт меню успішно додано!', 'success')
        return redirect(url_for('admin_menu'))

    conn = get_db()
    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()
    return render_template('add_menu_item.html', categories=categories)


@app.route('/admin/menu/delete/<int:item_id>', methods=['POST'])
@admin_required
def delete_menu_item(item_id):
    conn = get_db()

    # Отримуємо інформацію про зображення для видалення
    item = conn.execute('SELECT image_name FROM menu_items WHERE id = ?', (item_id,)).fetchone()

    # Видаляємо запис з БД
    conn.execute('DELETE FROM menu_items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()

    # Видаляємо пов'язане зображення
    if item and item['image_name']:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item['image_name']))
        except OSError:
            pass

    flash('Пункт меню успішно видалено!', 'success')
    return redirect(url_for('admin_menu'))


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/admin/menu/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit_menu_item(item_id):
    conn = get_db()

    if request.method == 'POST':
        category_id = request.form['category_id']
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        image = request.files['image']

        # Отримуємо поточні дані товару
        current_item = conn.execute('SELECT image_name FROM menu_items WHERE id = ?', (item_id,)).fetchone()
        image_name = current_item['image_name']

        # Якщо завантажено нове зображення
        if image and allowed_file(image.filename):
            # Видаляємо старе зображення
            if image_name:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image_name))
                except OSError:
                    pass

            # Зберігаємо нове зображення
            filename = secure_filename(image.filename)
            image_name = f"item_{int(datetime.now().timestamp())}_{filename}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))

        # Оновлюємо запис в БД
        conn.execute('''
            UPDATE menu_items 
            SET category_id = ?, name = ?, description = ?, price = ?, image_name = ?
            WHERE id = ?
        ''', (category_id, name, description, price, image_name, item_id))
        conn.commit()
        conn.close()

        flash('Пункт меню успішно оновлено!', 'success')
        return redirect(url_for('admin_menu'))

    # GET-запит - показуємо форму редагування
    item = conn.execute('''
        SELECT m.*, c.name as category_name 
        FROM menu_items m
        JOIN categories c ON m.category_id = c.id
        WHERE m.id = ?
    ''', (item_id,)).fetchone()

    categories = conn.execute('SELECT * FROM categories').fetchall()
    conn.close()

    if not item:
        flash('Пункт меню не знайдено', 'error')
        return redirect(url_for('admin_menu'))

    return render_template('edit_menu_item.html', item=item, categories=categories)


@app.route('/admin/users')
@admin_required
def admin_users():
    conn = get_db()
    users = conn.execute(
        'SELECT id, username, email, created_at, is_admin FROM users ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/toggle_admin/<int:user_id>', methods=['POST'])
@admin_required
def toggle_admin(user_id):
    if current_user.id == user_id:
        flash('Ви не можете змінити свої власні права адміністратора', 'danger')
        return redirect(url_for('admin_users'))

    conn = get_db()
    user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,)).fetchone()

    if not user:
        flash('Користувача не знайдено', 'danger')
        return redirect(url_for('admin_users'))

    new_status = not user['is_admin']
    conn.execute('UPDATE users SET is_admin = ? WHERE id = ?', (new_status, user_id))
    conn.commit()
    conn.close()

    action = "надано" if new_status else "прибрано"
    flash(f'Права адміністратора {action} для користувача', 'success')
    return redirect(url_for('admin_users'))


@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    if current_user.id == user_id:
        flash('Ви не можете видалити самого себе', 'danger')
        return redirect(url_for('admin_users'))

    conn = get_db()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    flash('Користувача успішно видалено', 'success')
    return redirect(url_for('admin_users'))

# Запуск додатку
if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False для ngrok
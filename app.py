from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
import sqlite3
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import random
import string
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'shoestore'  # Replace with a secure key in production
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'wenbusale383@gmail.com'
app.config['MAIL_PASSWORD'] = 'bfmd neqb ltiv txrp'  # App-specific password
app.config['MAIL_DEFAULT_SENDER'] = 'maxwellusenaka@gmail.com'

mail = Mail(app)

# Ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  phone TEXT NOT NULL,
                  password TEXT NOT NULL,
                  address TEXT,
                  joined_date TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS shoes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  category TEXT NOT NULL,
                  size TEXT NOT NULL,
                  price REAL NOT NULL,
                  details TEXT NOT NULL,
                  image TEXT NOT NULL,
                  rating REAL)''')
    # Updated orders table to use user_email instead of user_name
    c.execute('''CREATE TABLE IF NOT EXISTS orders 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  shoe_id INTEGER NOT NULL,
                  user_email TEXT NOT NULL,
                  user_phone TEXT NOT NULL,
                  status TEXT NOT NULL,
                  order_date TEXT NOT NULL,
                  total REAL NOT NULL,
                  FOREIGN KEY(shoe_id) REFERENCES shoes(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS admins 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT NOT NULL,
                  shoe_id INTEGER NOT NULL,
                  quantity INTEGER NOT NULL,
                  revenue REAL NOT NULL,
                  profit_loss REAL NOT NULL,
                  FOREIGN KEY(shoe_id) REFERENCES shoes(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS contacts 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT NOT NULL,
                  message TEXT NOT NULL,
                  date TEXT NOT NULL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS refunds 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  order_id INTEGER NOT NULL,
                  customer TEXT NOT NULL,
                  amount REAL NOT NULL,
                  reason TEXT NOT NULL,
                  date TEXT NOT NULL,
                  FOREIGN KEY(order_id) REFERENCES orders(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS reviews 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  order_id INTEGER NOT NULL,
                  rating INTEGER NOT NULL,
                  review TEXT NOT NULL,
                  date TEXT NOT NULL,
                  FOREIGN KEY(order_id) REFERENCES orders(id))''')
    
    # Add address column to users if not exists
    try:
        c.execute('ALTER TABLE users ADD COLUMN address TEXT')
        logger.info("Added address column to existing users table.")
    except sqlite3.OperationalError:
        pass
    
    # Migrate orders table from user_name to user_email if needed
    c.execute("PRAGMA table_info(orders)")
    columns = [col[1] for col in c.fetchall()]
    if 'user_name' in columns and 'user_email' not in columns:
        logger.info("Migrating orders table to use user_email...")
        c.execute('''CREATE TABLE orders_new 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      shoe_id INTEGER NOT NULL,
                      user_email TEXT NOT NULL,
                      user_phone TEXT NOT NULL,
                      status TEXT NOT NULL,
                      order_date TEXT NOT NULL,
                      total REAL NOT NULL,
                      FOREIGN KEY(shoe_id) REFERENCES shoes(id))''')
        c.execute('''INSERT INTO orders_new (id, shoe_id, user_email, user_phone, status, order_date, total)
                     SELECT o.id, o.shoe_id, u.email, o.user_phone, o.status, o.order_date, o.total
                     FROM orders o
                     LEFT JOIN users u ON o.user_name = u.name''')
        c.execute('DROP TABLE orders')
        c.execute('ALTER TABLE orders_new RENAME TO orders')
        logger.info("Orders table migrated successfully.")
    
    conn.commit()
    conn.close()
    populate_initial_data()

def populate_initial_data():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('winslaise383@gmail.com',))
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users (name, email, phone, password, address, joined_date) VALUES (?, ?, ?, ?, ?, ?)',
                  ('Winslaise Shioso', 'winslaise383@gmail.com', '0769525570', generate_password_hash('password123'), 'Kitale, Trans-Nzoia', '2025-02-01'))
        conn.commit()
    c.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('wenslause300@gmail.com',))
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO users (name, email, phone, password, address, joined_date) VALUES (?, ?, ?, ?, ?, ?)',
                  ('Wenslause Busale', 'wenslause300@gmail.com', '0769525570', generate_password_hash('password123'), 'Kitale, Trans-Nzoia', '2025-02-01'))
        conn.commit()
    c.execute('SELECT COUNT(*) FROM shoes')
    if c.fetchone()[0] == 0:
        initial_shoes = [
            (1, "Fashion Men's Sneaker", "Men's Shoes", "42", 899, "Lightweight, breathable running shoes for men.", "nike1.jpg"),
            (2, "Sports Men's Shoes", "Sports Shoes", "40", 1200, "Durable sports shoes for running and training.", "nike4.jpg"),
            (3, "Alagzi Men's Formal Shoes", "Men's Shoes", "43", 1190, "Elegant casual shoes for formal occasions.", "alagzi.jpg"),
            (4, "Couple Canvas Low Top", "Casual Shoes", "38", 759, "Classic casual canvas shoes for couples.", "canvas.jpg")
        ]
        c.executemany('INSERT INTO shoes (id, name, category, size, price, details, image) VALUES (?, ?, ?, ?, ?, ?, ?)', initial_shoes)
        conn.commit()
    c.execute('SELECT COUNT(*) FROM admins WHERE name = ?', ('admin',))
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO admins (name, password) VALUES (?, ?)', ('admin', generate_password_hash('admin')))
        conn.commit()
        logger.info("Admin user created with name: admin, password: admin (hashed)")
    c.execute('SELECT COUNT(*) FROM sales')
    if c.fetchone()[0] == 0:
        initial_sales = [
            ('2025-02-27', 15, 7, 2000, -456.15),
            ('2025-02-28', 2, 15, 2000, 1000.00)
        ]
        c.executemany('INSERT INTO sales (date, shoe_id, quantity, revenue, profit_loss) VALUES (?, ?, ?, ?, ?)', initial_sales)
        conn.commit()
        logger.info("Sample sales data added")
    conn.close()

with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password)
        joined_date = datetime.now().strftime('%Y-%m-%d')
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (name, email, phone, password, address, joined_date) VALUES (?, ?, ?, ?, ?, ?)',
                      (name, email, phone, hashed_password, None, joined_date))
            conn.commit()
            conn.close()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'error')
            return redirect(url_for('signup'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        if user and check_password_hash(user[4], password):
            session['user_email'] = email
            session['user_name'] = user[1]
            session['user_phone'] = user[3]
            session['user_address'] = user[5] if len(user) > 5 else None
            logger.debug(f"User logged in: {email}, Session: {session}")
            flash('Login successful!', 'success')
            return redirect(url_for('brands'))
        else:
            flash('Invalid email or password!', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/reset_password', methods=['POST'])
def reset_password():
    email = request.form.get('email')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    
    if user:
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        hashed_temp_password = generate_password_hash(temp_password)
        
        c.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_temp_password, email))
        conn.commit()
        
        msg = Message('Password Reset - Kanaan Shoe Collection',
                     recipients=[email])
        msg.body = f'''
        Hello,

        Your password has been reset. Please use the following temporary password to log in:
        
        Temporary Password: {temp_password}

        After logging in, please change your password immediately from your account page: {url_for('account', _external=True)}

        If you did not request this reset, please contact our support team.

        Regards,
        Kanaan Shoe Collection Team
        '''
        try:
            mail.send(msg)
            flash('A temporary password has been sent to your email. Please check your inbox (and spam folder).', 'success')
        except Exception as e:
            logger.error(f"Failed to send reset email: {str(e)}")
            flash('Failed to send reset email. Please try again later.', 'error')
            conn.close()
            return redirect(url_for('login'))
    else:
        flash('Email not found in our records.', 'error')
    
    conn.close()
    return redirect(url_for('login'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM admins WHERE name = ?', (username,))
        admin = c.fetchone()
        logger.debug(f"Admin fetched: {admin}")
        conn.close()
        if admin and check_password_hash(admin[2], password):
            session['admin'] = admin[1]
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_home'))
        else:
            flash('Invalid username or password! Please try again.', 'error')
            logger.debug(f"Login failed for {username}")
            return redirect(url_for('admin_login'))
    return render_template('admin_login.html')

@app.route('/admin_home')
def admin_home():
    if 'admin' not in session:
        flash('Please log in as admin first!', 'error')
        return redirect(url_for('admin_login'))
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('''SELECT o.id, o.shoe_id, o.user_email, s.name, o.order_date, o.status, o.user_phone, u.address 
                 FROM orders o 
                 JOIN shoes s ON o.shoe_id = s.id 
                 LEFT JOIN users u ON o.user_email = u.email''')
    orders = [{'id': row[0], 'shoe_id': row[1], 'user_email': row[2], 'shoe_name': row[3], 'order_date': row[4], 
               'status': row[5], 'user_phone': row[6], 'user_address': row[7]} for row in c.fetchall()]
    
    c.execute('SELECT id, name, email, phone, address, joined_date FROM users')
    users = [{'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3], 'address': row[4], 'joined_date': row[5]} 
             for row in c.fetchall()]
    
    c.execute('''SELECT sales.id, sales.date, shoes.name, sales.quantity, sales.revenue, sales.profit_loss 
                 FROM sales LEFT JOIN shoes ON sales.shoe_id = shoes.id''')
    sales = [{'id': row[0], 'date': row[1], 'shoe_name': row[2] if row[2] else 'Unknown Shoe', 'quantity': row[3], 
              'revenue': row[4], 'profit_loss': row[5]} for row in c.fetchall()]
    logger.debug(f"Sales data fetched: {sales}")
    
    c.execute('SELECT id, name, category, size, price, details, image FROM shoes')
    products = [{'id': row[0], 'name': row[1], 'category': row[2], 'size': row[3], 'price': row[4], 'details': row[5], 'image': row[6]} 
                for row in c.fetchall()]
    
    c.execute('SELECT id, name, email, message, date FROM contacts')
    contacts = [{'id': row[0], 'name': row[1], 'email': row[2], 'message': row[3], 'date': row[4]} for row in c.fetchall()]
    
    c.execute('''SELECT refunds.id, refunds.order_id, refunds.customer, refunds.amount, refunds.reason, refunds.date 
                 FROM refunds''')
    refunds = [{'id': row[0], 'order_id': row[1], 'customer': row[2], 'amount': row[3], 'reason': row[4], 'date': row[5]} 
               for row in c.fetchall()]
    
    c.execute('SELECT COUNT(*) FROM orders')
    total_orders = c.fetchone()[0]
    c.execute('SELECT COUNT(*) FROM users')
    total_users = c.fetchone()[0]
    c.execute('SELECT SUM(revenue) FROM sales')
    total_sales = c.fetchone()[0] or 0
    conn.close()
    
    return render_template('home.html', admin=session['admin'], orders=orders, users=users, sales=sales, products=products, 
                          contacts=contacts, refunds=refunds, total_orders=total_orders, total_users=total_users, total_sales=total_sales)

@app.route('/update_order', methods=['POST'])
def update_order():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    order_id = request.form['order_id']
    status = request.form['status']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Order updated successfully!'})

@app.route('/add_order', methods=['POST'])
def add_order():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    customer_email = request.form['customer']  # Expecting email now
    shoe_id = request.form['shoe_id']
    phone = request.form['phone']
    date = request.form['date']
    status = request.form['status']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT price FROM shoes WHERE id = ?', (shoe_id,))
    shoe = c.fetchone()
    total = float(shoe[0]) if shoe else 0.0
    c.execute('INSERT INTO orders (shoe_id, user_email, user_phone, status, order_date, total) VALUES (?, ?, ?, ?, ?, ?)',
              (shoe_id, customer_email, phone, status, date, total))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Order added successfully!'})

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    name = request.form['name']
    price = float(request.form['price'])
    details = request.form['details']
    category = request.form['category'].replace('_', ' ').title()
    size = request.form['size']
    
    file = request.files['image']
    if file and file.filename:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    else:
        return jsonify({'success': False, 'message': 'Image upload failed!'}), 400
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO shoes (name, category, size, price, details, image) VALUES (?, ?, ?, ?, ?, ?)',
              (name, category, size, price, details, filename))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Product added successfully!'})

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    product_id = request.form['product_id']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT image FROM shoes WHERE id = ?', (product_id,))
    image = c.fetchone()
    if image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image[0])
        if os.path.exists(image_path):
            os.remove(image_path)
    c.execute('DELETE FROM shoes WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Product deleted successfully!'})

@app.route('/add_user', methods=['POST'])
def add_user():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    password = generate_password_hash('default123')
    joined_date = request.form['joined']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO users (name, email, phone, password, address, joined_date) VALUES (?, ?, ?, ?, ?, ?)',
              (name, email, phone, password, None, joined_date))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'User added successfully!'})

@app.route('/update_user', methods=['POST'])
def update_user():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    user_id = request.form['user_id']
    name = request.form['name']
    email = request.form['email']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE users SET name = ?, email = ? WHERE id = ?', (name, email, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'User updated successfully!'})

@app.route('/add_sale', methods=['POST'])
def add_sale():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    date = request.form['date']
    shoe_id = request.form['shoe_id']
    quantity = int(request.form['quantity'])
    revenue = float(request.form['revenue'])
    profit_loss = float(request.form['profit_loss'])
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO sales (date, shoe_id, quantity, revenue, profit_loss) VALUES (?, ?, ?, ?, ?)',
              (date, shoe_id, quantity, revenue, profit_loss))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Sale added successfully!'})

@app.route('/add_contact_reply', methods=['POST'])
def add_contact_reply():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    contact_id = request.form['contact_id']
    reply = request.form['reply']
    return jsonify({'success': True, 'message': 'Reply sent (mocked)!'})

@app.route('/add_refund', methods=['POST'])
def add_refund():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    order_id = request.form['order_id']
    customer = request.form['customer']
    amount = float(request.form['amount'])
    reason = request.form['reason']
    date = datetime.now().strftime('%Y-%m-%d')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('INSERT INTO refunds (order_id, customer, amount, reason, date) VALUES (?, ?, ?, ?, ?)',
              (order_id, customer, amount, reason, date))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Refund processed successfully!'})

@app.route('/admin_change_password', methods=['POST'])
def admin_change_password():
    if 'admin' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New password and confirmation do not match!'}), 400
    
    admin_name = session['admin']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT password FROM admins WHERE name = ?', (admin_name,))
    admin = c.fetchone()
    
    if admin and check_password_hash(admin[0], current_password):
        hashed_password = generate_password_hash(new_password)
        c.execute('UPDATE admins SET password = ? WHERE name = ?', (hashed_password, admin_name))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Password changed successfully!'})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Current password is incorrect!'}), 400

@app.route('/brands')
def brands():
    email = session.get('user_email', None)
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, name, category, size, price, details, image FROM shoes')
    shoes = [{'id': row[0], 'name': row[1], 'category': row[2], 'size': row[3], 'price': row[4], 'details': row[5], 'image': row[6]} 
             for row in c.fetchall()]
    conn.close()
    return render_template('brands.html', email=email, shoes=shoes)

@app.route('/order', methods=['POST'])
def order():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please log in to place an order!'}), 401
    shoe_id = request.form.get('shoe_id')
    user_email = session.get('user_email')  # Use email from session
    user_phone = session.get('user_phone')
    order_date = datetime.now().strftime('%Y-%m-%d')
    status = 'pending'
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT price FROM shoes WHERE id = ?', (shoe_id,))
    shoe = c.fetchone()
    if not shoe:
        conn.close()
        return jsonify({'success': False, 'message': 'Shoe not found!'}), 404
    total = float(shoe[0])
    try:
        c.execute('INSERT INTO orders (shoe_id, user_email, user_phone, status, order_date, total) VALUES (?, ?, ?, ?, ?, ?)',
                  (shoe_id, user_email, user_phone, status, order_date, total))
        conn.commit()
        logger.debug(f"Order placed: shoe_id={shoe_id}, user_email={user_email}, status={status}")
    except sqlite3.IntegrityError as e:
        logger.error(f"Database error: {str(e)}")
        conn.close()
        return jsonify({'success': False, 'message': 'Database error occurred!'}), 500
    conn.close()
    return jsonify({'success': True, 'message': 'Order placed successfully!'})

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_phone', None)
    session.pop('user_address', None)
    session.pop('admin', None)
    flash('You have been logged out!', 'success')
    return redirect(url_for('index'))

@app.route('/account')
def account():
    if 'user_email' not in session:
        flash('Please log in first!', 'error')
        return redirect(url_for('login'))
    email = session['user_email']
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('SELECT name, email, phone, address FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        if user:
            logger.debug(f"Rendering account for: {user}")
            return render_template('account.html', email=user[1], name=user[0], phone=user[2], address=user[3])
    except sqlite3.OperationalError:
        c.execute('SELECT name, email, phone FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        if user:
            logger.debug(f"Rendering account (fallback) for: {user}")
            return render_template('account.html', email=user[1], name=user[0], phone=user[2], address=None)
    return render_template('account.html', email=email, name='User', phone='0769525570', address='Kitale, Trans-Nzoia')

@app.route('/get_orders', methods=['GET'])
def get_orders():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please log in to view orders!'}), 401
    user_email = session.get('user_email')  # Use email from session
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''SELECT o.id, s.name AS shoe_name, o.order_date, o.status, o.total 
                 FROM orders o 
                 JOIN shoes s ON o.shoe_id = s.id 
                 WHERE o.user_email = ?''', (user_email,))
    orders = [{'id': row[0], 'shoe_name': row[1], 'order_date': row[2], 'status': row[3], 'total': row[4]} 
              for row in c.fetchall()]
    conn.close()
    logger.debug(f"Orders fetched for {user_email}: {orders}")
    return jsonify(orders)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please log in to update profile!'}), 401
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    user_email = session['user_email']
    
    logger.debug(f"Updating profile: Old email={user_email}, New email={email}, Name={name}, Phone={phone}")
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('SELECT id FROM users WHERE email = ?', (user_email,))
        if not c.fetchone():
            conn.close()
            logger.error(f"Profile update failed: User with email {user_email} not found in database")
            return jsonify({'success': False, 'message': 'User not found!'}), 404
        
        c.execute('UPDATE users SET name = ?, email = ?, phone = ? WHERE email = ?', 
                  (name, email, phone, user_email))
        conn.commit()
        
        session['user_email'] = email
        session['user_name'] = name
        session['user_phone'] = phone
        logger.debug(f"Profile updated: New session={session}")
        conn.close()
        return jsonify({'success': True, 'message': 'Profile updated successfully!'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Email already exists!'}), 400

@app.route('/update_password', methods=['POST'])
def update_password():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please log in to update password!'}), 401
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    user_email = session['user_email']
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT password FROM users WHERE email = ?', (user_email,))
    user = c.fetchone()
    if user and check_password_hash(user[0], current_password):
        hashed_password = generate_password_hash(new_password)
        c.execute('UPDATE users SET password = ? WHERE email = ?', (hashed_password, user_email))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Password updated successfully!'})
    else:
        conn.close()
        return jsonify({'success': False, 'message': 'Current password is incorrect!'}), 400

@app.route('/update_address', methods=['POST'])
def update_address():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please log in to update address!'}), 401
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    user_email = session['user_email']
    
    logger.debug(f"Updating address: Old email={user_email}, New email={email}, Name={name}, Phone={phone}, Address={address}")
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('SELECT id FROM users WHERE email = ?', (user_email,))
        if not c.fetchone():
            conn.close()
            logger.error(f"Address update failed: User with email {user_email} not found in database")
            return jsonify({'success': False, 'message': 'User not found!'}), 404
        
        c.execute('UPDATE users SET name = ?, email = ?, phone = ?, address = ? WHERE email = ?', 
                  (name, email, phone, address, user_email))
        conn.commit()
        
        session['user_email'] = email
        session['user_name'] = name
        session['user_phone'] = phone
        session['user_address'] = address
        logger.debug(f"Address updated: New session={session}")
        conn.close()
        return jsonify({'success': True, 'message': 'Address updated successfully!'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Email already exists!'}), 400

@app.route('/submit_review', methods=['POST'])
def submit_review():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please log in to submit a review!'}), 401
    order_id = request.form.get('order_id')
    rating = request.form.get('rating')
    review = request.form.get('review')
    date = datetime.now().strftime('%Y-%m-%d')
    
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO reviews (order_id, rating, review, date) VALUES (?, ?, ?, ?)',
                  (order_id, rating, review, date))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Review submitted successfully!'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Error submitting review!'}), 400

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    if 'user_email' not in session:
        return jsonify({'success': False, 'message': 'Please log in to cancel an order!'}), 401
    order_id = request.form.get('order_id')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    try:
        c.execute('UPDATE orders SET status = ? WHERE id = ? AND user_email = ?', 
                  ('Cancelled', order_id, session.get('user_email')))
        if c.rowcount == 0:
            conn.close()
            return jsonify({'success': False, 'message': 'Order not found or unauthorized!'}), 404
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Order cancelled successfully!'})
    except sqlite3.Error:
        conn.close()
        return jsonify({'success': False, 'message': 'Error cancelling order!'}), 500

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == '__main__':
    app.run(debug=True)
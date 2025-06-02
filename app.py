from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5 per secund", "100 per minut "]  # istalgancha sozlashingiz mumkin
)

app.secret_key = 'bu_sirli_soz'

def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    return conn

# ----------- LOGIN -----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM customers WHERE email = ? AND password = ?", (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect('/')
        else:
            error = "❌ Email yoki parol noto‘g‘ri!"
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ----------- REGISTER -----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        company = request.form.get('company')
        password = request.form['password']
        conn = get_db_connection()
        existing = conn.execute("SELECT * FROM customers WHERE email = ?", (email,)).fetchone()
        if existing:
            error = "❌ Bu email allaqachon ro‘yxatdan o‘tgan."
        else:
            conn.execute("INSERT INTO customers (name, email, phone, company, password) VALUES (?, ?, ?, ?, ?)",
                         (name, email, phone, company, password))
            conn.commit()
            user = conn.execute("SELECT * FROM customers WHERE email = ?", (email,)).fetchone()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            conn.close()
            return redirect('/')
        conn.close()
    return render_template('register.html', error=error)

# ----------- MIJOZLAR -----------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers").fetchall()
    conn.close()
    return render_template('index.html', customers=customers)

@app.route('/edit/<int:id>')
def edit_customer(id):
    conn = get_db_connection()
    customer = conn.execute("SELECT * FROM customers WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template('edit.html', customer=customer)

@app.route('/update/<int:id>', methods=['POST'])
def update_customer(id):
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    company = request.form.get('company')
    conn = get_db_connection()
    conn.execute("UPDATE customers SET name=?, email=?, phone=?, company=? WHERE id=?",
                 (name, email, phone, company, id))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM customers WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# ----------- MAHSULOTLAR -----------
@app.route('/products')
def product_list():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        size = request.form['size']
        color = request.form['color']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        description = request.form['description']
        conn = get_db_connection()
        conn.execute("INSERT INTO products (name, category, size, color, price, stock, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                     (name, category, size, color, price, stock, description))
        conn.commit()
        conn.close()
        return redirect('/products')
    return render_template('add_product.html')

@app.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect('/products')

# ----------- SOTISH -----------
@app.route('/sell', methods=['GET', 'POST'])
def sell_product():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    customers = conn.execute("SELECT id, name FROM customers").fetchall()
    products = conn.execute("SELECT id, name, stock FROM products WHERE stock > 0").fetchall()

    if request.method == 'POST':
        customer_id = int(request.form['customer'])
        product_id = int(request.form['product'])
        quantity = int(request.form['quantity'])

        stock_row = conn.execute("SELECT stock FROM products WHERE id = ?", (product_id,)).fetchone()
        if stock_row and stock_row['stock'] >= quantity:
            conn.execute("INSERT INTO sales (product_id, customer_id, quantity, date) VALUES (?, ?, ?, DATE('now'))",
                         (product_id, customer_id, quantity))
            conn.execute("UPDATE products SET stock = stock - ? WHERE id = ?",
                         (quantity, product_id))
            conn.commit()
            flash("✅ Mahsulot muvaffaqiyatli sotildi!")
        else:
            flash("❌ Yetarli mahsulot yo‘q!")
        conn.close()
        return redirect('/sell')

    conn.close()
    return render_template('sell.html', customers=customers, products=products)

# ----------- STATISTIKA -----------
@app.route('/stats')
def stats():
    if 'user_id' not in session:
        return redirect('/login')
    conn = get_db_connection()
    result = conn.execute("""
        SELECT p.name AS product_name, SUM(s.quantity) AS total_sold
        FROM sales s
        JOIN products p ON s.product_id = p.id
        GROUP BY p.name
        ORDER BY total_sold DESC
    """).fetchall()
    conn.close()

    labels = [row['product_name'] for row in result]
    data = [row['total_sold'] for row in result]

    return render_template('stats.html', labels=labels, data=data)

if __name__ == '__main__':
    app.run(debug=True)

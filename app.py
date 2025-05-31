from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'bu_sirli_soz'  # session ishlashi uchun

# SQL Server ulanish
conn = pyodbc.connect(
    r'DRIVER={SQL Server};SERVER=DESKTOP-4TBFSCU\SQLEXPRESS;DATABASE=CRM;Trusted_Connection=yes;'
)

# ----------- LOGIN -----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor()
    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM Customers WHERE Email = ? AND Password = ?", (email, password))
        user = cursor.fetchone()
        if user:
            session['user_id'] = user.CustomerID
            session['user_name'] = user.FullName
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
    cursor = conn.cursor()
    error = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']
        password = request.form['password']

        cursor.execute("SELECT * FROM Customers WHERE Email = ?", (email,))
        if cursor.fetchone():
            error = "❌ Bu email allaqachon ro‘yxatdan o‘tgan."
        else:
            cursor.execute("""
                INSERT INTO Customers (FullName, Email, Phone, Company, Password)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, phone, company, password))
            conn.commit()
            cursor.execute("SELECT * FROM Customers WHERE Email = ?", (email,))
            user = cursor.fetchone()
            session['user_id'] = user.CustomerID
            session['user_name'] = user.FullName
            return redirect('/')
    return render_template('register.html', error=error)

# ----------- MIJOZLAR (asosiy sahifa) -----------
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers")
    customers = cursor.fetchall()
    return render_template('index.html', customers=customers)

@app.route('/edit/<int:id>')
def edit_customer(id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Customers WHERE CustomerID = ?", (id,))
    customer = cursor.fetchone()
    return render_template('edit.html', customer=customer)

@app.route('/update/<int:id>', methods=['POST'])
def update_customer(id):
    cursor = conn.cursor()
    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    company = request.form['company']
    cursor.execute("""
        UPDATE Customers SET FullName=?, Email=?, Phone=?, Company=? WHERE CustomerID=?
    """, (name, email, phone, company, id))
    conn.commit()
    return redirect('/')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Customers WHERE CustomerID = ?", (id,))
    conn.commit()
    return redirect('/')

# ----------- MAHSULOTLAR -----------
@app.route('/products')
def product_list():
    if 'user_id' not in session:
        return redirect('/login')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if 'user_id' not in session:
        return redirect('/login')
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        size = request.form['size']
        color = request.form['color']
        price = request.form['price']
        stock = request.form['stock']
        desc = request.form['description']
        cursor.execute("""
            INSERT INTO Products (ProductName, Category, Size, Color, Price, Stock, Description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, category, size, color, price, stock, desc))
        conn.commit()
        return redirect('/products')
    return render_template('add_product.html')

@app.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Products WHERE ProductID = ?", (id,))
    conn.commit()
    return redirect('/products')

@app.route('/stats')
def stats():
    if 'user_id' not in session:
        return redirect('/login')

    cursor = conn.cursor()
    cursor.execute("""
        SELECT P.ProductName, SUM(S.Quantity) AS TotalSold
        FROM Sales S
        JOIN Products P ON S.ProductID = P.ProductID
        GROUP BY P.ProductName
        ORDER BY TotalSold DESC
    """)
    result = cursor.fetchall()

    labels = [row.ProductName for row in result]
    data = [row.TotalSold for row in result]

    return render_template('stats.html', labels=labels, data=data)

# ----------- SOTISH -----------
@app.route('/sell', methods=['GET', 'POST'])
def sell_product():
    if 'user_id' not in session:
        return redirect('/login')

    cursor = conn.cursor()
    cursor.execute("SELECT CustomerID, FullName FROM Customers")
    customers = cursor.fetchall()
    cursor.execute("SELECT ProductID, ProductName, Stock FROM Products WHERE Stock > 0")
    products = cursor.fetchall()

    if request.method == 'POST':
        customer_id = request.form['customer']
        product_id = request.form['product']
        quantity = int(request.form['quantity'])

        cursor.execute("SELECT Stock FROM Products WHERE ProductID = ?", (product_id,))
        stock = cursor.fetchone().Stock

        if stock >= quantity:
            cursor.execute("INSERT INTO Sales (CustomerID, ProductID, Quantity) VALUES (?, ?, ?)",
                           (customer_id, product_id, quantity))
            cursor.execute("UPDATE Products SET Stock = Stock - ? WHERE ProductID = ?",
                           (quantity, product_id))
            conn.commit()

            flash("✅ Mahsulot muvaffaqiyatli sotildi!")
            return redirect('/sell')
        else:
            flash("❌ Yetarli mahsulot yo‘q!")
            return redirect('/sell')

    return render_template('sell.html', customers=customers, products=products)

# ----------- RUN -----------
if __name__ == '__main__':
    app.run(debug=True)

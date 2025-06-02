import sqlite3

def create_database():
    conn = sqlite3.connect('crm.db')
    c = conn.cursor()

    # Mijozlar jadvali
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            company TEXT,
            password TEXT NOT NULL
        )
    ''')

    # Mahsulotlar jadvali
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            size TEXT,
            color TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL CHECK (stock >= 0),
            description TEXT
        )
    ''')

    # Sotuvlar jadvali
    c.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            customer_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity > 0),
            date TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
            FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()
    print("✅ Bazaga kerakli jadvallar yaratildi!")

if __name__ == '__main__':
    create_database()

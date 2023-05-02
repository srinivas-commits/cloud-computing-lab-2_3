from flask import Flask, render_template, request, redirect, session
import sqlite3
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = 'mysecretkey'
mydatabase = "data/products.db"

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect(mydatabase)
    c = conn.cursor()
    c.execute("SELECT * FROM product")
    products = c.fetchall()
    
    return render_template('index.html', products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = sqlite3.connect(mydatabase)
        c = conn.cursor()
        c.execute("SELECT * FROM user WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        print(user)
        if user:
            session['user_id'] = user[0]
            return redirect('/')
        else:
            return render_template('login.html', error='Invalid email or password.')
    else:
        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # Form submitted, create new user
        conn = sqlite3.connect(mydatabase)
        c = conn.cursor()
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if username already exists
        c.execute("SELECT * FROM user WHERE email=?", (email,))
        user = c.fetchone()
        if user is not None:
            return render_template("signup.html", error="Email already exists")
        
        # Create new user
        c.execute("INSERT INTO user (email, name, password, is_admin) VALUES (?, ?, ?, ?)", (email, name, password, False))
        conn.commit()

        return redirect('/login')
    else:
        return render_template('signup.html')
    
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Form submitted, create new user
        conn = sqlite3.connect(mydatabase)
        c = conn.cursor()
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        is_admin = True

        # Check if username already exists
        c.execute("SELECT * FROM user WHERE email=?", (email,))
        user = c.fetchone()
        if user is not None:
            return render_template("signup.html", error="Email already exists")
        
        # Create new user
        c.execute("INSERT INTO user (email, name, password, is_admin) VALUES (?, ?, ?, ?)", (email, name, password, is_admin))
        conn.commit()

        return redirect('/login')
    else:
        return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/buy/<int:id>', methods=['GET', 'POST'])
def buy(id):
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    conn = sqlite3.connect(mydatabase)
    c = conn.cursor()   
    c.execute("SELECT * FROM user WHERE id=?",(user_id,))
    user = c.fetchone()
    if request.method == 'POST':
        if user[4]:
            return redirect('/')
        c.execute("SELECT * FROM product WHERE id=?",(id,))
        product = c.fetchone()

        if product:
            strdate = datetime.datetime.utcnow()
            c.execute("INSERT INTO purchase (user_id, product_id, product_name, purchase_date) VALUES (?, ?, ?, ?)", (user_id, product[0], product[1], strdate))
            c.execute("DELETE FROM product WHERE id=?", (product[0],))
            conn.commit()
            return redirect('/')
    else:
        c.execute("SELECT * FROM product WHERE id=?",(id,))
        product = c.fetchone()
        return render_template('buy.html', product=product)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    
    conn = sqlite3.connect(mydatabase)
    c = conn.cursor()   
    c.execute("SELECT * FROM user WHERE id=?",(user_id,))
    user = c.fetchone()
    if user[4] == False:
        return redirect('/')
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        
        c.execute("INSERT INTO product (name, description, price) VALUES (?, ?, ?)", (name, description, price))

        conn.commit()
        return redirect('/')
    else:
        return render_template('add.html')

@app.route('/purchased')
def user_purchases_api():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']

    conn = sqlite3.connect(mydatabase)
    c = conn.cursor()   
    c.execute("SELECT * FROM user WHERE id=?",(user_id,))
    user = c.fetchone()
    if user is None:
        return {'error': f'User with ID {user_id} not found'}

    c.execute("SELECT * FROM purchase WHERE user_id=?",(user_id,))
    user_purchases = c.fetchall()
    return render_template('purchased.html', purchasedlst = user_purchases)

if __name__ == '__main__':
    conn = sqlite3.connect(mydatabase)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS user(id INTEGER NOT NULL, name VARCHAR(50) NOT NULL, email VARCHAR(50) NOT NULL, password VARCHAR(50) NOT NULL, is_admin BOOLEAN, PRIMARY KEY (id), UNIQUE (email))')
    c.execute('CREATE TABLE IF NOT EXISTS product(id INTEGER NOT NULL, name VARCHAR(50) NOT NULL, description VARCHAR(200), price FLOAT NOT NULL, PRIMARY KEY (id))')
    c.execute('CREATE TABLE IF NOT EXISTS purchase(id INTEGER NOT NULL, user_id INTEGER, product_id INTEGER, product_name VARCHAR(50) NOT NULL, purchase_date DATETIME, PRIMARY KEY (id), FOREIGN KEY(user_id) REFERENCES user (id), FOREIGN KEY(product_id) REFERENCES product (id))')
    app.run(debug=True, host='0.0.0.0', port=5000)

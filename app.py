from flask import Flask, request, g
import sqlite3

app = Flask(__name__)
DATABASE = 'test.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query):
    cur = get_db().cursor()
    cur.execute(query)
    return cur.fetchall()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # VULNERABLE SQL QUERY: direct concatenation — DO NOT DO THIS IN REAL APPS
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        results = query_db(query)

        if results:
            return f"Welcome, {username}! You are logged in."
        else:
            return "Login failed!"

    return '''
        <h2>Login</h2>
        <form method="POST">
            Username: <input name="username"><br>
            Password: <input name="password" type="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

@app.route('/search')
def search():
    product = request.args.get('product', '')
    query = f"SELECT name, price FROM products WHERE name LIKE '%{product}%'"
    results = query_db(query)

    html = "<h3>Search Results</h3><ul>"
    for row in results:
        html += f"<li>{row}</li>"
    html += "</ul>"

    return f'''
        <form method="GET">
            Search Product: <input name="product">
            <input type="submit" value="Search">
        </form>
        {html}
    '''

# =============
# Admin Panel
# =============
@app.route('/admin')
def admin():
    return "<h2>This is the Admin Panel! 🔐</h2><p>Only visible after login.</p>"

# =================
# DB Setup Function
# =================
def setup_db():
    with sqlite3.connect(DATABASE) as con:
        cur = con.cursor()
        cur.execute('DROP TABLE IF EXISTS users')
        cur.execute('DROP TABLE IF EXISTS products')

        # Create users table
        cur.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            )
        ''')
        cur.execute("INSERT INTO users (username, password) VALUES ('admin', 'adminpass')")
        cur.execute("INSERT INTO users (username, password) VALUES ('user1', 'user1pass')")

        # Create products table
        cur.execute('''
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL
            )
        ''')
        cur.execute("INSERT INTO products (name, price) VALUES ('Keyboard', 49.99)")
        cur.execute("INSERT INTO products (name, price) VALUES ('Monitor', 149.99)")
        cur.execute("INSERT INTO products (name, price) VALUES ('Mouse', 19.99)")

        con.commit()

# ===============
# Main Entrypoint
# ===============
if __name__ == '__main__':
    setup_db()
    app.run(debug=True)
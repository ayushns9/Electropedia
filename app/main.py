from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import sys 

app = Flask(__name__)

app.secret_key = 'random'

app.config['MYSQL_HOST'] = 'electropedia-dbmsproject44.cgnvoh62xdvo.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'admin123'
app.config['MYSQL_DB'] = 'DBMS'

mysql = MySQL(app)

@app.route('/login', methods  =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user where email=%s and password=%s', (username, password))
        account = cursor.fetchone()
        if(account):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['name']
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect email/password'
    return render_template('index.html', msg = msg)

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    email=""
    password=""
    name=""
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        email = request.form['email']
        password = request.form['password']
        name = request.form['username']
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
        return render_template('register.html', msg=msg)
    if(len(email)==0):
        msg = 'Please fill out the form!'
        return render_template('register.html', msg=msg)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user where email=%s AND password=%s', (email, password))
    account = cursor.fetchone()
    if account:
        msg = 'Account already exists!'
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        msg = 'Invalid email address!'
    elif not re.match(r'[A-Za-z0-9]+', name):
        msg = 'name must contain only characters and numbers!'
    elif not name or not password or not email:
        msg = 'Please fill out the form!'
    else:
        cursor.execute('INSERT INTO user(name, email, password) VALUES (%s, %s, %s)', (name, email, password))
        mysql.connection.commit()
        msg = 'You have successfully registered!'
    return render_template('register.html', msg=msg)

@app.route('/home', methods=['GET', 'POST'])
def home():
    if('loggedin' in session):
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():

    return render_template('add_product.html')

@app.route('/add_sells', methods = ['GET', 'POST'])
def add_sells():
    msg = ""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    p_id = request.form['id']
    link = request.form['link']
    price = request.form['price']
    store = request.form['store']

    cursor.execute(f'Select * from store where name = "{store}"')
    store_t = cursor.fetchall()
    if(len(store_t) == 0):
        cursor.execute(f'Insert into store(name) values("{store}")')
        mysql.connection.commit()
    cursor.execute(f'Select * from store where name = "{store}"')
    store_t = cursor.fetchone()
    s_id = store_t['id']

    try:
        cursor.execute(f'''Insert into sells values({p_id}, {s_id}, {price}, "{link}")''')
        mysql.connection.commit()
    except:
        msg = "Unable to add link!"
    return render_template('add_product.html', msg = msg)

@app.route('/search2', methods=['GET','POST'])
def search2():
    data = []
    print(request.form, file=sys.stderr)
    if 'keyword' in request.form:
        keyword = request.form['keyword']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    qry = f'SELECT * from products where name like "%{keyword}%"'
    cur.execute(qry)
    data = cur.fetchall()
    print(data, file = sys.stderr)
    print(qry, file = sys.stderr)
    return render_template('add_product.html', data = data)

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))
    
@app.route('/view/<int:type>', methods=['GET', 'POST'])
def view(type):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if type == 1:
        type = "Laptop"
    elif type == 2:
        type = "Mobile"
    elif type == 3:
        type = "Camera"
    elif type == 4:
        type = "TV"
    else:
        return render_template("add_product.html")
    cur.execute(f'SELECT * from products where type="{type}"')
    data = cur.fetchall()
    return render_template('list.html', data = data, item='Laptops')

muliple = ""
@app.route('/one_item/<int:id>')
def one_item(id):
    global muliple
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT min(price), link from sells where p_id=%s",(id,))
    best = cur.fetchone()
    print(best,file=sys.stderr)
    u_id = session['id']
    try:
        cur.execute("Insert into clicks values(%s, %s)", (u_id, id))
    except:
        pass
    mysql.connection.commit()
    cur.execute("Select b.p_id from clicks a, clicks b where a.u_id = b.u_id and a.p_id = %s and a.u_id <> %s", (id,u_id))
    viewed = cur.fetchall()
    for i in viewed:
        cur.execute('Select name, image from products where id = %s', (i['p_id'],))
        x = cur.fetchone()
        i['name'] = x['name']
        i['image'] = x['image']
    cur.execute("Select review,user_id from reviews where product_id=%s",(id,))
    reviews = cur.fetchall()
    data=[]
    for i in reviews:
        cur.execute("Select name from user where id=%s",(i['user_id'],))
        data.append([i['review'], cur.fetchone()])
    print(muliple,file=sys.stderr)

    return render_template('one_item.html',best_price = best['min(price)'],best_link=best['link'], id = id, data=data, msg = muliple, viewed = viewed)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'keyword' in request.form:
        keyword = request.form['keyword']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    qry = 'SELECT * from products where name like '
    qry += '"%'
    qry += keyword
    qry += '%"'
    cur.execute(qry)
    data = cur.fetchall()
    return render_template('list.html', data = data)

@app.route('/review/<int:p_id>', methods=['POST', 'GET'])
def review(p_id):
    global muliple
    u_id = session['id']
    review = request.form['review']
    cur = mysql.connection.cursor()
    try:
        cur.execute('INSERT INTO reviews(user_id, product_id, review) VALUES(%s,%s,%s)',(u_id,p_id,review))
        mysql.connection.commit()
        muliple = ""
    except:
        muliple = "You can't add more than one review for the same product!"
    
    return redirect(url_for('one_item', id=p_id))

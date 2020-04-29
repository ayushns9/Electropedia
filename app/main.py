from __future__ import print_function
import sys
from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

app = Flask(__name__)

app.secret_key = 'random'

app.config['MYSQL_HOST'] = 'electropedia-dbmsproject44.cgnvoh62xdvo.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'admin123'
app.config['MYSQL_DB'] = 'DBMS'

mysql = MySQL(app)

@app.route('/')
def func():
    return render_template('index.html')

@app.route('/login', methods  =['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('call get_account(%s, md5(%s))', (username, password))
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
    if(len(email)==0 or name == 'admin'):
        msg = 'Please fill out the form!'
        return render_template('register.html', msg=msg)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM user where email=%s', (email,))
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
        cursor.execute('INSERT INTO user(name, email, password) VALUES (%s, %s, md5(%s))', (name, email, password))
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
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if('name' in request.form and 'link' in request.form and len(request.form) == 3):
        msg = ""
        name=request.form['name']
        image=request.form['link']

        if('laptop' in request.form):
            type = 'Laptop'
        elif('mobile' in request.form):
            type = 'Mobile'
        elif('tv' in request.form):
            type = 'TV'
        else:
            type = 'Camera'
        try:
            cursor.execute('Insert into products(name, type, image) values(%s,%s,%s)',(name,type,image,))
            mysql.connection.commit()
            msg1 = "Prouct added!"
        except:
            msg1 = "Unable to add product!"
    else:
        msg = "Please fill the form"
    return render_template('add_product.html', msg1=msg)

@app.route('/add_sells', methods = ['GET', 'POST'])
def add_sells():
    msg = ""
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if(len(request.form) == 4):
        p_id = request.form['id']
        link = request.form['link']
        price = request.form['price']
        store = request.form['store']

        cursor.execute(f'Select * from store where name = "%s"', (store,))
        store_t = cursor.fetchall()
        if(len(store_t) == 0):
            cursor.execute(f'Insert into store(name) values(%s)', (store,))
            mysql.connection.commit()
        cursor.execute(f'Select * from store where name = %s', (store,))
        store_t = cursor.fetchone()
        s_id = store_t['id']

        try:
            cursor.execute(f'''Insert into sells values(%s, %s, %s, %s)''',(p_id, s_id, price, link))
            mysql.connection.commit()
            msg = "Link added!"
        except:
            msg = "Unable to add link!"
    else:
        msg = "Unable to add link!"
    return render_template('add_product.html', msg = msg)

@app.route('/search2', methods=['GET','POST'])
def search2():
    data = []
    if 'keyword' in request.form:
        keyword = request.form['keyword']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute('''SELECT * FROM products WHERE name LIKE "%{}%"'''.format(keyword))
    data = cur.fetchall()
    return render_template('add_product.html', data = data)

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        return render_template('profile.html', account=account)
    return redirect(url_for('login'))

@app.route('/delete_acccount')
def delete_account():
    global session
    print(session,file=sys.stderr)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('call remove_account(%s)', (session['id'],))
    mysql.connection.commit()
    session = {}
    return render_template('index.html')
    
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
    cur.execute(f'SELECT * from products where type=%s',(type,))
    data = cur.fetchall()
    return render_template('list.html', data = data, item='Laptops')

muliple = ""
@app.route('/one_item/<int:id>')
def one_item(id):
    global muliple
    eprint(session)
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("select a.link,a.p_id, a.s_id, a.price from sells a, (select p_id, min(price) as mp from sells group by p_id)b where a.price=b.mp and a.p_id = b.p_id and a.p_id = %s",(id,))
    best = cur.fetchone()
    u_id = session['id']
    try:
        cur.execute("Insert into clicks values(%s, %s)", (u_id, id))
        mysql.connection.commit()
    except:
        pass 
    cur.execute("Select p.name, p.image, b.p_id from clicks a, clicks b, products p where a.u_id = b.u_id and a.p_id = %s and a.u_id <> %s and b.p_id = p.id", (id,u_id))
    viewed = cur.fetchall()
    cur.execute("Select name, review,user_id from reviews,user where product_id=%s and user_id = id",(id,))
    reviews = cur.fetchall()
    cur.execute('''call get_type(%s)''',(id,))
    type = (cur.fetchone()['type']).lower()
    type += '_specs'
    cur.execute(f'''SELECT * from {type} where p_id=%s''',(id,))
    specs = cur.fetchone()
    return render_template('one_item.html',reviews = reviews, best_price = best['price'],best_link=best['link'], store=best['s_id'] , id = id, msg = muliple, viewed = viewed, specs_col = list(specs.keys()),specs_row=list(specs.values()))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'keyword' in request.form:
        keyword = request.form['keyword']
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    keyword = keyword.replace('"', '\\"')
    if('--' in keyword):
        msg = "No products found"
    cur.execute('''SELECT * FROM products WHERE name LIKE "%{}%"'''.format(keyword))
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


@app.route('/clicked/<int:s_id>/<int:p_id>', methods=['POST', 'GET'])
def clicked(s_id, p_id):
    eprint('called')
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("Insert into clicks_to_website values(%s, %s)",(p_id, s_id))
    mysql.connection.commit()
    return redirect(url_for('one_item',id = p_id))

@app.route('/login_store',methods=['GET', 'POST'])
def login_store():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM store where email=%s and password=md5(%s)', (username, password))
        account = cursor.fetchone()
        if(account):
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['name']
            return redirect(url_for('store_portal'))
        else:
            msg = 'Incorrect email/password'
    return render_template('login_store.html', msg = msg)

@app.route('/store_portal',  methods=['POST', 'GET'])
def store_portal():
    eprint(session)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT name, s_id, p_id,count(p_id), rank() over(order by count(p_id)) myrank FROM clicks_to_website, products p where s_id=%s and p.id = p_id group by p_id order by myrank', (session['id'],))
    data = cursor.fetchall()
    real_data = []
    clicks = 0
    for i in data:
        clicks += i['count(p_id)']
    return render_template('store_portal.html', data = data, clicks = clicks)

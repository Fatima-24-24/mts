from flask import Flask, render_template, request, session
from flask import *
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)

@app.route('/')
def main(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products")
   result = cur.fetchall()
   print(result)
   if 'cart' not in session:
      session['cart'] = []
      stx = 'False'
      x = 0
   else:
      x = len(session['cart'])
      if x == 0:
         stx = 'False'
      else:
         stx = 'True'

   if 'username' in session:
      st='True'
   else:
      st='False'
   print(st)
   return render_template('index.html', data={ 'result': result, 'st': st, 'stx': stx, 'x': x,})

'''@app.route('/buy/<int:id>') 
def user(id): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE id= ?", [id])
   result = cur.fetchall()
   print(result)
   return render_template('buy.html', data={ 'result': result[0],})
'''

@app.route('/buy/<int:id>') 
def user(id): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products")
   result = cur.fetchall()
   cur.execute("SELECT name FROM products WHERE id= ?", [id])
   pr = cur.fetchone()
   print(pr)
   cart = session['cart']
   cart.append(id)
   session['cart'] = cart
   
   x = len(session['cart'])
   if x == 0:
      stx = 'False'
   else:
      stx = 'True'

   if 'username' in session:
      st='True'
   else:
      st='False'
      print(st)
   return render_template('index.html', data={'result': result, 'st': st, 'stx': stx, 'x': x,})

@app.route('/cart')
def cart():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   result = []
   for i in session['cart']:
      cur.execute("SELECT * FROM products WHERE id = ?", [i])
      r = cur.fetchall()
      result.append(r)
   return render_template('cart.html', data={'result': result})

@app.route('/order_reg', methods=['POST']) 
def order_reg():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   prod = dict(request.form)
   print(prod)
   x=''
   y=[]
   for i in prod:
      print(i)
      if prod[i] == 'on':
         x += i + ','
         cur.execute("SELECT * FROM products WHERE id= ?", [i])
         result = cur.fetchall()
         r = result[0]
         y.append(r)
   print(y)
   session['cart'].clear()
   return render_template('buy2.html', data={'y': y, 'x': x,})

@app.route('/orderplur', methods=['POST'])
def orderplur():
   tel = request.form['tel']
   adress = request.form['adress']
   paycard = request.form['paycard']
   id = request.form['id']

   print(id)

   current_time = datetime.now()
   formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   
   cur.execute('SELECT id FROM users WHERE tel=?', (tel,))
   r = cur.fetchone()
   print(r)

   user_id = r[0]


   prise = 0
   idd = id.split(',')
   del idd[-1]
   print(idd)
   for i in idd:
      cur.execute('SELECT prise FROM products WHERE id=?', (i,))
      ss = cur.fetchone()  #fetchall [(),()]
      print(ss)
      prise+=int(ss[0])

   print(user_id, id, prise, formatted_time, adress, paycard)

   conn.execute('INSERT INTO orders (user_id, products, prise, order_time, status, adress, paycard) VALUES (?, ?, ?, ?, ?, ?, ?)',(user_id, id, prise, formatted_time, 'Оформлен', adress, paycard))
   conn.commit()
   conn.close()

   return render_template('orderdone.html')


@app.route('/order', methods=['POST'])
def order():
   tel = request.form['tel']
   adress = request.form['adress']
   paycard = request.form['paycard']
   id = request.form['id']
   print(id)

   current_time = datetime.now()
   formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

   conn = sqlite3.connect('mts.db') 
   cur = conn.cursor()

   cur.execute('SELECT id FROM users WHERE tel=?', (tel,))
   r = cur.fetchone()
   user_id = r[0]

   id = id.split(',')
   del id[-1]
   print(id)
   v = []
   for i in id:
      cur.execute('SELECT name, prise, photo FROM products WHERE id=?', (int(i),))
   #cur.execute('SELECT name, prise, photo FROM products WHERE id=?', (id,))
      d = cur.fetchall()
      print(d)
      pr = d[0]
      v.append(pr)
      print(v)
   conn.execute('INSERT INTO orders (user_id, products, prise, order_time, status, adress, paycard) VALUES (?, ?, ?, ?, ?, ?, ?)',(user_id, pr[0], pr[1], formatted_time, 'Оформлен', adress, paycard))
   conn.commit()
   conn.close()

   return render_template('orderdone.html')


@app.route('/search')
def search(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   form_data = dict(request.args)
   print(form_data)
   if 'requestt' in form_data:
      print(form_data['requestt'])
      cur.execute("SELECT * FROM products WHERE name LIKE ?", ('%' + form_data['requestt'] + '%',))
      result = cur.fetchall()
      if not result:
         return "ошибка", 404
      print(result)
      return render_template('search.html', data={ 'result': result, 'requestt': form_data['requestt']})

@app.route('/add', methods=['POST'])
def add():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()

   login = request.form['login']
   password = request.form['password']
   name = request.form['name']
   surname = request.form['surname']
   tel = request.form['tel']
   position = request.form['position']

   hashed_password = generate_password_hash(password)

   cur.execute('INSERT INTO work (login, password, name, surname, tel, position) VALUES (?, ?, ?, ?, ?, ?)',(login, hashed_password, name, surname, tel, position))
   conn.commit()
   conn.close()

   return render_template('admin.html', s=True)

@app.route('/prod_red')
def prod_red():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products')
   result = cur.fetchall()
   return render_template('prod_red.html', data={ 'result': result,})

@app.route('/add_prod', methods=['POST'])
def add_prod():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()

   photo = request.form['photo']
   name = request.form['name']
   prise = request.form['prise']
   brand = request.form['brand']
   gadget = request.form['gadget']
   description = request.form['description']

   conn.execute('INSERT INTO products (photo, name, prise, brand, gadget, description) VALUES (?, ?, ?, ?, ?, ?)',(photo, name, prise, brand, gadget, description))
   cur.execute('SELECT * FROM products')
   result = cur.fetchall()
   conn.commit()
   conn.close()
   return render_template('prod_red.html', data={ 'result': result,})

@app.route('/red_prod', methods=['POST'])
def red_prod():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()

   prod_id= request.form['prod_id']
   changeto = request.form['changeto']
   changed = request.form['changed']

   cur.execute(f'UPDATE products SET {changeto} = {changed} WHERE id = ?', (prod_id,))
   cur.execute('SELECT * FROM products')
   result = cur.fetchall()
   conn.commit()
   conn.close()
   return render_template('prod_red.html', data={ 'result': result,}) # просто result это словарь, а словарь в качестве входных параметров нельзя передавать в Flask

@app.route('/del_prod', methods=['POST'])
def del_prod():
   prod_id= request.form['prod_id']
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('DELETE FROM products WHERE id = ?', (prod_id,))
   cur.execute('SELECT * FROM products')
   result = cur.fetchall()
   conn.commit()
   conn.close()
   return render_template('prod_red.html', data={ 'result': result,})

@app.route('/order_red', methods=['POST'])
def order_red():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()

   order_id = request.form['order_id']
   new_order_status = request.form['new_order_status']

   cur.execute('UPDATE orders SET status = ? WHERE order_id = ?', (new_order_status, order_id))
   cur.execute('SELECT * FROM orders')
   result = cur.fetchall()
   conn.commit()
   conn.close()
   return render_template('order_red.html', data={ 'result': result,}) # просто result это словарь, а словарь в качестве входных параметров нельзя передавать в Flask

@app.route('/work_form')
def work_form():
   return render_template('enterlk.html')

@app.route('/work', methods=['POST'])
def work():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   login = request.form['username']
   password = request.form['password']

   cur.execute('SELECT password FROM work WHERE login=?', (login,))
   passworddb = cur.fetchone()

   cur.execute('SELECT position FROM work WHERE login=?', (login,))
   pos = cur.fetchone()

   if passworddb and check_password_hash(passworddb[0], password):
      if pos[0]=='admin':
         return render_template('admin.html')
      if pos[0]=='prod_red':
         cur.execute('SELECT * FROM products')
         result = cur.fetchall()
         return render_template('prod_red.html', data={ 'result': result,})
      if pos[0]=='order_red':
         cur.execute('SELECT * FROM orders')
         result = cur.fetchall()
         return render_template('order_red.html', data={ 'result': result,}) # просто result это словарь, а словарь в качестве входных параметров нельзя передавать в Flask
   else:
      return render_template('wrongregwork.html')

@app.route('/r') #Войти в свой аккаунт
def r(): 
   if 'username' in session:
      conn = sqlite3.connect('mts.db')
      cur = conn.cursor()
      cur.execute('SELECT * FROM users WHERE username=?', (session['username'],))
      result = cur.fetchall()
      r = result[0]
      print(result)
      print(r)
      cur.execute('SELECT * FROM orders WHERE user_id=?', (r[0],))
      orderinf = cur.fetchall()
      print(orderinf)
      resprod = []
      respr = []
      if not orderinf:
         return render_template('register.html', data={'photo': r[7], 'name': r[3], 'surname': r[4], 'city': r[6], 'tel': r[5], 'email': r[1], 'product': 'Нет заказов'})
      else:
         for i in orderinf:
            print(i)
            idp = i[2].split(',')
            del idp[-1]
            print(idp)
            for i in idp:
               cur.execute('SELECT * FROM products WHERE id=?', (i,))
               resp = cur.fetchone()
               respr.append(resp)
            resprod.append(respr)
         print(resprod)
         l = len(orderinf)
         return render_template('register_with_order.html', l=l, prod=resprod, orderinf=orderinf, data={'photo': r[7], 'name': r[3], 'surname': r[4], 'city': r[6], 'tel': r[5], 'email': r[1]})
   else:
      return render_template('reg.html')

@app.route('/del_ses')
def del_ses():
   session.clear()
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products")
   result = cur.fetchall()
   print(result)
   return render_template('index.html', data={ 'result': result, 'st': 'False'})
                          
@app.route('/reg_ses')
def reg_ses():
   if 'username' in session:
      conn = sqlite3.connect('mts.db')
      cur = conn.cursor()
      cur.execute('SELECT * FROM users WHERE username=?', (session['username'],))
      result = cur.fetchall()
      r = result[0]
      #print(result)
      #print(r)
      cur.execute('SELECT * FROM orders WHERE user_id=?', (r[0],))
      orderinf = cur.fetchall()
      print(orderinf)
      resprod = []
      respr = []
      if not orderinf:
         return render_template('register.html', data={'photo': r[7], 'name': r[3], 'surname': r[4], 'city': r[6], 'tel': r[5], 'email': r[1], 'product': 'Нет заказов'})
      else:
         for i in orderinf:
            print(i)
            idp = i[2].split(',')
            del idp[-1]
            print(idp)
            for v in idp:
               cur.execute('SELECT * FROM products WHERE id=?', (v,))
               resp = cur.fetchone()
               respr.append(resp)
            resprod.append(respr)
            respr = []
         print(resprod)
         l = len(orderinf)
         return render_template('register_with_order.html', l=l, prod=resprod, orderinf=orderinf, data={'photo': r[7], 'name': r[3], 'surname': r[4], 'city': r[6], 'tel': r[5], 'email': r[1]})
   else:
         return render_template('stop.html')
   
@app.route('/reg', methods=['POST']) #
def register():
   username = request.form['username']
   password = request.form['password']
   print(username)
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   
   cur.execute('SELECT password FROM users WHERE username=?', (username,))
   result = cur.fetchone() 

   #print(result)reg.ht
 
   if result and check_password_hash(result[0], password):
      session.permanent = True  
      session['username'] = username
      cur.execute('SELECT * FROM users WHERE username=?', (session['username'],))
      result = cur.fetchall()
      r = result[0]
      #print(result)
      #print(r)
      cur.execute('SELECT * FROM orders WHERE user_id=?', (r[0],))
      orderinf = cur.fetchall()
      print(orderinf)
      resprod = []
      respr = []
      if not orderinf:
         return render_template('register.html', data={'photo': r[7], 'name': r[3], 'surname': r[4], 'city': r[6], 'tel': r[5], 'email': r[1], 'product': 'Нет заказов'})
      else:
         for i in orderinf:
            print(i)
            idp = i[2].split(',')
            del idp[-1]
            print(idp)
            for v in idp:
               cur.execute('SELECT * FROM products WHERE id=?', (v,))
               resp = cur.fetchone()
               respr.append(resp)
            resprod.append(respr)
            respr = []
         print(resprod)
         l = len(orderinf)
         return render_template('register_with_order.html', l=l, prod=resprod, orderinf=orderinf, data={'photo': r[7], 'name': r[3], 'surname': r[4], 'city': r[6], 'tel': r[5], 'email': r[1]})
   else:
      return render_template('wrongreg.html')

@app.route('/rr') #Зарегистрироваться
def rr(): 
    return render_template('regg.html')

@app.route('/regg', methods=['POST'])
def regg():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('''CREATE TABLE IF NOT EXISTS users(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   username TEXT,
   password TEXT,
   name TEXT,
   surname TEXT,
   tel INTEGER,
   city TEXT,
   photo TEXT
   );''')

   username = request.form['username']
   password = request.form['password']
   name = request.form['name']
   surname = request.form['surname']
   tel = request.form['tel']
   city = request.form['city']
   photo = request.form['photo']
   
   hashed_password = generate_password_hash(password)

   conn.execute('INSERT INTO users (username, password, name, surname, tel, city, photo) VALUES (?, ?, ?, ?, ?, ?, ?)',(username, hashed_password, name, surname, tel, city, photo))
   conn.commit()
   conn.close()

   return render_template('regdone.html')


@app.route('/iphone_15_pro')
def iphone_15_pro():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products WHERE name=?', ('Смартфон Apple iPhone 15 Pro',))
   result = cur.fetchall()
   print(result)
   r = result[0]
   conn.commit()
   return render_template('product.html', data={'name': r[2], 'photo': r[1], 'prise': r[3], 'description': r[6]})

@app.route('/iphone_13')
def iphone_13():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products WHERE name=?', ('Смартфон Apple iPhone 13',))
   result = cur.fetchall()
   print(result)
   r = result[0]
   conn.commit()
   return render_template('product.html', data={'name': r[2], 'photo': r[1], 'prise': r[3], 'description': r[6]})


@app.route('/tovar/<int:tovar_id>')
def card_tovar(tovar_id):
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products WHERE id=?', (tovar_id,))
   result = cur.fetchall()
   print(result)
   r = result[0]
   conn.commit()
   return render_template('product.html', data={'name': r[2], 'photo': r[1], 'prise': r[3], 'description': r[6]})


@app.route('/samsung_galaxy_s24')
def samsung_galaxy_s24():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products WHERE name=?', ('Смартфон Samsung Galaxy S24',))
   result = cur.fetchall()
   print(result)
   r = result[0]
   conn.commit()
   return render_template('product.html', data={'name': r[2], 'photo': r[1], 'prise': r[3], 'description': r[6]})

@app.route('/samsung_galaxy_s24_ultra')
def samsung_galaxy_s24_ultra():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products WHERE name=?', ('Смартфон Samsung Galaxy S24 Ultra',))
   result = cur.fetchall()
   print(result)
   r = result[0]
   conn.commit()
   return render_template('product.html', data={'name': r[2], 'photo': r[1], 'prise': r[3], 'description': r[6]})

@app.route('/xiaomi_redmi_12')
def xiaomi_redmi_12():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products WHERE name=?', ('Смартфон Xiaomi Redmi 12',))
   result = cur.fetchall()
   print(result)
   r = result[0]
   conn.commit()
   return render_template('product.html', data={'name': r[2], 'photo': r[1], 'prise': r[3], 'description': r[6]})

@app.route('/xiaomi_redmi_note_13')
def xiaomi_redmi_note_13():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products WHERE name=?', ('Смартфон Xiaomi Redmi Note 13',))
   result = cur.fetchall()
   print(result)
   r = result[0]
   conn.commit()
   return render_template('product.html', data={'name': r[2], 'photo': r[1], 'prise': r[3], 'description': r[6]})

@app.route('/honor_200_lite')
def honor_200_lite():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products WHERE name=?', ('Смартфон HONOR 200 Lite',))
   result = cur.fetchall()
   print(result)
   r = result[0]
   conn.commit()
   return render_template('product.html', data={'name': r[2], 'photo': r[1], 'prise': r[3], 'description': r[6]})

@app.route('/honor_90_lite')
def honor_90_lite():
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute('SELECT * FROM products WHERE name=?', ('Смартфон HONOR 90 Lite',))
   result = cur.fetchall()
   print(result)
   r = result[0]
   conn.commit()
   return render_template('product.html', data={'name': r[2], 'photo': r[1], 'prise': r[3], 'description': r[6]})

@app.route('/apple')
def apple(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE brand=?", ('apple',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'apple'})

@app.route('/samsung')
def samsung(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE brand=?", ('samsung',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'samsung'})

@app.route('/xiaomi')
def xiaomi(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE brand=?", ('xiaomi',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'xiaomi'})

@app.route('/honor')
def honor(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE brand=?", ('honor',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'honor'})

@app.route('/phones')
def phones(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE gadget=?", ('phone',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'phones'})

@app.route('/smart_whatches')
def smart_whatches(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE gadget=?", ('watch',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'watch'})

@app.route('/earphones')
def earphones(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE gadget=?", ('earphone',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'earphones'})

@app.route('/laptops')
def laptops(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE gadget=?", ('laptop',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'laptops'})

@app.route('/comp_tex')
def comp_tex(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE gadget=?", ('comp_tex',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'comp_tex'})

@app.route('/TV')
def TV(): 
   conn = sqlite3.connect('mts.db')
   cur = conn.cursor()
   cur.execute("SELECT * FROM products WHERE gadget=?", ('TV',))
   result = cur.fetchall()
   print(result)
   return render_template('search.html', data={ 'result': result, 'requestt': 'TV'})


#if __name__ == '__main__':
#    app.run(debug=True)

if __name__ == "__main__":
   #app.run(host="0.0.0.0", port=5000)
   app.run(host='0.0.0.0', port=5000, debug=True)

'''
apt update && apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx certbot python3-certbot-nginx -y
'''
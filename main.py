from tokenize import String
from sqlalchemy import Column
from flask import request, g
from werkzeug.urls import url_parse
import pymsgbox
from flask import Flask, render_template, request ,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask_mail import Mail                             
from pymsgbox import *
from werkzeug.security import generate_password_hash,check_password_hash
import json
import pymysql,json
import re
pymysql.install_as_MySQLdb()
# from flask_cors import CORS



# my db connection
local_server=True # setting localserver
app = Flask(__name__)
app.secret_key="swathi"

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/mallquest'
db=SQLAlchemy(app)
# CORS(app, supports_credentials=True, resources={r"/": {"origins": ""}})
# app.config['CORS_HEADERS'] = 'Content-Type'

#this is for getting unique employee access
login_manager=LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(str(user_id))



#database name = cashandcarry

#loading the db to main.py file
#app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:passwllord@localhost/databse_table_name'


class Employee(UserMixin, db.Model):
    __tablename__ = 'employee'
    E_id=db.Column(db.String(10), primary_key=True)
    Ename=db.Column(db.String(20), nullable=False)
    Eaddress=db.Column(db.String(50), nullable=False)
    Ephone=db.Column(db.Integer, nullable=False)
    Esalary=db.Column(db.Integer, nullable=False)
    Epass=db.Column(db.String(1000), nullable=False)
    def get_id(self):
        return (self.E_id)

class Customer(db.Model):
    __tablename__ = 'customer'
    C_id=db.Column(db.Integer,primary_key=True)
    Cname=db.Column(db.String(20), nullable=False)
    Caddress=db.Column(db.String(20), nullable=False)
    Cphone=db.Column(db.Integer, nullable=False)

class Orders(db.Model):
    __tablename__ = 'orders'
    Ord_no=db.Column(db.Integer,primary_key=True)
    C_id=db.Column(db.Integer, nullable=False)
    Stname=db.Column(db.String(20), nullable=False)
    Stamount=db.Column(db.Integer, nullable=False)
    Sh_id=db.Column(db.Integer, nullable=False)

class Shop(db.Model):
    __tablename__ = 'shop'
    Sh_id=db.Column(db.Integer,primary_key=True, nullable=False)
    Shname=db.Column(db.String(20), nullable=False)
    Shphone=db.Column(db.Integer, nullable=False)
    Shaddress=db.Column(db.String(20), nullable=False)
    # E_id = db.Column(db.String(10),db.ForeignKey('employee.E_id'), nullable=False)
    C_id = db.Column(db.Integer,db.ForeignKey('customer.C_id'), nullable=False)
    
class Stock(db.Model):
    __tablename__ = 'stock'
    St_id=db.Column(db.Integer,primary_key=True, nullable=False)
    Stname=db.Column(db.String(20), nullable=False)
    Stamount=db.Column(db.Integer, nullable=False)
    Stbarcode=db.Column(db.Integer, nullable=False)
    Sh_id = db.Column(db.Integer,db.ForeignKey('shop.Sh_id'), nullable=False)
    M_id = db.Column(db.Integer,db.ForeignKey('manufacturer.M_id'), nullable=False)

class Manufacturer(db.Model):
    __tablename__ = 'manufacturer'
    M_id = db.Column(db.Integer, primary_key=True, nullable=False)
    Mname = db.Column(db.String(20), nullable=False)
    Maddress = db.Column(db.String(20), nullable=False)
    Memail = db.Column(db.String(50), nullable=False)
    
class Branch(db.Model):
    __tablename__ = 'branch'
    M_id = db.Column(db.Integer, db.ForeignKey('manufacturer.M_id'),primary_key=True,nullable=False)
    Bname= db.Column(db.String(20), nullable=False)
    Baddress = db.Column(db.String(20), nullable=False)
    Bphone= db.Column(db.Integer, nullable=False)

visits = db.Table('visits',
db.Column('Sh_id',db.Integer, db.ForeignKey('shop.Sh_id'), nullable=False),
db.Column('C_id',db.Integer, db.ForeignKey('customer.C_id'), nullable=False)
)

shproducts = db.Table('shproducts',
db.Column('Sh_id',db.Integer, db.ForeignKey('shop.Sh_id'), primary_key=True, nullable=False),
db.Column('Shproducts',db.String(20), nullable=False)
)

producedby = db.Table('producedby',
db.Column('St_id',db.Integer, db.ForeignKey('stock.St_id'), nullable=False),
db.Column('M_id',db.Integer, db.ForeignKey('manufacturer.M_id'),  nullable=False)
)

class Trig(db.Model):
    __tablename__ = 'trig'
    Triggerid=db.Column(db.Integer,primary_key=True)
    St_id=db.Column(db.Integer)
    Stname=db.Column(db.String(20))
    Stamount=db.Column(db.String(40))
    Stbarcode=db.Column(db.Integer)
    Action=db.Column(db.String(30))
    Time=db.Column(db.String(50))

@app.route('/orders', methods=['POST','GET'])
def orders():
    query=db.engine.execute("SELECT * FROM `orders` ORDER BY `orders`.`Ord_no` DESC")
    return render_template('orders.html', query=query)
    

@app.route('/',methods=['POST','GET'])
def login():
    if request.method=="POST":
        E_id=request.form.get('E_id')  
        print(E_id)
        Epass=request.form.get('Epass')
        print(Epass)
        user=Employee.query.filter_by(E_id=E_id).first()
        print(user)

        # if user and Epass:
        if E_id == "admin"  and check_password_hash(user.Epass,Epass) :
            
            login_user(user)
            return redirect(url_for('home'))
        elif E_id[:2] == 'GS' and check_password_hash(user.Epass,Epass) : 
            login_user(user)
            return redirect(url_for('grocery1'))
        elif E_id[:2] == 'SS' and check_password_hash(user.Epass,Epass) :
            login_user(user)
            return redirect(url_for('stationary1'))
        elif E_id[:2] == 'MS' and check_password_hash(user.Epass,Epass) :
            login_user(user)
            return redirect(url_for('med1'))
        elif E_id[:2] == 'TS' and check_password_hash(user.Epass,Epass) :
            login_user(user)
            return redirect(url_for('toys1'))
        elif E_id[:2] == 'CS'and check_password_hash(user.Epass,Epass)  :
            login_user(user)
            return redirect(url_for('clothing1'))
        elif E_id[:2] == 'BS' and check_password_hash(user.Epass,Epass) :
            login_user(user)
            return redirect(url_for('bakery1'))
        else:
            #print('Invalid credentials')
            alert(text='Invalid credentials', title='Message Alert', button='OK')
            return render_template('login.html')    
    return render_template('login.html')

@app.route('/register',methods=['POST','GET'])
def register(): 
    # to get data from the form
    if request.method=="POST":

        E_id=request.form.get('E_id')  
        Ename=request.form.get('Ename')
        Eaddress=request.form.get('Eaddress')
        Epass=request.form.get('Epass')
        print(Epass)
  #     print(EmployeeId,EmployeeName, Address,Password)
        user=Employee.query.filter_by(E_id=E_id).first()
        if user:
            alert(text='User ID Already Exists!', title='Message Alert', button='OK')
            return redirect(url_for('login'))
        encpassword=generate_password_hash(Epass)   
        new_user=db.engine.execute(f"INSERT INTO `employee`(`E_id`, `Ename`, `Eaddress`, `Epass`) VALUES ('{E_id}','{Ename}','{Eaddress}','{encpassword}')")
        return redirect(url_for('login')) # return redirect(url_for('login'))
        
    return render_template('register.html')


@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/stationary',methods=['POST','GET'])
@login_required
def stationary():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=1")

    return render_template('stationary.html', query=query)

@app.route('/med',methods=['POST','GET'])
@login_required
def med():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=2")
    return render_template('med.html', query=query)

@app.route('/toys',methods=['POST','GET'])
@login_required
def toys():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=3")
    return render_template('toys.html', query=query)

@app.route('/bakery',methods=['POST','GET'])
@login_required
def bakery():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=4")
    return render_template('bakery.html', query=query)


@app.route('/clothing',methods=['POST','GET'])
@login_required
def clothing():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=5")
    return render_template('clothing.html', query=query)

@app.route('/grocery',methods=['POST','GET'])
@login_required
def grocery():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=6")
    return render_template('grocery.html', query=query)

@app.route('/employee',methods=['POST','GET'])
@login_required
def employee():
    if request.method=='POST':
        E_id=request.form.get('E_id')
        Ename=request.form.get('Ename')
        Eaddress=request.form.get('Eaddress')
        Ephone=request.form.get('Ephone')
        Esalary=request.form.get('Esalary')
        Epass=request.form.get('Epass')
        new_add=db.engine.execute(f"INSERT INTO employee` (`E_id, `Ename`, `Eaddress`,  `Ephone`,`Esalary`,`Epass`) VALUES ('{E_id}','{Ename}','{Eaddress}','{Ephone}','{Esalary}','{Epass}')")
    query=db.engine.execute("SELECT * FROM `employee`")
    return render_template('employee.html', query=query)

@app.route('/customer',methods=['POST','GET'])
@login_required
def customer():
    if request.method=='POST':
        C_id=request.form.get('C_id')
        Cname=request.form.get('Cname')
        Caddress=request.form.get('Caddress')
        Cphone=request.form.get('Cphone')
        new_add=db.engine.execute(f"INSERT INTO `customer` (`C_id, `Cname`, `Caddress`,  `Cphone`) VALUES ('{C_id}','{Cname}','{Caddress}','{Cphone}')")
    query=db.engine.execute("SELECT * FROM `customer`")
    return render_template('customer.html', query=query)

@app.route('/manufacturer',methods=['POST','GET'])
@login_required
def manufacturer():
    if request.method=='POST':
        M_id=request.form.get('M_id')
        Mname=request.form.get('Mname')
        Maddress=request.form.get('Maddress')
        Memail=request.form.get('Memail')
        new_add=db.engine.execute(f"INSERT INTO `manufacturer` (`M_id, `Mname`, `Maddress`,  `Memail`) VALUES ('{M_id}','{Mname}','{Maddress}','{Memail}')")
    query=db.engine.execute("SELECT * FROM `manufacturer`")
    return render_template('manufacturer.html', query=query)

@app.route('/shop',methods=['POST','GET'])
@login_required
def shop():
    if request.method=='POST':
        Sh_id=request.form.get('Sh_id')
        Shname=request.form.get('Shname')
        Shphone=request.form.get('Shphone')
        Shaddress=request.form.get('Shaddress')
        E_id=request.form.get('E_id')
        C_id=request.form.get('C_id')
        new_add=db.engine.execute(f"INSERT INTO `shop` (`Sh_id, `Shname`, `Shphone`,  `Cphone`, `E_id`, `C_id`) VALUES ('{Sh_id}','{Shname}','{Shphone}','{Shaddress}','{E_id}','{C_id}')")
    query=db.engine.execute("SELECT * FROM `shop`")
    return render_template('shop.html', query=query)

@app.route('/stock',methods=['POST','GET'])
@login_required
def stock():
    if request.method=='POST':
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        M_id=request.form.get('M_id')
        new_add=db.engine.execute(f"INSERT INTO `stock` (`St_id, `Stname`, `Stamount`, `Stbarcode` `Cphone`,`Sh_id`, `M_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}','{Sh_id}','{M_id}')")
    query=db.engine.execute("SELECT * FROM `stock`")
    return render_template('stock.html', query=query)

@app.route('/branch',methods=['POST','GET'])
@login_required
def branch():
    if request.method=='POST':
        M_id=request.form.get('M_id')
        Bname=request.form.get('Bname')
        Baddress=request.form.get('Baddress')
        Bphone=request.form.get('Bphone')
        new_add=db.engine.execute(f"INSERT INTO `branch` (`M_id, `Bname`, `Baddress`, `Bphone` `Cphone`) VALUES ('{M_id}','{Bname}','{Baddress}','{Bphone})")
    query=db.engine.execute("SELECT * FROM `branch`")
    return render_template('branch.html', query=query)

# edit
@app.route("/edit/<string:St_id>",methods=['POST','GET'])
def edit(St_id):
    posts=Stock.query.filter_by(St_id=St_id).first()
    if request.method=="POST":
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        # CustomerId=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        db.engine.execute(f"UPDATE `stock` SET `St_id` = '{St_id}', `Stname` = '{Stname}' , `Stamount` = '{Stamount}', `Stbarcode` = '{Stbarcode}', `Sh_id` = '{Sh_id}' WHERE `stock`.`St_id` = {St_id}")
        # alert(text='You\'ve Success)
        # return redirect('/edit/{Stname}')
        # return redirect(request.referrer)
        alert(text='Order Succesfully Updated!', title='Message Alert', button='OK')
    return render_template('edit.html',posts=posts)
 #delete

@app.route("/delete/<string:St_id>",methods=['POST','GET'])
def delete(St_id):
    db.engine.execute(f"DELETE FROM `stock` WHERE `stock`.`St_id`={St_id}")
    return redirect(request.referrer)
# Trigger page required!!

@app.route('/triggers')
def triggers():
    query=db.engine.execute(f"SELECT * FROM `trig` ORDER BY `trig`.`Time` DESC") 
    return render_template('triggers.html',query=query)


@app.route('/addcustomer',methods=['POST','GET'])
def addcustomer():
    if request.method=='POST':
        # C_id=request.form.get('C_id')
        Cname=request.form.get('Cname')
        Caddress=request.form.get('Caddress')
        Cphone=request.form.get('Cphone')
        new_add=db.engine.execute(f"INSERT INTO `customer` (`Cname`, `Caddress`,  `Cphone`) VALUES ('{Cname}','{Caddress}','{Cphone}')")
        # url = request.referrer
        # if url:
        #     session["url"] = url
        # return redirect(session.get("url"))
        # return redirect(request.referrer)
    return render_template('/addcustomer.html')

    
   


# this is for the employee, so when you apply regex it should redirevt them to the following pages. for eg: if the employee has id as GS001 then,
#it should take him to the grocery1.html

@app.route('/stationary1',methods=['POST','GET'])
@login_required
def stationary1():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
        if new_order:
            alert(text='order placed!', title='Message Alert', button='OK')
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=1")

    return render_template('stationary1.html', query=query)

@app.route('/med1',methods=['POST','GET'])
@login_required
def med1():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
        if new_order:
            alert(text='order placed!', title='Message Alert', button='OK')
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=2")
    return render_template('med1.html', query=query)

@app.route('/toys1',methods=['POST','GET'])
@login_required
def toys1():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
        if new_order:
            alert(text='order placed!', title='Message Alert', button='OK')
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=3")
    return render_template('toys1.html', query=query)

@app.route('/bakery1',methods=['POST','GET'])
@login_required
def bakery1():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
        if new_order:
            alert(text='order placed!', title='Message Alert', button='OK')
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=4")
    return render_template('bakery1.html', query=query)


@app.route('/clothing1',methods=['POST','GET'])
@login_required
def clothing1():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
        if new_order:
            alert(text='order placed!', title='Message Alert', button='OK')
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=5")
    return render_template('clothing1.html', query=query)

@app.route('/grocery1',methods=['POST','GET'])
@login_required
def grocery1():
    if request.method=='POST':
        # Stocks
        St_id=request.form.get('St_id')
        Stname=request.form.get('Stname')
        Stamount=request.form.get('Stamount')
        Stbarcode=request.form.get('Stbarcode')
        Sh_id=request.form.get('Sh_id')
        C_id=request.form.get('C_id')
        # M_id=request.form.get('M_id')
        new_order=db.engine.execute(f"INSERT INTO `orders` (`St_id`, `Stname`, `Stamount`, `Stbarcode`, `Sh_id`, `C_id`) VALUES ('{St_id}','{Stname}','{Stamount}','{Stbarcode}' ,'{Sh_id}','{C_id}')")
        if new_order:
            alert(text='order placed!', title='Message Alert', button='OK')
    query=db.engine.execute("SELECT * FROM `stock` WHERE Sh_id=6")
    return render_template('grocery1.html', query=query)
app.run(debug=True)

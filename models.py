from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_migrate import Migrate
import os

from sqlalchemy import ForeignKey
app = Flask(__name__)
base_dir = os.path.dirname(__file__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'CRM.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Customer(db.Model):
    __tablename__ = 'customers'
    customer_id = db.Column(db.String(10), primary_key=True)
    customer_name = db.Column(db.String(20), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)

    def __init__(self,customer_id,customer_name,age,gender):
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.age = age
        self.gender = gender

    purchase = db.relationship('Purchase', backref='customer', lazy=True,cascade='all, delete')

    def __repr__(self):
        return f"<Customer(customer_id={self.customer_id}, customer_name={self.customer_name}, age={self.age}, gender={self.gender})>"


class Item(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.String(10), primary_key=True)
    item_name = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    def __init__(self,item_id,item_name,price):
        self.item_id = item_id
        self.item_name = item_name
        self.price = price

    def __repr__(self):
        return f"<Item(item_id={self.item_id}, item_name={self.item_name}, price={self.price})>"
    
    purchase_detail = db.relationship('PurchaseDetail', backref='item', lazy=True,cascade='all, delete')

    def to_csv_row(self):
        return f"{self.item_id},{self.item_name},{self.price}"
    
    
class Purchase(db.Model):
    __tablename__ = 'purchases'
    
    purchase_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.String(10), db.ForeignKey('customers.customer_id'), nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)

    def __init__(self,customer_id,purchase_date):
        self.customer_id = customer_id
        self.purchase_date = purchase_date

    def __repr__(self):
        return f"<Purchase(purchase_id={self.purchase_id}, customer_id={self.customer_id}, purchase_date={self.purchase_date})>"

    purchase_detail = db.relationship('PurchaseDetail', backref='purchase', lazy=True,cascade='all, delete')

class PurchaseDetail(db.Model):
    __tablename__ = 'purchase_details'
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.purchase_id'), nullable=False, primary_key=True)
    item_id = db.Column(db.String(10), db.ForeignKey('items.item_id'), nullable=False, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    def __init__(self,purchase_id,item_id,quantity):
        self.purchase_id = purchase_id
        self.item_id = item_id
        self.quantity = quantity

    def __repr__(self):
        return f"<PurchaseDetail(purchase_id={self.purchase_id}, item_id={self.item_id}, quantity={self.quantity})>"


with app.app_context():
    db.create_all()
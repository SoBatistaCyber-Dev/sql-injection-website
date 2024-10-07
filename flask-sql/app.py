# Imports

from flask import Flask, render_template, redirect, request
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# My app
app = Flask(__name__)

# MySQL Required Configuration
app.config["MYSQL_USER"] = "user_flask"
app.config["MYSQL_PASSWORD"] = "password123"
app.config["MYSQL_DB"] = "flask_sql_vulnerable"
app.config['SQLALCHEMY_DATABASE_URI']='mysql://user_flask:password123@localhost/flask_sql_vulnerable'

db = SQLAlchemy(app)
mysql = MySQL(app)
query_list = []

# Models - START --------------------------------------------------------------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Integer, unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"Product ({self.id}) - {self.name}"

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"Customer ({self.id}) - {self.name}"

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id', ondelete="CASCADE"))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id', ondelete="CASCADE"))
    quantity = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return f"Order ({self.id}) - {self.product_id}"

# Models - END --------------------------------------------------------------

# Routes
@app.route("/", methods=["POST", "GET"])
def index():
    # Add a product
    if request.method == "POST":
        product_name = request.form['name']
        product_price = request.form['price']
        new_product = Product(name=product_name, price=product_price)
        try:
            db.session.add(new_product)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            return f"ERROR: {e}"
    # Get all current products
    else:
        cur = mysql.connection.cursor()
        query = """SELECT id, name, price FROM flask_sql_vulnerable.product"""
        cur.execute(query)
        products = cur.fetchall()
        print("1st query: ", query)
        return render_template("index.html", products=products)

# Routes
@app.route("/search", methods=["POST"])
def search():
    # Search a product
    search_name = request.form['search']
    print(search_name)
    cur = mysql.connection.cursor()
    query = "SELECT id, name, price FROM flask_sql_vulnerable.product WHERE name = '" + search_name + "'"
    print("Search query: ", query)
    cur.execute(query)
    search_results = cur.fetchall()
    print(search_results)
    global query_list
    query_list += [[f"{datetime.now():%Y-%m-%d@%H-%M-%S}"] + [query]]
    print(query_list)
    return render_template("index.html", search_results=search_results, query_list=query_list)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
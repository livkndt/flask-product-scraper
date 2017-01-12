# imports
import os
import sqlite3
import json

# Flask framework
from flask import Flask, g, render_template, make_response

# create application inst
app = Flask(__name__)

# load config file
app.config.from_pyfile('config.cfg', silent=True)

# front end of the app
@app.route('/')
def show_home():
    db = get_db()
    cur = db.execute('select * from category')
    entries = cur.fetchall()
    return render_template('index.html', entries=entries)

# Endpoint to retrieve JSON of scraped products
@app.route('/product', methods=['GET'])
def get_products():
    db = get_db()
    query = db.execute('select * from product')
    products = query.fetchall()
    return nice_json(products, 'product')

# Endpoint to retrieve JSON of scraped products by category
@app.route('/product/category/<int:catId>', methods=['GET'])
def get_products_by_cat(catId):
    db = get_db()
    cur = db.execute('select * from product where catId=? or catId in '
        + '(select catId from category where parentCatId=?)', (str(catId), str(catId)))
    products = cur.fetchall()
    return nice_json(products, 'product')

# Endpoint to retrieve JSON of scraped categories
@app.route('/category', methods=['GET'])
def get_category():
    db = get_db()
    cur = db.execute('select * from category')
    categories = cur.fetchall()
    return nice_json(categories, 'category')

# format products/categories nicely in JSON
def nice_json(entries, entity):
    return_data = []
    for item in entries:
        if entity == 'product':
            elem = {
                "prodId": item[0],
                "prodCode": item[1],
                "prodUrl": item[2],
                "prodImg": item[3],
                "prodName": item[4],
                "prodPrice": item[5],
                "catId": item[6]
            }
        else:
            elem = {
                "parentCatId": item[1],
                "catId": item[0],
                "catTitle": item[2],
                "catUrl": item[3]
            }
        return_data.append(elem)
    response = make_response(json.dumps(return_data, sort_keys = True, indent=4))
    response.headers['Content-type'] = "application/json"
    return response

# connect to the sqlite db
def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# open new db connection if not already
def get_db():
    # g is a general purpose variable associated with the current application context
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# initialise the db
def init_db():
    db = get_db()
    with app.open_resource('database/schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())

    # load the categories from JSON file
    try:
        categories = json.load(open('database/category.json'))
    except IOError:
        print "Error: There is no such file: database/category.json. Make sure you run the scraper first."
        return

    # load categories into DB
    columns = ['catId', 'parentCatId', 'catTitle', 'catUrl']
    query = "insert into category (catId, parentCatId, catTitle, catUrl) values (?,?,?,?)"
    for item in categories:
        inserts = tuple(item[c] for c in columns)
        db.execute(query, inserts)

    # load the categories from JSON file
    try:
        products = json.load(open('database/product.json'))
    except IOError:
        print "Error: There is no such file: database/product.json. Make sure you run the scraper first."
        return

    # load the products from JSON file
    columns = ['prodName', 'catId', 'prodPrice', 'prodImg', 'prodUrl', 'prodCode']
    query = "insert into product (prodName, catId, prodPrice, prodImg, prodUrl, prodCode) values (?,?,?,?,?,?)"
    for item in products:
        inserts = tuple(item[c] for c in columns)
        db.execute(query, inserts)

    # commit to db
    db.commit()
    print('Initialized the database.')

@app.cli.command()
def initdb():
    """Initializes the database."""
    init_db()

# close db at end of request
@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

if __name__ == '__main__':
    app.run()

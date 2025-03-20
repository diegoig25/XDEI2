import re
import math
from datetime import datetime

from flask import Flask, render_template

from ngsiv2 import list_entities, read_entity

app = Flask(__name__)

# Creamos esta función para obtener los tiles de OpenStreetMap (en la función store se calculan los valores 
# que luego se emplearán en "store.html")

def latlon_to_tile(lat_deg, lon_deg, zoom):
    
    n = 1 << zoom 
    lat_rad = math.radians(lat_deg)
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


# Ruta por defecto (HOME)
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json") # lleva al JSON asociado

@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/products/")
def products():
    (status, products) = list_entities(type='Product', options='keyValues')
    if status == 200:
        return render_template("products.html", products=products)

@app.route("/products/<id>")
def product(id):
    (status, product) = read_entity(id)
    if status == 200:
        (status, inventory_items) = list_entities(type = 'InventoryItem', options='keyValues',query = f'refProduct=={id}')

        if status == 200:
            return render_template('product.html', product = product, inventory_items = inventory_items)
        
@app.route("/stores/")
def stores():
    (status, stores) = list_entities(type='Store', options='keyValues')
    if status == 200:
        return render_template("stores.html", stores = stores)
    
@app.route("/stores/<id>")
def store(id):
    (status, store) = read_entity(id)
    if status == 200:
        (status, inventory_items) = list_entities(type = 'InventoryItem', options='keyValues',query = f'refStore=={id}')

        if status == 200:
            # Obtenemos los valores correspondientes para el cálculo de las tiles
            lon_deg = store["location"]["value"]["coordinates"][0]
            lat_deg = store["location"]["value"]["coordinates"][1]
            zoom = 15
            
            # Cálculo de xtile y ytile
            xtile, ytile = latlon_to_tile(lat_deg, lon_deg, zoom)

            return render_template('store.html', store=store, inventory_items=inventory_items, xtile=xtile, ytile=ytile, zoom=zoom)

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name = None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )
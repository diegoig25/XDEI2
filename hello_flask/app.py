import re
import math

from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

from ngsiv2 import *

app = Flask(__name__)

# Creamos esta función para obtener los tiles de OpenStreetMap (en la función store se calculan los valores 
# que luego se emplearán en "store.html")

def latlon_to_tile(lat_deg, lon_deg, zoom):
    
    n = 1 << zoom 
    lat_rad = math.radians(lat_deg)
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


# Ruta por defecto (al Home)
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

# # Definimos la ruta a Employee
# @app.route("/employees/")
# def employees():
#     (status, employees) = list_entities(type='Employee', options='keyValues')
#     if status == 200:
#         return render_template("employees.html", employees=employees)

# @app.route("/employees/<id>")
# def employee(id):
#     (status, employee) = read_entity(id)
#     # if status == 200:
#     #     (status, inventory_items) = list_entities(type = 'InventoryItem', options='keyValues',query = f'refProduct=={id}')

#     if status == 200:
#         return render_template('employee.html', employee = employee) #, inventory_items = inventory_items)        

# @app.route("/hello/")
# @app.route("/hello/<name>")
# def hello_there(name = None):
#     return render_template(
#         "hello_there.html",
#         name=name,
#         date=datetime.now()
#     )
    


# Añadimos la creación y modificación de Product, Store (queda employee y modificaciones)

# Creación de un Product
@app.route("/products/create", methods=['GET', 'POST']) 
def create_product(): 
    if request.method == 'POST': 
        product = {"id": request.form["id"],
                   "type": "Product", 
                   "name": {"type": "Text", "value": request.form["name"]}, 
                   "size": {"type": "Text", "value": request.form["size"]},
                   "price": {"type": "Integer", "value": int(request.form["price"])},
                   "image": {"type": "Text", "value": request.form["image"]},
                   "color": {"type": "Text", "value": request.form["color"]}}
        status = create_entity(product) 
        if status == 201:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('display_products')) 
    else:
        return render_template('create_product.html')


# Creación de un Store (duda en el tipo de location y address, también en el html)
# para trabajar con location, solicitamos al cliente la latitud y longitud, de forma 
# que creamos automáticamente la lista de coordenadas nosotros, sin necesidad de que tenga que ponerlo él
@app.route("/stores/create", methods=['GET', 'POST']) 
def create_store(): 
    if request.method == 'POST': 
        store = {"id": request.form["id"],
                "type": "Store",
                "name": {"type": "Text", "value": request.form["image"]},
                "address": {"type": "PostalAddress", "value": request.form["address"]},
                "location": {"type": "geo:json", "value": {"type": "Point", "coordinates": [float(request.form["longitude"]), float(request.form["latitude"])]}}, 
                "image": {"type": "Text", "value": request.form["image"]},
                "url": {"type": "Text", "value": request.form["url"]},
                "telephone": {"type": "Text", "value": request.form["telephone"]},
                "countryCode": {"type": "Text", "value": request.form["country_code"]},
                "capacity": {"type": "Integer", "value": int(request.form["capacity"])},
                "description": {"type": "Text", "value": request.form["description"]},
                "temperature": {"type": "Integer", "value": int(request.form["temperature"])},
                "relativeHumidity": {"type": "Integer", "value": int(request.form["relativeHumidity"])}}
        status = create_entity(store) 
        if status == 201:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('display_products')) 
    else:
        return render_template('create_store.html')

# Creación de un Employee 
@app.route("/employees/create", methods=['GET', 'POST']) 
def create_employee(): 
    if request.method == 'POST': 
        employee = {"id": request.form["id"],
                "type": "Employee",
                "name": {"type": "Text", "value": request.form["image"]},
                "email": {"type": "Email", "value": request.form["email"]},
                "dateOfContract": {"type": "Date", "value": request.form["dateOfContract"]}, 
                "category": {"type": "Text", "value": request.form["category"]},
                "salary": {"type": "Integer", "value": int(request.form["salary"])},
                "skills": {"type": "Text", "value": request.form["skills"]},
                "username": {"type": "Text", "value": request.form["username"]},
                "password": {"type": "Password", "value": request.form["capacity"]}}
        status = create_entity(employee) 
        if status == 201:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('display_products')) 
    else:
        return render_template('create_employee.html') 
    

# Creación de una Shelf dentro de una Store (para ello, podemos entrar en alguno de los stores
# de la página web e introducir a continuación /shelves/create)
@app.route("/stores/<store_id>/shelves/create", methods=['GET', 'POST'])
def create_shelf(store_id):
    if request.method == 'POST':
        shelf = {"id": request.form["id"],
                "type": "Shelf",
                "name": {"type": "Text", "value": request.form["image"]},
                "location": {"type": "geo:json", "value": {"type": "Point", "coordinates": [float(request.form["longitude"]), float(request.form["latitude"])]}},
                "maxCapacity": {"type": "Integer", "value": request.form["maxCapacity"]}, 
                "refStore": {"type": "Relationship", "value": f"urn:ngsi-ld:Store:{store_id}"}}  # Relación con el Store}
        status = create_entity(shelf) 
        if status == 201:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('store', id=store_id)) 
    else:
        return render_template('create_shelf.html', store_id=store_id) 
import re
import math
import base64

from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
# from flask_socketio import SocketIO, emit
from ngsiv2 import *

app = Flask(__name__)

# Cargamos los datos de la función load de ngsiv2
load()

# # Informa de las actualizaciones a los clientes
# socketio = SocketIO(app)

# @socketio.on('update_notification')
# def handle_connect(data):
#     socketio.emit('update_notification',data)


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
def display_products():
    (status, products) = list_entities(type='Product', options='keyValues')
    if status == 200:
        images = []
        for product in products:
            enc_data_w_pad = product['image']
            enc_data_w_pad = enc_data_w_pad.ljust(math.ceil(len(enc_data_w_pad) / 4) * 4, '=')
            images.append(enc_data_w_pad)
        prods_imgs = zip(products, images)
        return render_template("products.html", prods_imgs=prods_imgs)

@app.route("/products/<id>")
def display_product(id):
    (status, product) = read_entity(id)
    if status == 200:
        (status, inventory_items) = list_entities(type = 'InventoryItem', options='keyValues',query = f'refProduct=={id}')
        if status == 200:
            (status, stores) = list_entities(type = 'Store', options = 'keyValues')
            if status == 200:
                return render_template('product.html', product = product, stores = stores, inventory_items = inventory_items)
        
@app.route("/stores/")
def display_stores():
    (status, stores) = list_entities(type='Store', options='keyValues')
    if status == 200:
        images = []
        for store in stores:
            imageb64 = store['image']
            imageb64 = imageb64.ljust(math.ceil(len(imageb64) / 4) * 4, '=')
            images.append(imageb64)
        
        stores_images = zip(stores, images)
        return render_template("stores.html", stores_images = stores_images)
    
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

# Definimos la ruta a Employee
@app.route("/employees/")
def display_employees():
 (status, employees) = list_entities(type = "Employee", options = 'keyValues')
 if status == 200:
    return render_template('employees.html', employees = employees)

@app.route('/employees/<id>') # DUDA!!!!
def display_employee(id):
   (status, employee) = read_entity(id)
   if status == 200:
        (status, inventory_items) = list_entities(type = 'Employee', options = 'keyValues', query = f'refEmployee=={id}')
        if status == 200:
            return render_template('employee.html', employee = employee, inventory_items = inventory_items)      

    


# Añadimos la creación y modificación de Product, Store (queda employee y modificaciones)

# Creación de un Product
@app.route("/products/create", methods=['GET', 'POST']) 
def create_product(): 
    
    if request.method == 'POST': 
        imgbase64 = request.form["image"].rstrip('=')
        product = {"id": request.form["id"],
                   "type": "Product", 
                   "name": {"type": "Text", "value": request.form["name"]}, 
                   "size": {"type": "Text", "value": request.form["size"]},
                   "price": {"type": "Integer", "value": int(request.form["price"])},
                   "image": {"type": "Text", "value": imgbase64},
                   "color": {"type": "Text", "value": request.form["color"]}}
        status = create_entity(product) 
        if status == 201:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('display_products')) 
    else:
        return render_template('create_product.html')


@app.route("/products/<id>/update", methods=['GET', 'POST'])
def modify_product(id):
    (status, product) = read_entity(id)
    imgb64 = product["image"]["value"]
    imgb64 = imgb64.ljust(math.ceil(len(imgb64) / 4) * 4, '=')
    
    if request.method == 'POST':
        base64 = request.form["image"].rstrip('=')
        attrs = {"name": {"type": "Text", "value": f'{request.form["name"]}'},
                    "size": {"type": "Text", "value": f'{request.form["size"]}'},
                    "price": {"type": "Integer", "value": int(request.form["price"])},
                    "image": {"type": "Text", "value": base64},
                    "color": {"type": "Text", "value": f'{request.form["color"]}'}}
        
        status = update_attrs(id, attrs)
        if status == 204:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('display_products'))
    else:
        return render_template('modify_product.html', product = product, imgb64 = imgb64)



# Creación de un Store (duda en el tipo de location y address, también en el html)
# para trabajar con location, solicitamos al cliente la latitud y longitud, de forma 
# que creamos automáticamente la lista de coordenadas nosotros, sin necesidad de que tenga que ponerlo él
@app.route("/stores/create", methods=['GET', 'POST']) 
def create_store(): 
    if request.method == 'POST': 
        image = request.files("image")
        image = image.read()
        imagebase64 = base64.b64encode(image).decode("utf8").rstrip("=")
        store = {"id": request.form["id"],
                "type": "Store",
                "name": {"type": "Text", "value": request.form["image"]},
                "address": {"type": "PostalAddress", "value": {"streetAddress": request.form["streetAddress"],
                                                                "addressRegion": request.form["region"],
                                                                "addressLocality": request.form["locality"],
                                                                "postalCode": int(request.form["code"])}},
                "location": {"type": "geo:json", "value": {"type": "Point", "coordinates": [float(request.form["longitude"]), float(request.form["latitude"])]}}, 
                "image": {"type": "Text", "value": imagebase64},
                "url": {"type": "Text", "value": request.form["url"]},
                "telephone": {"type": "Text", "value": request.form["telephone"]},
                "countryCode": {"type": "Text", "value": request.form["countryCode"]},
                "capacity": {"type": "Integer", "value": int(request.form["capacity"])},
                "description": {"type": "Text", "value": request.form["description"]}}
        
        provider_weather = {
                    "description": "Get Weather data for Store " + request.form["id"].split(":")[3],
                    "dataProvided": {
                        "entities": [
                        {
                            "id": request.form["id"],
                            "type": "Store"
                        }
                        ],
                        "attrs": [
                        "temperature",
                        "relativeHumidity"
                        ]
                    },
                    "provider": {
                        "http": {
                        "url": "http://context-provider:3000/random/weatherConditions"
                        },
                        "legacyForwarding": False
                    },
                    "status": "active"
                    }
        
        provider_tweets = {
                    "description": "Get Tweets for Store" + request.form["id"].split(":")[3],
                    "dataProvided": {
                        "entities": [
                        {
                            "id" : request.form["id"],
                            "type": "Store"
                        }
                        ],
                        "attrs": [
                        "tweets"
                        ]
                    },
                    "provider": {
                        "http": {
                        "url": "http://context-provider:3000/catfacts/tweets"
                        },
                        "legacyForwarding": False
                    },
                    "status": "active"
                    }
        
        status = create_entity(store) 
        if status == 201:
            status = register_contextProvider(provider_weather)
            if status == 201:
                status = register_contextProvider(provider_tweets)
                if status == 201:
                    next = request.args.get('next', None)
                    if next:
                        return redirect(next)
            return redirect(url_for('display_stores')) 
    else:
        return render_template('create_store.html')

@app.route("/stores/<id>/update", methods=['GET', 'POST'])
def modify_store(id):
    (status, store) = read_entity(id)
    imgb64 = store['image']['value']
    imgb64 = imgb64.ljust(math.ceil(len(imgb64) / 4) * 4, '=')
    if request.method == 'POST':
        img = request.files["image"]
        if img.filename != '':
            image = img.read()
            imagebase64 = base64.b64encode(image).decode('utf-8').rstrip('=')
        else:
            imagebase64 = store['image']['value']
        attrs = {"name": {"type": "Text", "value": request.form["name"]},
                    "address": {"type": "PostalAddress", "value": {'streetAddress': request.form["streetAddress"],
                                                                    'addressRegion': request.form["region"],
                                                                    'addressLocality': request.form["locality"],
                                                                    'postalCode': int(request.form["code"])}},
                    "location": {"type": "geo:json", "value": {"type": "Point", 
                                                               "coordinates": [float(coord) for coord in request.form["location"].split(",")]}},                    
                    "image": {"type": "Text", "value": imagebase64},
                    "url": {"type": "url", "value": request.form["url"]},
                    "telephone": {"type": "Integer", "value": int(request.form["telephone"])},
                    "countryCode": {"type": "Text", "value": request.form["countryCode"]},
                    "capacity": {"type": "Integer", "value": int(request.form["capacity"])},
                    "description": {"type": "Text", "value": request.form["description"]}}
        
        status = update_attrs(id, attrs)
        if status == 204:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('display_stores'))
    else:
        return render_template('modify_store.html', store = store, imgb64 = imgb64)

# Creación y modificación de un Employee 
@app.route("/employees/create", methods=['GET', 'POST']) 
def create_employee(): 
    (status, stores) = list_entities('Store', 'keyValues')
    list_stores = []
    for store in stores:
        list_stores.append(store['id'])   

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
            return redirect(url_for('display_employees')) 
    else:
        return render_template('create_employee.html', list_stores = list_stores) 
    

@app.route("/employees/<id>/update", methods=['GET', 'POST'])
def modify_employee(id):
    (status, employee) = read_entity(id)
    if request.method == 'POST':     
        attrs = {"name": {"type": "Text", "value": request.form["name"]},
                    "email": {"type": "Text", "value": request.form["email"]},
                    "dateOfContract": {"type": "Date", "value": request.form["dateOfContract"]},
                    "category": {"type": "Text", "value": request.form["category"]},
                    "salary": {"type": "Integer", "value": int(request.form["salary"])},
                    "skills": {"type": "Text", "value": request.form["skills"]},
                    "username": {"type": "Text", "value": request.form["username"]},
                    "password": {"type": "Text", "value": request.form["password"]}}                    
        status = update_attrs(id, attrs)
        if status == 204:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('display_employees'))
    else:
        return render_template('modify_employee.html', employee = employee)

# Creación de una Shelf dentro de una Store (para ello, podemos entrar en alguno de los stores
# de la página web e introducir a continuación)
@app.route("/stores/<store_id>/create_shelf", methods=['GET', 'POST'])
def create_shelf(store_id):
    if request.method == 'POST':
        shelf = {"id": request.form["id"],
                "type": "Shelf",
                "name": {"type": "Text", "value": request.form["name"]},
                "location": {"type": "geo:json", "value": {"type": "Point", "coordinates": [float(request.form["longitude"]), float(request.form["latitude"])]}},
                "maxCapacity": {"type": "Integer", "value": int(request.form["maxCapacity"])}, 
                "refStore": {"type": "Relationship", "value": f"urn:ngsi-ld:Store:{store_id}"}}  # Relación con el Store
        status = create_entity(shelf) 
        if status == 201:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('store', id=store_id)) 
    else:
        return render_template('create_shelf.html', store_id=store_id) 
  
@app.route("/stores/<id_store>/<id_shelf>/update", methods=['GET', 'POST'])    
def modify_shelf(id_store, id_shelf):
    (status, store) = read_entity(id_store)
    (status, shelf) = read_entity(id_shelf)
    if request.method == 'POST':
        attrs = {"name": {"type": "Text", "value": request.form["name"]},
                    "maxCapacity": {"type": "Integer", "value": int(request.form["maxCapacity"])},
                    "location": {"type": "geo:json", "value": {"type": "Point", "coordinates": [float(request.form["longitude"]), float(request.form["latitude"])]}}}
        
        status = update_attrs(id_shelf, attrs)
        if status == 204:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('store', id=id_store))
    else:
        return render_template('modify_shelf.html', store = store, shelf = shelf)
    
# Eliminaciones necesarias para los botones de los HTMLs
@app.route("/products/<id>/delete", methods=['POST', 'GET'])
def delete_product(id):
    (status) = delete_entity(id)
    if status == 204:
        return render_template('delete.html', ids=id)


@app.route("/employees/<id>/delete", methods=['POST', 'GET'])
def delete_employee(id):
    (status) = delete_entity(id)
    if status == 204:
        return render_template('delete.html', ids=id)
    
    
@app.route("/stores/<id>/delete", methods=['POST', 'GET'])
def delete_store(id):
    (status, registrations) = list_registrations()
    if status == 200:
        for reg in registrations:
            if reg['dataProvided']['entities'][0]['id'] == id:
                status = delete_registration(reg['id'])
    (status) = delete_entity(id)
    if status == 204:
        return render_template('delete.html', ids=id)

# Inventory Items
@app.route("/products/<id_product>/<id_store>/create_inventoryitem", methods=['GET', 'POST']) 
def create_inventoryitem(id_product, id_store):
    (status, product) = read_entity(id_product)
    (status, store) =read_entity(id_store)
    (status, shelves_product) = list_entities(type = 'InventoryItem',
                                                   options = 'keyValues',
                                                   attrs= 'refShelf',
                                                   query = f'refStore=={id_store};refProduct=={id_product}')
    (status, shelves_store) = list_entities(type = 'Shelf',
                                                 options = 'keyValues',
                                                 query = f'refStore=={id_store}')
    shelves_available = []
    for shelf_store in shelves_store:
        shelves_p = []
        for shelf_product in shelves_product:
            shelves_p.append(shelf_product['refShelf'])
        if shelf_store['id'] not in shelves_p:
            shelves_available.append(shelf_store['id'])

    if request.method == 'POST':
        inventoryitem = {
                    "id": f'{request.form["id"]}',
                    "type": "InventoryItem",
                    "refProduct": {"type": "Relationship", "value": f'{id_product}'},
                    "refShelf": {"type": "Relationship", "value": f'{request.form["refShelf"]}'},
                    "refStore": {"type": "Relationship", "value": f'{id_store}'},
                    "shelfCount": {"type": "Integer", "value": int(request.form["shelfCount"])},
                    "stockCount": {"type": "Integer", "value": int(request.form["stockCount"])}
        }
        status = create_entity(inventoryitem)
        if status == 201:
            next = request.args.get('next', None)
            if next:
                return redirect(next)
            return redirect(url_for('display_product', id=id_product))
    else:
        return render_template('create_inventoryitem.html', product = product, store = store, shelves_available = shelves_available)


# if __name__ == '__main__':
#     socketio.run(app, host="0.0.0.0")
    
# CAMBIAR LO DE STORES HTML !!!! (LO DE HUMIDITY > 20 Y ESO)
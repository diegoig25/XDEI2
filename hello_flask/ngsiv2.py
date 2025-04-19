import requests
import json

base_path = "http://localhost:1026/v2"

# PARA LAS ENTIDADES 

def create_entity(entity): 
    r = requests.post(base_path + "/entities/", json = entity)
    return r.status_code

def read_entity(entity_id): 
    r = requests.get(base_path + "/entities/" + entity_id)
    return(r.status_code, json.loads(r.text))

def list_entities(type = None, options = "count", attrs = None, query = None): # añadimos el parámetro query 
    url = base_path + "/entities/?type=" + type + "&options=" + options
    if attrs:
        url += "&attrs=" + attrs
    if query:
        url += "&q=" + query 

    r = requests.get(url)
    return r.status_code, json.loads(r.text)

    
def delete_entity(id):
    r = requests.delete(base_path + "/entities/" + id)
    return r.status_code


# PARA LOS ATRIBUTOS

def read_attr(id, attr): 
    r = requests.get(base_path + "/entities/" + id + "/attrs/" + attr)
    return(r.status_code, json.loads(r.text))

def update_attr(id, attr, val):
    payload = val
    headers = {'Content-Type': 'text/plain'}
    r = requests.put(base_path + "/entities/" + id + "/attrs/" + attr + "/value",headers=headers,json=payload)
    return r.status_code

def update_attrs(id, attrs_val):
    payload = json.dumps(attrs_val)
    headers = {'Content-Type': 'application/json'}
    r = requests.request("PATCH", base_path + "/entities/" + id + "/attrs",headers=headers,data=payload)
    return r.status_code

def delete_attr(id,attr): 
    r = requests.delete(base_path + "/entities/" + id + "/attrs/" + attr)
    return r.status_code   

def create_attrs(attrs): 
    headers = {'Content-Type': 'application/json'}
    r = requests.post(base_path + '/op/update/', headers = headers, data = json.dumps(attrs))
    return r.status_code   


# PROVEEDORES DE CONTEXTO
def register_contextProvider(provider):
    headers = {"Content-Type": "application/json"}
    r = requests.post(base_path + "/registrations", headers=headers, data=json.dumps(provider))
    return r.status_code

def list_registrations():
    r = requests.get(base_path + "/registrations")
    return(r.status_code, json.loads(r.text))

def delete_registration(reg_id):
    r = requests.delete(base_path + '/registrations/' + reg_id)
    return r.status_code

# SUBSCRIPCIONES
def create_subscription(sub):
    headers = {'Content-Type': 'application/json'}
    r = requests.post(base_path + '/subscriptions/', headers = headers, data = json.dumps(sub))
    return r.status_code 



# # Para la 2ª práctica, es necesario crear un nuevo tipo de entidad llamada employee
# def add_employee(id, name, email, date_of_contract, category, salary, skills, username, password, store_id):
#     employee = {
#         "id": f"urn:ngsi-ld:Employee:{id}",
#         "type": "Employee",
#         "name": {"type": "Text", "value": name},
#         "email": {"type": "Text", "value": email},
#         "dateOfContract": {"type": "Date", "value": date_of_contract},
#         "category": {"type": "Text", "value": category},
#         "salary": {"type": "Float", "value": salary},
#         "skills": {"type": "Text", "value": skills},
#         "username": {"type": "Text", "value": username},
#         "password": {"type": "Text", "value": password},
#         "store": {"type": "Relationship", "value": f"urn:ngsi-ld:Store:{store_id}"}
#     }
    
#     return create_entity(employee)
    
 
 
# def update_store(id, image, url, telephone, country_code, capacity, description, temperature, relative_humidity):
#     store_update = {
#         "image": {"type": "Text", "value": image},
#         "url": {"type": "Text", "value": url},
#         "telephone": {"type": "Text", "value": telephone},
#         "countryCode": {"type": "Text", "value": country_code},
#         "capacity": {"type": "Float", "value": capacity},
#         "description": {"type": "Text", "value": description},
#         "temperature": {"type": "Float", "value": temperature},
#         "relativeHumidity": {"type": "Float", "value": relative_humidity}
#     }
    
#     return update_attrs(f"urn:ngsi-ld:Store:{id}", store_update)

# def update_product(id, image, color):
#     product_update = {
#         "image": {"type": "Text", "value": image},
#         "color": {"type": "Text", "value": color},
#     }
#     return update_attrs(f"urn:ngsi-ld:Product:{id}", product_update)

# Creamos valores par poder acceder a ellos

def load():
    create_entity({
            "id":"urn:ngsi-ld:Employee:001", "type":"Employee",
            "name":{"type":"Text", "value":"Laura"},
            "email":{"type": "Text", "value": "laura456@hotmail.com"},
            "dateOfContract":{"type": "Date", "value": "2023-11-05"},
            "category":{"type": "Text", "value": "Manager"},
            "salary":{"type": "Integer", "value": "1800"},
            "skills":{"type": "Text", "value": "CustomerRelationships"},
            "username":{"type": "Text", "value": "luciaaa"},
            "password":{"type":"Text", "value": "lucia7890"},
            "refStore":{"type":"Relationship", "value": "urn:ngsi-ld:Store:001"}
        })

    create_attrs({
        "actionType":"append",
        "entities":[
            {
                "id":"urn:ngsi-ld:Store:001", "type":"Store",
                "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64_001"},
                "url": {"type": "URL", "value": "https://www.lidl.de/"},
                "telephone": {"type": "Integer", "value": 900100200},
                "countryCode": {"type": "Text", "value": "DE"},
                "capacity": {"type": "Integer", "value": 80},
                "description": {"type": "Text", "value": "Lidl near Alexanderplatz"}
            },
            {
                "id":"urn:ngsi-ld:Store:002", "type":"Store",
                "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64_002"},
                "url": {"type": "URL", "value": "https://www.lidl.de/"},
                "telephone": {"type": "Integer", "value": 900100201},
                "countryCode": {"type": "Text", "value": "DE"},
                "capacity": {"type": "Integer", "value": 95},
                "description": {"type": "Text", "value": "Supermarket at Potsdamer Platz"}
            },
            {
                "id":"urn:ngsi-ld:Store:003", "type":"Store",
                "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64_003"},
                "url": {"type": "URL", "value": "https://www.lidl.de/"},
                "telephone": {"type": "Integer", "value": 900100202},
                "countryCode": {"type": "Text", "value": "DE"},
                "capacity": {"type": "Integer", "value": 100},
                "description": {"type": "Text", "value": "Grocery store in Neukölln"}
            },
            {
                "id":"urn:ngsi-ld:Store:004", "type":"Store",
                "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64_004"},
                "url": {"type": "URL", "value": "https://www.lidl.de/"},
                "telephone": {"type": "Integer", "value": 900100203},
                "countryCode": {"type": "Text", "value": "DE"},
                "capacity": {"type": "Integer", "value": 110},
                "description": {"type": "Text", "value": "Store at Berlin Hauptbahnhof"}
            }
        ]
    })


    # Context Providers

    register_contextProvider({
    "description": "Get Tweets for Store 001",
    "dataProvided": {
        "entities": [
        {
            "id" : "urn:ngsi-ld:Store:001",
            "type": "Store"
        }
        ],
        "attrs": [
        "tweets"
        ]
    },
    "provider": {
        "http": {
        "url": "http://context-provider:3000/random/tweets"
        },
        "legacyForwarding": False
    },
    "status": "active"
    })

    register_contextProvider({
    "description": "Get Tweets for Store 002",
    "dataProvided": {
        "entities": [
        {
            "id" : "urn:ngsi-ld:Store:002",
            "type": "Store"
        }
        ],
        "attrs": [
        "tweets"
        ]
    },
    "provider": {
        "http": {
        "url": "http://context-provider:3000/random/tweets"
        },
        "legacyForwarding": False
    },
    "status": "active"
    })

    register_contextProvider({
    "description": "Get Tweets for Store 003",
    "dataProvided": {
        "entities": [
        {
            "id" : "urn:ngsi-ld:Store:003",
            "type": "Store"
        }
        ],
        "attrs": [
        "tweets"
        ]
    },
    "provider": {
        "http": {
        "url": "http://context-provider:3000/random/tweets"
        },
        "legacyForwarding": False
    },
    "status": "active"
    })

    register_contextProvider({
    "description": "Get Tweets for Store 004",
    "dataProvided": {
        "entities": [
        {
            "id" : "urn:ngsi-ld:Store:004",
            "type": "Store"
        }
        ],
        "attrs": [
        "tweets"
        ]
    },
    "provider": {
        "http": {
        "url": "http://context-provider:3000/random/tweets"
        },
        "legacyForwarding": False
    },
    "status": "active"
    })


    register_contextProvider({
    "description": "Get Weather data for Store 001",
    "dataProvided": {
        "entities": [
        {
            "id" : "urn:ngsi-ld:Store:001",
            "type": "Store"
        }
        ],
        "attrs": [
        "temperature", "relativeHumidity"
        ]
    },
    "provider": {
        "http": {
        "url": "http://context-provider:3000/random/weatherConditions"
        },
        "legacyForwarding": False
    },
    "status": "active"
    })


    register_contextProvider({
    "description": "Get Weather data for Store 002",
    "dataProvided": {
        "entities": [
        {
            "id" : "urn:ngsi-ld:Store:002",
            "type": "Store"
        }
        ],
        "attrs": [
        "temperature", "relativeHumidity"
        ]
    },
    "provider": {
        "http": {
        "url": "http://context-provider:3000/random/weatherConditions"
        },
        "legacyForwarding": False
    },
    "status": "active"
    })

    register_contextProvider({
    "description": "Get Weather data for Store 003",
    "dataProvided": {
        "entities": [
        {
            "id" : "urn:ngsi-ld:Store:003",
            "type": "Store"
        }
        ],
        "attrs": [
        "temperature", "relativeHumidity"
        ]
    },
    "provider": {
        "http": {
        "url": "http://context-provider:3000/random/weatherConditions"
        },
        "legacyForwarding": False
    },
    "status": "active"
    })


    register_contextProvider({
    "description": "Get Weather data for Store 004",
    "dataProvided": {
        "entities": [
        {
            "id" : "urn:ngsi-ld:Store:004",
            "type": "Store"
        }
        ],
        "attrs": [
        "temperature", "relativeHumidity"
        ]
    },
    "provider": {
        "http": {
        "url": "http://context-provider:3000/random/weatherConditions"
        },
        "legacyForwarding": False
    },
    "status": "active"
    })

    # Incorporate attrs for Products

    create_attrs({
    "actionType":"append",
    "entities":[
        {
        "id":"urn:ngsi-ld:Product:001", "type":"Product",
        "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64"},
        "color":{"type": "Text", "value": "#FF0000"}
        }
    ]
    })

    create_attrs({
    "actionType":"append",
    "entities":[
        {
        "id":"urn:ngsi-ld:Product:002", "type":"Product",
        "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64"},
        "color":{"type": "Text", "value": "#FFFF00"}
        }
    ]
    })


    create_attrs({
    "actionType":"append",
    "entities":[
        {
        "id":"urn:ngsi-ld:Product:003", "type":"Product",
        "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64"},
        "color":{"type": "Text", "value": "#FF0000"}
        }
    ]
    })


    create_attrs({
    "actionType":"append",
    "entities":[
        {
        "id":"urn:ngsi-ld:Product:004", "type":"Product",
        "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64"},
        "color":{"type": "Text", "value": "#468200"}
        }
    ]
    })


    create_attrs({
    "actionType":"append",
    "entities":[
        {
        "id":"urn:ngsi-ld:Product:005", "type":"Product",
        "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64"},
        "color":{"type": "Text", "value": "#468200"}
        }
    ]
    })


    create_attrs({
    "actionType":"append",
    "entities":[
        {
        "id":"urn:ngsi-ld:Product:006", "type":"Product",
        "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64"},
        "color":{"type": "Text", "value": "#FFD767"}
        }
    ]
    })

    create_attrs({
    "actionType":"append",
    "entities":[
        {
        "id":"urn:ngsi-ld:Product:007", "type":"Product",
        "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64"},
        "color":{"type": "Text", "value": "#FF4174"}
        }
    ]
    })

    create_attrs({
    "actionType":"append",
    "entities":[
        {
        "id":"urn:ngsi-ld:Product:008", "type":"Product",
        "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64"},
        "color":{"type": "Text", "value": "#FF411E"}
        }
    ]
    })


    create_attrs({
    "actionType":"append",
    "entities":[
        {
        "id":"urn:ngsi-ld:Product:009", "type":"Product",
        "image":{"type":"Text", "value": "NUEVA_IMAGEN_BASE64"},
        "color":{"type": "Text", "value": "#FFD767"}
        }
    ]
    })
    
    create_subscription({
    "description": "Notify me of low stock in Store 001",
    "subject": {
        "entities": [
        {
            "idPattern": ".*",
            "type": "InventoryItem"
        }
        ],
        "condition": {
        "attrs": [
            "shelfCount"
        ],
        "expression": {
            "q": "shelfCount<10;refStore==urn:ngsi-ld:Store:001"
        }
        }
    },
    "notification": {
        "http": {
        "url": "http://host.docker.internal:1026/stores/urn:ngsi-ld:Store:001"
        },
        "attrsFormat" : "keyValues"
    }})
    


    create_subscription({
    "description": "Notify me of price changes in products",
    "subject": {
        "entities": [
            {
                "idPattern": ".*",
                "type": "Product"
            }
        ],
        "condition": {
            "attrs": "price"
        }
    },
    "notification": {
        "http": {
        "url": "http://host.docker.internal:1026/products/urn:ngsi-ld:Product:001"
        },
        "attrsFormat": "keyValues"
    }})



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


# Para la 2ª práctica, es necesario crear un nuevo tipo de entidad llamada employee
def add_employee(id, name, email, date_of_contract, category, salary, skills, username, password, store_id):
    employee = {
        "id": f"urn:ngsi-ld:Employee:{id}",
        "type": "Employee",
        "name": {"type": "Text", "value": name},
        "email": {"type": "Text", "value": email},
        "dateOfContract": {"type": "Date", "value": date_of_contract},
        "category": {"type": "Text", "value": category},
        "salary": {"type": "Float", "value": salary},
        "skills": {"type": "Text", "value": skills},
        "username": {"type": "Text", "value": username},
        "password": {"type": "Text", "value": password},
        "store": {"type": "Relationship", "value": f"urn:ngsi-ld:Store:{store_id}"}
    }
    
    return create_entity(employee)
    
 
 
def update_store(id, image, url, telephone, country_code, capacity, description, temperature, relative_humidity):
    store_update = {
        "image": {"type": "Text", "value": image},
        "url": {"type": "Text", "value": url},
        "telephone": {"type": "Text", "value": telephone},
        "countryCode": {"type": "Text", "value": country_code},
        "capacity": {"type": "Float", "value": capacity},
        "description": {"type": "Text", "value": description},
        "temperature": {"type": "Float", "value": temperature},
        "relativeHumidity": {"type": "Float", "value": relative_humidity}
    }
    
    return update_attrs(f"urn:ngsi-ld:Store:{id}", store_update)

def update_product(id, image, color):
    product_update = {
        "image": {"type": "Text", "value": image},
        "color": {"type": "Text", "value": color},
    }
    return update_attrs(f"urn:ngsi-ld:Product:{id}", product_update)


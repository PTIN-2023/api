from flask import Flask, jsonify, request, abort, redirect, url_for, render_template
import pymongo
import datetime
import jwt


app = Flask(__name__, template_folder='/opt/templates/')

config = {
    "username": "root",
    "password": "root",
    "host": "mongo",
    "port": 27017
}

connector = "mongodb://{username}:{password}@{host}:{port}/?authSource=admin".format(**config)
client = pymongo.MongoClient(connector)
db = client["PTIN"]
users = db["UsersA4"]
farmacs = db["Medicaments"]

@app.route("/api")
def main():
    return render_template('main.html')


@app.route("/api/save", methods=['POST'])
def save():
    entry = {
        "name": request.form['name'],
        "email": request.form['email'],
        "id": request.form['idnum'],
        "when": datetime.datetime.now(),
    }
    res = users.insert_one(entry)
    users.create_index("id", unique=True)
    return render_template('main.html')

@app.route("/api/list", methods=['GET'])
def list_people():
    count = users.count_documents({})
    usuarios = users.find({})
    return render_template('list.html', count=count, usuarios=usuarios)

@app.route("/api/person/<idnum>", methods=['GET'])
def person(idnum):
    people = users.find_one({ 'id': idnum })
    if not people:
        abort(404)
    return render_template('person.html', person=people)


@app.errorhandler(404)
def not_found(error):
    app.logger.info(error)
    return redirect('404.html'), 404

@app.route("/api/get", methods=['POST'])
def get():
    name = request.form['name']
    doc = users.find_one({'name' : {'$regex': name}})
    if doc:
        app.logger.info(doc)
        return redirect(url_for('person', idnum=doc["id"]) )
    return render_template('main.html', error="Could not find that person")

@app.route("/api/login", methods=['POST'])
def prueba_login():
    user_email = 'laura.sanchez@gmail.com'
    user_password = 'laura123'
    doc = users.find_one({'user_email' : {'$regex': user_email}})
    if doc["user_email"]==user_email and doc["user_password"]==user_password:
        token = jwt.encode({'username': user_email}, 'mi_clave_secreta', algorithm='HS256')
        response = {'result': 'ok', 'user_given_name': doc["user_given_name"], 'user_role': doc["user_role"], 'user_picture': "https://picsum.photos/200", 'user_token': token}
######################################################Falta imatge
        print(response)
    else:
        response = {'result': 'error', 'message': 'Credenciales inválidas'}
        print(response)

#@app.route("/api/login", methods=['POST'])
#def login():
#data = request.get_json()
#entry = {
#    "user_email": data['user_email'],
#    "user_password": data['user_password']
#}
#doc = users.find_one({'user_email' : {'$regex': user_email}})
#if doc["user_email"]==user_email and doc["password"]==password:
#        token = jwt.encode({'username': email}, 'mi_clave_secreta', algorithm='HS256')
#        response = {'result': 'ok', 
#                    'user_given_name': doc["user_given_name"],
#                    'user_role': doc["user_role"], 
#                    'user_picture': 'url' #De donde se coge la url?
#                    'user_token': token}
#        return jsonify(response)
#    else:
#        response = {'result': 'error', 'message': 'Credenciales inválidas'}
#        return jsonify(response)
    
@app.route("/api/register", methods=['POST'])
def registrar():
    data = request.get_json()
    entry = {
        "user_full_name": data['user_full_name'],
        "user_given_name": data['user_given_name'],
        "user_role": "patient",
        "user_email": data['user_email'],
        "user_phone": data['user_phone'],
        "user_city": data['user_city'],
        "user_address":data['user_address'],
        "user_password": data['user_password'] ,
        "when": datetime.datetime.now(),
    }
    print(data['user_email'])
    try:
        id = users.insert_one(entry).inserted_id
        token = jwt.encode({'username': entry["user_email"]}, 'mi_clave_secreta', algorithm='HS256')
        response = {'result': 'ok', 'session_token': token}
    except pymongo.errors.DuplicateKeyError as description_error:
         response = {'result': 'error',
		     'description': str(description_error)}
    #response = {'result': 'ok'}
    return jsonify(response)

@app.route("/api/google", methods=['POST'])
def google():
    data = request.get_json()
    user_google = data['user_google_token']
###############################################################No es suficiente este token, falta info
    entry = {
            "user_full_name": data['user_full_name'],
            "user_given_name": data['user_given_name'],
            "user_email": data['user_email'],
            "user_phone": data['user_phone'],
            "user_city": data['user_city'],
            "user_address":data['user_address'],
            "user_password": data['user_password'] ,
            "when": datetime.datetime.now(),
    }
    try:
        id = users.insert_one(entry).inserted_id
        response = {'result': 'ok'}
#####################################################################################Falta token aquí, añadir en response
    except pymongo.errors.DuplicateKeyError as description_error:
         response = {'result': 'error',
		     'description': str(description_error)}
    #response = {'result': 'ok'}
    return jsonify(response)

@app.route("/api/medicines_list", methods=['POST']) #list_available_medicines", methods=['POST'])
def search_farmacs():
    data = request.get_json()
    query = {}
    if 'filter' in data:
        try:
            filter_data = data['filter'][0]

            if 'medName' in filter_data:
                query['medName'] = {'$regex': filter_data['medName']}

            if 'pvp_min' in filter_data:
                query['precio'] = {'$gte': float(filter_data['pvp_min'])}

            if 'pvp_max' in filter_data:
                if 'precio' in query:
                    query['precio']['$lte'] = float(filter_data['pvp_max'])
                else:
                    query['precio'] = {'$lte': float(filter_data['pvp_max'])}

            if 'receta' in filter_data:
                if True in filter_data['receta']:
                    query['detalles'] = {'$regex': 'Receta necesaria'}
                if False in filter_data['receta']:
                    query['detalles'] = {'$regex': 'Receta no necesaria'}

            if 'forma' in filter_data:
                query['forma'] = {'$in': filter_data['forma']}

            if 'via' in filter_data:
                query['via'] = {'$in': filter_data['via']}

         # Determinem el número de medicaments per pàgina i la pàgina que es vol obtenir
            medNum = int(filter_data.get('medNum', '10'))
            page = int(filter_data.get('page', '1'))

         # Calculem el límit inferior i superior de medicaments a obtenir segons la pàgina i el número de medicaments per pàgina
            limit_inf = (page - 1) * medNum
            limit_sup = limit_inf + medNum

    #     # Executem la query amb els límits especificats
            results = farmacs.find(query).limit(medNum).skip(limit_inf)
        except Exception as e:
            results = str(e)
# Si no es proporciona un filtre, es retornen tots els medicaments
    else:
        results = farmacs.find()

    #results = farmacs.find()
    return jsonify([{
        'medName': doc['nom'],
        'codi_nacional': doc['codi_nacional'],
        'tipus_us': str(doc['tipus_us']) + '€',
        'administracio': doc['administracio'],
        'req_recepta': doc['req_recepta'],
        'preu': doc['preu'],
        'presentacio': doc['presentacio'],
    } for doc in results])
 

@app.route("/api/has_prescription", methods=['POST'])
def has_prescription():
    data = request.get_json()
    decoded_token = jwt.decode(data['session_token'], 'mi_clave_secreta', algorithm='HS256')
    med = data['medicine_identifier']
    query = {'_id': med, 'req_recepta': True}
    prescription_needed = farmacs.find_one(query)
    if prescription_needed:
        prescription_given = False
####################################################################################################Hablar con DDBB para que hagan una tabla o algo en la que pueda ver si un cliente tiene un medicamento determinado recetado
    else:
        prescription_given = False
    response = {'result': 'falta comprovar prescription given', 'prescription_needed': prescription_needed["prescription_needed"], 'prescription_given': prescription_given}
    return jsonify(response)


@app.route("/api/checktoken", methods=['POST'])
def check_token():
    decoded_token = jwt.decode('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImxhdXJhLnNhbmNoZXpAZ21haWwuY29tIn0.fxd5qO7A0yqMzwuoXUTW4Ubh8CtcGcjrk0I8R4zzCt8', 'mi_clave_secreta', algorithm='HS256')
    query = {'user_email': decoded_token['username']}
    print(query)
    user_with_email = users.find_one(query)
    if user_with_email is None:
        response = {'valid': 'yes', 'type': 'None'}
    else:
        response = {'valid': 'mail no trobat', 'type': user_with_email["user_role"]}
    return jsonify(response)

prueba_login()
check_token()

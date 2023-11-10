from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
#from flask_sqlalchemy import SQLAlchemy
#from werkzeug.security import generate_password_hash, check_password_hash
from tensorflow.keras.models import load_model
from pymongo import MongoClient
from bson import json_util
import ssl
import json
#from passlib.hash import pbkdf2_sha256
#import requests
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sweswe'  


connection_string = "mongodb+srv://vsswetha:swetha@cluster0.0jvyqaa.mongodb.net/"

# Create a MongoClient instance
client = MongoClient(connection_string)

# Access your MongoDB Atlas database and collection
db = client.users_db
collection = db.users_collection

print("db connected")
print(db)
print(collection)

    
def register_user():
    # Hash the password before storing it in the database
    data = request.get_json()
    phoneno= data["phoneNumber"]
    user_data = data
    #return "inside reg user"
    # Check if the user already exists
    existing_user = collection.find_one({"phoneNumber": phoneno})
    if existing_user:
        return False  # User already exists
    else:
        collection.insert_one(user_data)
        return True  # User registered successfully

# Function to log in a user
def login_user(phoneNumber, password):
    # Retrieve the user from the database
    user = collection.find_one({"phoneNumber": phoneNumber})

    if user:
        return True  # Login successful
    else:
        return False  # Login failed


@app.route("/register", methods=["POST"])
def register():
    
        #return "inside post"
    if register_user():
        return "okk"
    else:
        return "Username already exists. Choose a different one."

@app.route("/details", methods=["GET"])
def details():
     # Initialize the MongoClient
    
    # Fetch all documents from the collection
    all_documents = list(collection.find())

    # Close the MongoDB connection
   

    # Convert the documents to a JSON response
    for doc in all_documents:
        doc['_id'] = str(doc['_id'])
    response = jsonify(all_documents)
    return response
    # print(collection.find())
    # return json.loads(json_util.dumps(collection.find()))
    # return ""



    

@app.route("/login", methods=["POST"])
def login():
    
    data = request.get_json()
    phone_no = data['phoneNumber']
    password = data['password']
    if login_user(phone_no, password):
        session["phoneNumber"] = phone_no
        return "sucess"
    else:
        return "Login failed. Please check your credentials."

   

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/home")
def home():
    
    return "ok"



def reverse_geocode(lat, lng, api_key):
    # Google Maps Geocoding API endpoint
    endpoint = "https://maps.googleapis.com/maps/api/geocode/json"

    # Parameters for the request
    params = {
        "latlng": f"{lat},{lng}",
        "key": api_key,
    }

    # Send a GET request to the API
    response = requests.get(endpoint, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['status'] == "OK" and data['results']:
            # Extract the formatted address from the results
            formatted_address = data['results'][0]['formatted_address']
            return formatted_address
        else:
            return "Location not found"
    else:
        return "Error in the API request"
    
@app.route('/predict', methods=['POST'])
def predict():
    try:
        model1 = load_model('AcceleratorModel.h5')
        model2 = load_model('GyroscopeModel.h5')
        data = request.get_json()
        age = data['age']
        gyro_x = data['gyro_x']
        gyro_y = data['gyro_y']
        gyro_z = data['gyro_z']
        longitude = data['long']
        latitude = data['latt']
        height = data['height']
        weight = data['weight']
        acc_x = data['acc_x']
        acc_y = data['acc_y']
        acc_z = data['acc_z']
        input_data1 = np.array([[age,gyro_x, gyro_y, gyro_z, height,weight ]])
        input_data2 = np.array([[age,acc_x,acc_y,acc_z, height,weight ]])
        prediction1 = model1.predict(input_data1)
        prediction2 = model2.predict(input_data2)

        response = {'prediction1': prediction1[0], 'prediction2': prediction2[0]}
        # api_key = "your_api_key"
        # location = reverse_geocode(latitude, longitude, api_key)

        # print(location)
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True, port=8082)



# Replace 'your_api_key' with your actual Google Maps Geocoding API key

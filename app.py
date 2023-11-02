from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
#from flask_sqlalchemy import SQLAlchemy
#from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
from pymongo import MongoClient
import certifi
ca = certifi.where()
#from passlib.hash import pbkdf2_sha256
#import requests
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sweswe'  


connection_string = "mongodb+srv://vsswetha:swetha@cluster0.0jvyqaa.mongodb.net/"

# Create a MongoClient instance
client = MongoClient(connection_string, tlsCAFile=ca)

# Access your MongoDB Atlas database and collection
db = client.users_db
collection = db.users_collection


    
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


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #return "inside post"
        if register_user():
            return "okk"
        else:
            return "Username already exists. Choose a different one."

    return "reg"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        phone_no = data['phoneNumber']
        password = data['password']
        if login_user(phone_no, password):
            session["phoneNumber"] = phone_no
            return "sucess"
        else:
            return "Login failed. Please check your credentials."

    return "login done"

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

@app.route("/home")
def home():
    print("HELO")
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
        model = "model name podu"
        data = request.get_json()
        gyro_x = data['gyro_x']
        gyro_y = data['gyro_y']
        gyro_z = data['gyro_z']
        longitude = data['long']
        latitude = data['latt']
        pulse = data['pulse']
        acc_x = data['acc_x']
        acc_y = data['acc_y']
        acc_z = data['acc_z']
        input_data = np.array([[gyro_x, gyro_y, gyro_z, pulse, acc_x,acc_y,acc_z]])
        
        prediction = model.predict(input_data)

        response = {'prediction': prediction[0]}
        api_key = "your_api_key"
        location = reverse_geocode(latitude, longitude, api_key)

        print(location)
        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    #db.create_all()
    app.run(debug=True, port=8082)



# Replace 'your_api_key' with your actual Google Maps Geocoding API key

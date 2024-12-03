from firebase_admin import credentials, firestore
from flask import Flask, jsonify, request, render_template, redirect, url_for
import firebase_admin
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Firebase
if os.getenv("PRIVATE_KEY") and os.getenv("CLIENT_EMAIL"):
    # Use environment variables from Netlify (ensure they are uppercase)
    firebase_config = {
        "type":
        os.getenv("TYPE"),
        "project_id":
        os.getenv("PROJECT_ID"),
        "private_key_id":
        os.getenv("PRIVATE_KEY_ID"),
        "private_key":
        os.getenv("PRIVATE_KEY").replace('\\n', '\n')
        if os.getenv("PRIVATE_KEY") else None,
        "client_email":
        os.getenv("CLIENT_EMAIL"),
        "client_id":
        os.getenv("CLIENT_ID"),
        "auth_uri":
        "https://accounts.google.com/o/oauth2/auth",
        "token_uri":
        "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url":
        "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url":
        os.getenv("CLIENT_X509_CERT_URL")
    }

    # Ensure all required keys are available
    if firebase_config["private_key"] and firebase_config["client_email"]:
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
        print("Firebase app initialized successfully.")
    else:
        print("Error: Missing Firebase credentials.")
else:
    print("Error: Firebase credentials not found in environment variables.")

# Debug log to check environment variables
print("TYPE:", os.getenv("TYPE"))
print("PROJECT_ID:", os.getenv("PROJECT_ID"))

# Initialize Firestore
db = firestore.client()

try:
    test_doc = db.collection('test').document('test_doc').get()
    if test_doc.exists:
        print("Firestore connection successful!")
    else:
        print("Firestore connection seems okay, but no data found.")
except Exception as e:
    print(f"Firestore connection error: {e}")

app = Flask(__name__, template_folder='.')


# Home route (renders index.html)
@app.route('/')
def home():
    return render_template('index.html')


# Route to get all products (API)
@app.route('/products', methods=['GET'])
def get_products():
    try:
        inventory_ref = db.collection('inventory')
        docs = inventory_ref.stream()

        products = []
        for doc in docs:
            product = doc.to_dict()
            product['id'] = doc.id  # Include document ID
            expiration_date = product.get('Expiration date')

            if isinstance(expiration_date, str):
                product['Expiration date'] = expiration_date
            elif isinstance(expiration_date, datetime):
                product['Expiration date'] = expiration_date.date().isoformat()
            elif isinstance(expiration_date, firestore.Timestamp):
                product['Expiration date'] = expiration_date.date().isoformat()

            products.append(product)

        # Sort products by expiration date in ascending order
        products.sort(key=lambda x: x['Expiration date'])

        return jsonify(products), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to display inventory in a template (web page)
@app.route('/inventory')
def inventory():
    try:
        inventory_ref = db.collection('inventory')
        docs = inventory_ref.stream()

        products = []
        for doc in docs:
            product = doc.to_dict()
            product['id'] = doc.id
            expiration_date = product.get('Expiration date')

            if isinstance(expiration_date, str):
                product['Expiration date'] = expiration_date
            elif isinstance(expiration_date, datetime):
                product['Expiration date'] = expiration_date.date().isoformat()
            elif isinstance(expiration_date, firestore.Timestamp):
                product['Expiration date'] = expiration_date.date().isoformat()

            products.append(product)

        # Sort products by expiration date in ascending order
        products.sort(key=lambda x: x['Expiration date'])

        return render_template('inventory.html', products=products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to delete a product
@app.route('/delete-product/<product_id>', methods=['POST'])
def delete_product(product_id):
    try:
        # Deleting the product from Firestore
        db.collection('inventory').document(product_id).delete()

        # Redirect to the inventory page after successful deletion
        return redirect(url_for('inventory'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to handle adding a new product
@app.route('/add-product', methods=['GET'])
def add_product_page():
    return render_template('add-product.html')


@app.route('/add-product', methods=['POST'])
def add_product():
    try:
        # Get product data from the request
        data = request.get_json()
        product_name = data.get('product_name')
        expiration_date = data.get('expiration_date')
        units = data.get('units')

        # Add product to Firestore
        db.collection('inventory').add({
            'Product': product_name,
            'Expiration date': expiration_date,
            'Units': units
        })

        # Respond with success message
        return jsonify({"message": "Product added successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

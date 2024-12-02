from flask import Flask, jsonify, request, render_template
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("credentials/your-firebase-key.json")
firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

app = Flask(__name__)

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
            products.append(product)

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
            products.append(product)

        return render_template('inventory.html', products=products)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to add a product
@app.route('/add-product', methods=['POST'])
def add_product():
    try:
        data = request.get_json()
        product = {
            'Product': data['Product'],
            'Expiration date': data['Expiration date'],  # Make sure date format is compatible
            'Units': data['Units']
        }

        db.collection('inventory').add(product)
        return jsonify({"message": "Product added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

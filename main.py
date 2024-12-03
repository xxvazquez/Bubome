from firebase_admin import credentials, firestore
from flask import Flask, jsonify, request, render_template, redirect, url_for
import firebase_admin
from datetime import datetime

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
            expiration_date = product.get('Expiration date')

            if isinstance(expiration_date, str):
                # If it's a string, ensure it's in the correct date format
                product['Expiration date'] = expiration_date
            elif isinstance(expiration_date, datetime):
                # If it's a datetime object, convert it to string
                product['Expiration date'] = expiration_date.date().isoformat()
            elif isinstance(expiration_date, firestore.Timestamp):
                # If it's a Firestore Timestamp, convert it to string
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
                # If it's a string, ensure it's in the correct date format
                product['Expiration date'] = expiration_date
            elif isinstance(expiration_date, datetime):
                # If it's a datetime object, convert it to string
                product['Expiration date'] = expiration_date.date().isoformat()
            elif isinstance(expiration_date, firestore.Timestamp):
                # If it's a Firestore Timestamp, convert it to string
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


if __name__ == '__main__':
    app.run(debug=True)

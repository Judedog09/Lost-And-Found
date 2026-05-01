from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'data.json'

# --- DATA HANDLING ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

# API: Get all items (READ)
@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(load_data())

# API: Add new item (CREATE)
@app.route('/api/items', methods=['POST'])
def add_item():
    items = load_data()
    # Basic Validation
    new_item = {
        "id": len(items) + 1,
        "name": request.json.get('name', 'Unknown'),
        "description": request.json.get('description', ''),
        "location": request.json.get('location', 'Office'),
        "status": "Lost"
    }
    items.append(new_item)
    save_data(items)
    return jsonify({"message": "Item added successfully!"}), 201

# API: Remove item (DELETE)
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    items = load_data()
    items = [i for i in items if i['id'] != item_id]
    save_data(items)
    return jsonify({"message": "Item removed!"})

if __name__ == '__main__':
    app.run(debug=True)
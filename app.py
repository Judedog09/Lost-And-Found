from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = 'data.json'

# --- DATA HANDLING (With Crash Protection) ---
def load_data():
    # If the file doesn't exist, return an empty list
    if not os.path.exists(DATA_FILE):
        return []
    
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            # If the file is completely blank or corrupted, return an empty list safely
            return []

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
    
    # Generate a new ID based on the highest existing ID
    new_id = 1 if len(items) == 0 else max(item['id'] for item in items) + 1
    
    new_item = {
        "id": new_id,
        "name": request.json.get('name', 'Unknown'),
        "description": request.json.get('description', ''),
        "location": request.json.get('location', 'Office'),
        "status": "Found"
    }
    
    items.append(new_item)
    save_data(items)
    return jsonify({"message": "Item added successfully!"}), 201

# API: Remove item (DELETE)
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    items = load_data()
    # Keep all items EXCEPT the one with the matching ID
    items = [i for i in items if i['id'] != item_id]
    save_data(items)
    return jsonify({"message": "Item removed!"})

if __name__ == '__main__':
    app.run(debug=True)
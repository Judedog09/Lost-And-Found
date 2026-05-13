from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import secrets
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'data.json'
SECRET_KEY_FILE = '.secret_key'

def get_secret_key():
    if os.path.exists(SECRET_KEY_FILE):
        with open(SECRET_KEY_FILE, 'r') as f:
            return f.read().strip()
    key = secrets.token_hex(32)
    with open(SECRET_KEY_FILE, 'w') as f:
        f.write(key)
    return key

app.secret_key = get_secret_key()

BLOCKED_WORDS = [
    "nigger", "nigga", "faggot", "fag", "chink", "spic", "kike", "wetback",
    "retard", "tranny", "cunt", "whore", "slut", "bitch", "fuck", "shit",
    "ass", "dick", "cock", "pussy", "bastard", "motherfucker", "twat"
]

def contains_blocked_word(text):
    normalized = ''.join(c.lower() for c in text if c.isalpha())
    return any(word in normalized for word in BLOCKED_WORDS)

# --- DATA HANDLING ---
def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- PUBLIC ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

# --- SECURE ADMIN ROUTES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'chargers2026':
            session['is_admin'] = True
            return redirect(url_for('admin'))
        else:
            error = "Incorrect password."

    return f'''
        <div style="max-width: 400px; margin: 100px auto; text-align: center; font-family: 'Segoe UI', sans-serif; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
            <h2 style="color: #B30000; margin-bottom: 20px;">Admin Login</h2>
            {f'<p style="color: #dc2626; font-weight: bold;">{error}</p>' if error else ''}
            <form method="POST">
                <input type="password" name="password" placeholder="Enter Password" required style="padding: 12px; width: 100%; margin-bottom: 20px; box-sizing: border-box; border: 2px solid #e4e4e7; border-radius: 5px; outline: none;">
                <button type="submit" style="padding: 12px; width: 100%; background: #B30000; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; font-size: 1rem;">Login</button>
            </form>
            <br><a href="/" style="color: #52525b; text-decoration: none; display: inline-block; margin-top: 15px;">&larr; Back to Search</a>
        </div>
        <style>body {{ background-color: #f4f4f5; }} input:focus {{ border-color: #B30000 !important; }}</style>
    '''

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

# --- API ROUTES ---
@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(load_data())

@app.route('/api/items', methods=['POST'])
def add_item():
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized"}), 403
    items = load_data()
    new_id = 1 if len(items) == 0 else max(item['id'] for item in items) + 1
    new_item = {
        "id": new_id,
        "name": request.json.get('name', 'Unknown'),
        "description": request.json.get('description', ''),
        "location": request.json.get('location', 'Office'),
        "status": "Found",
        "date_added": datetime.now().strftime('%Y-%m-%d'),
        "claimer_name": None
    }
    items.append(new_item)
    save_data(items)
    return jsonify({"message": "Item added successfully!"}), 201

@app.route('/api/items/<int:item_id>/claim', methods=['PATCH'])
def claim_item(item_id):
    data = request.get_json() or {}
    claimer_name = data.get('claimer_name', '').strip()
    if contains_blocked_word(claimer_name):
        return jsonify({"error": "Invalid name."}), 400
    items = load_data()
    for item in items:
        if item['id'] == item_id:
            item['status'] = 'Claimed'
            item['claimer_name'] = claimer_name
            save_data(items)
            return jsonify({"message": "Item marked as claimed."})
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/items/<int:item_id>/unclaim', methods=['PATCH'])
def unclaim_item(item_id):
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized"}), 403
    items = load_data()
    for item in items:
        if item['id'] == item_id:
            item['status'] = 'Found'
            item['claimer_name'] = None
            save_data(items)
            return jsonify({"message": "Item unclaimed."})
    return jsonify({"error": "Item not found"}), 404

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    if not session.get('is_admin'):
         return jsonify({"error": "Unauthorized"}), 403

    items = load_data()
    items = [i for i in items if i['id'] != item_id]
    save_data(items)
    return jsonify({"message": "Item removed!"})

if __name__ == '__main__':
    app.run(debug=True)

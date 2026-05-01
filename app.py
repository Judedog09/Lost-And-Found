from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# This is a temporary list acting as your database
items_db = [
    {"id": 1, "name": "Blue Water Bottle", "desc": "Hydroflask with stickers", "loc": "Gym", "status": "Lost"},
    {"id": 2, "name": "Calculus Textbook", "desc": "Name 'Alex' written inside", "loc": "Library", "status": "Found"}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/admin')
def admin_page():
    return render_template('admin.html')

# API to get all items
@app.route('/api/items', methods=['GET'])
def get_items():
    return jsonify(items_db)

# API for Admin to add items
@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.json
    new_item = {
        "id": len(items_db) + 1,
        "name": data['name'],
        "desc": data['desc'],
        "loc": data['loc'],
        "status": "Found"
    }
    items_db.append(new_item)
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(debug=True)
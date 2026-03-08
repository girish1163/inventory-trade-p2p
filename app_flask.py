from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])

# Simple in-memory database
DATABASE = {
    "users": [
        {
            "id": "1",
            "username": "admin",
            "email": "admin@inventory.com",
            "password": "girish7890@A",
            "role": "admin",
            "created_at": datetime.now().isoformat()
        }
    ],
    "inventory": [],
    "billing": [],
    "notes": []
}

def calculate_status(quantity, min_stock):
    if quantity == 0:
        return "Out of Stock"
    elif quantity <= min_stock:
        return "Low Stock"
    else:
        return "In Stock"

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    # Handle default credentials
    if (email == "743663" and password == "girish7890@A") or \
       (email == "admin@inventory.com" and password == "girish7890@A"):
        
        user = DATABASE["users"][0]
        return jsonify({
            "access_token": "demo-token",
            "token_type": "bearer",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"],
                "created_at": user["created_at"]
            }
        })
    
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    # Simple token validation for demo
    auth_header = request.headers.get('Authorization')
    if auth_header and 'Bearer demo-token' in auth_header:
        user = DATABASE["users"][0]
        return jsonify({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"]
        })
    
    return jsonify({"message": "Invalid token"}), 401

# Stock List endpoints
@app.route('/api/stock', methods=['GET'])
def get_stock_list():
    return jsonify(DATABASE["inventory"])

@app.route('/api/stock/alerts', methods=['GET'])
def get_stock_alerts():
    low_stock = [item for item in DATABASE["inventory"] if item["status"] == "Low Stock"]
    out_of_stock = [item for item in DATABASE["inventory"] if item["status"] == "Out of Stock"]
    return jsonify(low_stock + out_of_stock)

# Inventory Management endpoints
@app.route('/api/inventory', methods=['GET'])
def get_inventory_items():
    return jsonify(DATABASE["inventory"])

@app.route('/api/inventory', methods=['POST'])
def create_inventory_item():
    data = request.get_json()
    new_item = {
        "id": str(uuid.uuid4()),
        **data,
        "status": calculate_status(data.get('quantity', 0), data.get('min_stock_level', 10)),
        "created_at": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    DATABASE["inventory"].append(new_item)
    return jsonify(new_item), 201

@app.route('/api/inventory/<item_id>', methods=['PUT'])
def update_inventory_item(item_id):
    data = request.get_json()
    for i, item in enumerate(DATABASE["inventory"]):
        if item["id"] == item_id:
            updated_item = {
                **item,
                **data,
                "status": calculate_status(data.get('quantity', item['quantity']), data.get('min_stock_level', item['min_stock_level'])),
                "last_updated": datetime.now().isoformat()
            }
            DATABASE["inventory"][i] = updated_item
            return jsonify(updated_item)
    
    return jsonify({"message": "Item not found"}), 404

@app.route('/api/inventory/<item_id>', methods=['DELETE'])
def delete_inventory_item(item_id):
    for i, item in enumerate(DATABASE["inventory"]):
        if item["id"] == item_id:
            DATABASE["inventory"].pop(i)
            return jsonify({"message": "Item deleted successfully"})
    
    return jsonify({"message": "Item not found"}), 404

# Billing endpoints
@app.route('/api/billing', methods=['GET'])
def get_billing_items():
    return jsonify(DATABASE["billing"])

@app.route('/api/billing', methods=['POST'])
def create_billing_item():
    data = request.get_json()
    new_billing = {
        "id": str(uuid.uuid4()),
        **data,
        "status": "Pending",
        "created_at": datetime.now().isoformat()
    }
    DATABASE["billing"].append(new_billing)
    return jsonify(new_billing), 201

@app.route('/api/billing/<billing_id>/status', methods=['PUT'])
def update_billing_status(billing_id):
    data = request.get_json()
    status = data.get('status')
    
    for i, item in enumerate(DATABASE["billing"]):
        if item["id"] == billing_id:
            DATABASE["billing"][i]["status"] = status
            return jsonify({"message": "Billing status updated"})
    
    return jsonify({"message": "Billing item not found"}), 404

# Notes endpoints
@app.route('/api/notes', methods=['GET'])
def get_notes():
    return jsonify(DATABASE["notes"])

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    new_note = {
        "id": str(uuid.uuid4()),
        **data,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    DATABASE["notes"].append(new_note)
    return jsonify(new_note), 201

@app.route('/api/notes/<note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.get_json()
    for i, note in enumerate(DATABASE["notes"]):
        if note["id"] == note_id:
            updated_note = {
                **note,
                **data,
                "updated_at": datetime.now().isoformat()
            }
            DATABASE["notes"][i] = updated_note
            return jsonify(updated_note)
    
    return jsonify({"message": "Note not found"}), 404

@app.route('/api/notes/<note_id>', methods=['DELETE'])
def delete_note(note_id):
    for i, note in enumerate(DATABASE["notes"]):
        if note["id"] == note_id:
            DATABASE["notes"].pop(i)
            return jsonify({"message": "Note deleted successfully"})
    
    return jsonify({"message": "Note not found"}), 404

# Dashboard endpoint
@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_stats():
    total_items = len(DATABASE["inventory"])
    low_stock = len([item for item in DATABASE["inventory"] if item["status"] == "Low Stock"])
    out_of_stock = len([item for item in DATABASE["inventory"] if item["status"] == "Out of Stock"])
    total_value = sum(item["quantity"] * item["unit_price"] for item in DATABASE["inventory"])
    pending_bills = len([bill for bill in DATABASE["billing"] if bill["status"] == "Pending"])
    total_notes = len(DATABASE["notes"])
    
    return jsonify({
        "total_items": total_items,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
        "total_value": total_value,
        "pending_bills": pending_bills,
        "total_notes": total_notes
    })

@app.route('/')
def root():
    return jsonify({
        "message": "Inventory Management System API is running...",
        "database": "In-Memory Demo",
        "sectors": ["Stock List", "Inventory Management", "Billing", "Notes"]
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "database": "In-Memory Demo",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚀 Starting Inventory Management System")
    print("📊 Available Sectors:")
    print("   1. Stock List - View current stock levels and alerts")
    print("   2. Inventory Management - Add, edit, delete inventory items")
    print("   3. Billing - Manage invoices and billing")
    print("   4. Notes - Create and manage notes")
    print("\n🔑 Default Credentials:")
    print("   User ID: 743663")
    print("   Password: girish7890@A")
    print("\n🌐 API will be available at: http://localhost:5000")
    print("📖 API Documentation: http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)

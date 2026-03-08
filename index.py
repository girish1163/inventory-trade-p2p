from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import os

app = Flask(__name__)
CORS(app, origins=["*"])

# Simple in-memory database for Vercel deployment
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
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Management System</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
                sans-serif;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            text-align: center;
            background: white;
            padding: 3rem;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 600px;
            margin: 2rem;
        }
        h1 {
            color: #333;
            margin-bottom: 1rem;
            font-size: 2.5rem;
        }
        .emoji {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        .feature {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        .feature h3 {
            margin: 0 0 0.5rem 0;
            color: #667eea;
            font-size: 1.1rem;
        }
        .feature p {
            margin: 0;
            color: #666;
            font-size: 0.9rem;
        }
        .login-info {
            background: #e3f2fd;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 2rem 0;
            border-left: 4px solid #2196f3;
        }
        .login-info h3 {
            margin: 0 0 1rem 0;
            color: #1976d2;
        }
        .login-info p {
            margin: 0.5rem 0;
            color: #424242;
        }
        .status {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            display: inline-block;
        }
        .api-info {
            background: #fff3e0;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #ff9800;
        }
        .api-info h4 {
            margin: 0 0 0.5rem 0;
            color: #f57c00;
        }
        .api-info p {
            margin: 0;
            color: #666;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">📦</div>
        <div class="status">🚀 API Server Running</div>
        <h1>Inventory Management API</h1>
        <p style="font-size: 1.2rem; color: #666; margin-bottom: 2rem;">
            Complete backend API for inventory management system
        </p>
        
        <div class="features">
            <div class="feature">
                <h3>📋 Stock List</h3>
                <p>Real-time stock monitoring</p>
            </div>
            <div class="feature">
                <h3>📦 Inventory</h3>
                <p>Add, edit, delete items</p>
            </div>
            <div class="feature">
                <h3>💰 Billing</h3>
                <p>Invoices & payments</p>
            </div>
            <div class="feature">
                <h3>📝 Notes</h3>
                <p>Organized notes system</p>
            </div>
        </div>
        
        <div class="login-info">
            <h3>🔑 Login Credentials</h3>
            <p><strong>User ID:</strong> 743663</p>
            <p><strong>Password:</strong> girish7890@A</p>
            <p style="font-size: 0.9rem; color: #666; margin-top: 1rem;">
                💡 All amounts are displayed in Indian Rupees (₹)
            </p>
        </div>
        
        <div class="api-info">
            <h4>🔗 Available API Endpoints</h4>
            <p>POST /api/auth/login - User authentication</p>
            <p>GET /api/dashboard - Dashboard statistics</p>
            <p>GET /api/inventory - List inventory items</p>
            <p>POST /api/inventory - Create inventory item</p>
            <p>GET /api/billing - List billing items</p>
            <p>GET /api/notes - List notes</p>
        </div>
        
        <p style="margin-top: 2rem; color: #666; font-size: 0.9rem;">
            🐍 Flask API • Deployed on Vercel • In-Memory Database
        </p>
    </div>
</body>
</html>
    '''

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "database": "In-Memory Demo",
        "timestamp": datetime.now().isoformat()
    })

# Vercel serverless handler
def handler(request):
    return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    app.run(debug=True)

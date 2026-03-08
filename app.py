from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import uuid
import os

app = Flask(__name__)
CORS(app, origins=["*"])

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
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')
    
    if (email == "743663" and password == "girish7890@A") or \
       (email == "admin@inventory.com" and password == "girish7890@A"):
        
        user = DATABASE["users"][0]
        return jsonify({
            "access_token": "demo-token",
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            }
        })
    
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    auth_header = request.headers.get('Authorization')
    if auth_header and 'Bearer demo-token' in auth_header:
        user = DATABASE["users"][0]
        return jsonify({
            "user": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "role": user["role"]
            }
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
    data = request.get_json(silent=True) or {}
    
    # Validate required fields
    if not data.get('name') or not data.get('sku'):
        return jsonify({"message": "Name and SKU are required"}), 400
    
    # Check for duplicate SKU
    for item in DATABASE["inventory"]:
        if item["sku"] == data["sku"]:
            return jsonify({"message": "SKU already exists"}), 400
    
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
    data = request.get_json(silent=True) or {}
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
    data = request.get_json(silent=True) or {}
    
    # Validate required fields
    if not data.get('customer_name') or not data.get('invoice_number'):
        return jsonify({"message": "Customer name and invoice number are required"}), 400
    
    # Check for duplicate invoice number
    for bill in DATABASE["billing"]:
        if bill["invoice_number"] == data["invoice_number"]:
            return jsonify({"message": "Invoice number already exists"}), 400
    
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
    data = request.get_json(silent=True) or {}
    status = data.get('status')
    
    if status not in ['Pending', 'Paid', 'Cancelled']:
        return jsonify({"message": "Invalid status"}), 400
    
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
    data = request.get_json(silent=True) or {}
    
    # Validate required fields
    if not data.get('title') or not data.get('content'):
        return jsonify({"message": "Title and content are required"}), 400
    
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
    data = request.get_json(silent=True) or {}
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

# HTML Template with Walmart-style design and full functionality
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Management System</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f1f1f1;
            color: #333;
        }
        
        .header {
            background-color: #0071ce;
            color: white;
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: bold;
        }
        
        .nav-buttons {
            display: flex;
            gap: 1rem;
        }
        
        .nav-btn {
            background: none;
            border: none;
            color: white;
            padding: 0.5rem 1rem;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        
        .nav-btn:hover {
            background-color: rgba(255,255,255,0.1);
        }
        
        .nav-btn.active {
            background-color: #ffa500;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 1rem;
        }
        
        .page {
            display: none;
        }
        
        .page.active {
            display: block;
        }
        
        .card {
            background: white;
            border-radius: 8px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .card-header {
            font-size: 1.25rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #0071ce;
            border-bottom: 2px solid #0071ce;
            padding-bottom: 0.5rem;
        }
        
        .form-group {
            margin-bottom: 1rem;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: bold;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 1rem;
        }
        
        .btn {
            background-color: #0071ce;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s;
        }
        
        .btn:hover {
            background-color: #0056b3;
        }
        
        .btn-danger {
            background-color: #dc3545;
        }
        
        .btn-danger:hover {
            background-color: #c82333;
        }
        
        .btn-success {
            background-color: #28a745;
        }
        
        .btn-success:hover {
            background-color: #218838;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        
        .table th,
        .table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        .table th {
            background-color: #f8f9fa;
            font-weight: bold;
            color: #0071ce;
        }
        
        .table tr:hover {
            background-color: #f8f9fa;
        }
        
        .status-badge {
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.875rem;
            font-weight: bold;
        }
        
        .status-in-stock {
            background-color: #d4edda;
            color: #155724;
        }
        
        .status-low-stock {
            background-color: #fff3cd;
            color: #856404;
        }
        
        .status-out-of-stock {
            background-color: #f8d7da;
            color: #721c24;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }
        
        .stat-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #0071ce;
        }
        
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #0071ce;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.875rem;
        }
        
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #0071ce, #004080);
        }
        
        .login-card {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            width: 100%;
            max-width: 400px;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-header h1 {
            color: #0071ce;
            margin-bottom: 0.5rem;
        }
        
        .error-message {
            background-color: #f8d7da;
            color: #721c24;
            padding: 0.75rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            border: 1px solid #f5c6cb;
        }
        
        .success-message {
            background-color: #d4edda;
            color: #155724;
            padding: 0.75rem;
            border-radius: 4px;
            margin-bottom: 1rem;
            border: 1px solid #c3e6cb;
        }
        
        .hidden {
            display: none;
        }
        
        .text-center {
            text-align: center;
        }
        
        .text-right {
            text-align: right;
        }
        
        .mb-1 {
            margin-bottom: 0.5rem;
        }
        
        .mb-2 {
            margin-bottom: 1rem;
        }
        
        .mb-3 {
            margin-bottom: 1.5rem;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 0 0.5rem;
            }
            
            .nav-buttons {
                flex-wrap: wrap;
            }
            
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }
            
            .table {
                font-size: 0.875rem;
            }
            
            .table th,
            .table td {
                padding: 0.5rem;
            }
        }
    </style>
</head>
<body>
    <div id="app">
        <!-- Login Page -->
        <div id="loginPage" class="page active">
            <div class="login-container">
                <div class="login-card">
                    <div class="login-header">
                        <h1>Inventory Management</h1>
                        <p>Sign in to manage your inventory</p>
                    </div>
                    
                    <div id="loginError" class="error-message hidden"></div>
                    <div id="loginSuccess" class="success-message hidden"></div>
                    
                    <form id="loginForm">
                        <div class="form-group">
                            <label for="email">User ID</label>
                            <input type="text" id="email" name="email" required placeholder="Enter your user ID">
                        </div>
                        
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input type="password" id="password" name="password" required placeholder="Enter your password">
                        </div>
                        
                        <button type="submit" class="btn" style="width: 100%;">
                            Sign In
                        </button>
                    </form>
                </div>
            </div>
        </div>
        
        <!-- Main Application -->
        <div id="mainApp" class="page hidden">
            <header class="header">
                <div class="logo">📦 Inventory Management</div>
                <div class="nav-buttons">
                    <button class="nav-btn active" onclick="showPage('dashboard')">Dashboard</button>
                    <button class="nav-btn" onclick="showPage('stock')">Stock List</button>
                    <button class="nav-btn" onclick="showPage('inventory')">Inventory</button>
                    <button class="nav-btn" onclick="showPage('billing')">Billing</button>
                    <button class="nav-btn" onclick="showPage('notes')">Notes</button>
                    <button class="nav-btn" onclick="logout()">Logout</button>
                </div>
            </header>
            
            <div class="container">
                <!-- Dashboard Page -->
                <div id="dashboardPage" class="page active">
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value" id="totalItems">0</div>
                            <div class="stat-label">Total Items</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="lowStock">0</div>
                            <div class="stat-label">Low Stock</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="outOfStock">0</div>
                            <div class="stat-label">Out of Stock</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="totalValue">₹0</div>
                            <div class="stat-label">Total Value</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="pendingBills">0</div>
                            <div class="stat-label">Pending Bills</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value" id="totalNotes">0</div>
                            <div class="stat-label">Total Notes</div>
                        </div>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">Quick Actions</div>
                        <div class="form-row">
                            <button class="btn" onclick="showPage('inventory')">Add Item</button>
                            <button class="btn" onclick="showPage('billing')">Create Invoice</button>
                            <button class="btn" onclick="showPage('notes')">Add Note</button>
                            <button class="btn" onclick="showPage('stock')">View Stock</button>
                        </div>
                    </div>
                </div>
                
                <!-- Stock List Page -->
                <div id="stockPage" class="page">
                    <div class="card">
                        <div class="card-header">Stock List</div>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>SKU</th>
                                    <th>Category</th>
                                    <th>Quantity</th>
                                    <th>Min Stock</th>
                                    <th>Price (₹)</th>
                                    <th>Status</th>
                                    <th>Total Value (₹)</th>
                                </tr>
                            </thead>
                            <tbody id="stockTableBody">
                                <tr>
                                    <td colspan="8" class="text-center">No stock items available</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Inventory Management Page -->
                <div id="inventoryPage" class="page">
                    <div class="card">
                        <div class="card-header">Add/Edit Item</div>
                        <form id="inventoryForm">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Name *</label>
                                    <input type="text" name="name" required>
                                </div>
                                <div class="form-group">
                                    <label>SKU *</label>
                                    <input type="text" name="sku" required>
                                </div>
                                <div class="form-group">
                                    <label>Category *</label>
                                    <select name="category" required>
                                        <option value="">Select Category</option>
                                        <option value="Electronics">Electronics</option>
                                        <option value="Clothing">Clothing</option>
                                        <option value="Food">Food</option>
                                        <option value="Books">Books</option>
                                        <option value="Other">Other</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label>Quantity *</label>
                                    <input type="number" name="quantity" required min="0">
                                </div>
                                <div class="form-group">
                                    <label>Min Stock Level *</label>
                                    <input type="number" name="min_stock_level" required min="0">
                                </div>
                                <div class="form-group">
                                    <label>Unit Price (₹) *</label>
                                    <input type="number" name="unit_price" required min="0" step="0.01">
                                </div>
                                <div class="form-group">
                                    <label>Supplier</label>
                                    <input type="text" name="supplier">
                                </div>
                                <div class="form-group">
                                    <label>Location</label>
                                    <input type="text" name="location">
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Description</label>
                                <textarea name="description" rows="3"></textarea>
                            </div>
                            <div style="display: flex; gap: 1rem;">
                                <button type="submit" class="btn">Save Item</button>
                                <button type="button" class="btn" onclick="resetInventoryForm()">Clear</button>
                            </div>
                        </form>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">Inventory Items</div>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>SKU</th>
                                    <th>Category</th>
                                    <th>Quantity</th>
                                    <th>Price (₹)</th>
                                    <th>Status</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="inventoryTableBody">
                                <tr>
                                    <td colspan="7" class="text-center">No inventory items available</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Billing Page -->
                <div id="billingPage" class="page">
                    <div class="card">
                        <div class="card-header">Create Invoice</div>
                        <form id="billingForm">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Customer Name *</label>
                                    <input type="text" name="customer_name" required>
                                </div>
                                <div class="form-group">
                                    <label>Invoice Number *</label>
                                    <input type="text" name="invoice_number" required>
                                </div>
                                <div class="form-group">
                                    <label>Due Date *</label>
                                    <input type="date" name="due_date" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Items</label>
                                <div id="billingItems">
                                    <div class="billing-item-row">
                                        <input type="text" placeholder="Item name" class="item-name" required>
                                        <input type="number" placeholder="Quantity" class="item-quantity" min="1" required>
                                        <input type="number" placeholder="Price (₹)" class="item-price" min="0" step="0.01" required>
                                        <input type="text" placeholder="SKU" class="item-sku">
                                        <button type="button" class="btn btn-danger" onclick="removeBillingItem(this)">Remove</button>
                                    </div>
                                </div>
                                <button type="button" class="btn" onclick="addBillingItem()">Add Item</button>
                            </div>
                            <div class="form-group">
                                <label>Total Amount: ₹<span id="totalAmount">0.00</span></label>
                            </div>
                            <button type="submit" class="btn">Create Invoice</button>
                        </form>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">Invoices</div>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Invoice #</th>
                                    <th>Customer</th>
                                    <th>Amount (₹)</th>
                                    <th>Status</th>
                                    <th>Due Date</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="billingTableBody">
                                <tr>
                                    <td colspan="6" class="text-center">No invoices available</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Notes Page -->
                <div id="notesPage" class="page">
                    <div class="card">
                        <div class="card-header">Add Note</div>
                        <form id="notesForm">
                            <div class="form-row">
                                <div class="form-group">
                                    <label>Title *</label>
                                    <input type="text" name="title" required>
                                </div>
                                <div class="form-group">
                                    <label>Category *</label>
                                    <select name="category" required>
                                        <option value="">Select Category</option>
                                        <option value="General">General</option>
                                        <option value="Important">Important</option>
                                        <option value="Meeting">Meeting</option>
                                        <option value="Task">Task</option>
                                        <option value="Reminder">Reminder</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group">
                                <label>Content *</label>
                                <textarea name="content" rows="4" required></textarea>
                            </div>
                            <button type="submit" class="btn">Save Note</button>
                        </form>
                    </div>
                    
                    <div class="card">
                        <div class="card-header">Notes</div>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Category</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="notesTableBody">
                                <tr>
                                    <td colspan="4" class="text-center">No notes available</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let authToken = null;
        let currentUser = null;
        
        // Login functionality
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const loginData = {
                email: formData.get('email'),
                password: formData.get('password')
            };
            
            try {
                const response = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(loginData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    authToken = result.access_token;
                    currentUser = result.user;
                    localStorage.setItem('token', authToken);
                    document.getElementById('loginPage').classList.remove('active');
                    document.getElementById('mainApp').classList.add('active');
                    showSuccess('Login successful!');
                    loadDashboard();
                } else {
                    showError('loginError', result.message || 'Login failed');
                }
            } catch (error) {
                showError('loginError', 'Network error. Please try again.');
            }
        });
        
        // Logout functionality
        function logout() {
            authToken = null;
            currentUser = null;
            localStorage.removeItem('token');
            document.getElementById('mainApp').classList.remove('active');
            document.getElementById('loginPage').classList.add('active');
            document.getElementById('loginForm').reset();
            hideError('loginError');
        }
        
        // Page navigation
        function showPage(pageName) {
            document.querySelectorAll('.page').forEach(page => {
                page.classList.remove('active');
            });
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            document.getElementById(pageName + 'Page').classList.add('active');
            event.target.classList.add('active');
            
            // Load data for specific pages
            if (pageName === 'dashboard') loadDashboard();
            if (pageName === 'stock') loadStock();
            if (pageName === 'inventory') loadInventory();
            if (pageName === 'billing') loadBilling();
            if (pageName === 'notes') loadNotes();
        }
        
        // Error and success message functions
        function showError(elementId, message) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.classList.remove('hidden');
            setTimeout(() => {
                element.classList.add('hidden');
            }, 5000);
        }
        
        function showSuccess(message) {
            const element = document.getElementById('loginSuccess');
            element.textContent = message;
            element.classList.remove('hidden');
            setTimeout(() => {
                element.classList.add('hidden');
            }, 3000);
        }
        
        function hideError(elementId) {
            document.getElementById(elementId).classList.add('hidden');
        }
        
        // API helper functions
        async function apiCall(endpoint, method = 'GET', data = null) {
            const options = {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                }
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            const response = await fetch(endpoint, options);
            
            if (response.status === 401) {
                logout();
                return null;
            }
            
            return response.json();
        }
        
        // Load dashboard data
        async function loadDashboard() {
            const stats = await apiCall('/api/dashboard');
            if (stats) {
                document.getElementById('totalItems').textContent = stats.total_items;
                document.getElementById('lowStock').textContent = stats.low_stock;
                document.getElementById('outOfStock').textContent = stats.out_of_stock;
                document.getElementById('totalValue').textContent = `₹${stats.total_value.toFixed(2)}`;
                document.getElementById('pendingBills').textContent = stats.pending_bills;
                document.getElementById('totalNotes').textContent = stats.total_notes;
            }
        }
        
        // Load stock data
        async function loadStock() {
            const stock = await apiCall('/api/stock');
            if (stock) {
                const tbody = document.getElementById('stockTableBody');
                tbody.innerHTML = '';
                
                if (stock.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" class="text-center">No stock items available</td></tr>';
                    return;
                }
                
                stock.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.name}</td>
                        <td>${item.sku}</td>
                        <td>${item.category}</td>
                        <td>${item.quantity}</td>
                        <td>${item.min_stock_level}</td>
                        <td>₹${item.unit_price.toFixed(2)}</td>
                        <td><span class="status-badge status-${item.status.toLowerCase().replace(' ', '-')}">${item.status}</span></td>
                        <td>₹${(item.quantity * item.unit_price).toFixed(2)}</td>
                    `;
                    tbody.appendChild(row);
                });
            }
        }
        
        // Load inventory data
        async function loadInventory() {
            const inventory = await apiCall('/api/inventory');
            if (inventory) {
                const tbody = document.getElementById('inventoryTableBody');
                tbody.innerHTML = '';
                
                if (inventory.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" class="text-center">No inventory items available</td></tr>';
                    return;
                }
                
                inventory.forEach(item => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${item.name}</td>
                        <td>${item.sku}</td>
                        <td>${item.category}</td>
                        <td>${item.quantity}</td>
                        <td>₹${item.unit_price.toFixed(2)}</td>
                        <td><span class="status-badge status-${item.status.toLowerCase().replace(' ', '-')}">${item.status}</span></td>
                        <td>
                            <button class="btn btn-danger" onclick="deleteInventoryItem('${item.id}')">Delete</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            }
        }
        
        // Load billing data
        async function loadBilling() {
            const billing = await apiCall('/api/billing');
            if (billing) {
                const tbody = document.getElementById('billingTableBody');
                tbody.innerHTML = '';
                
                if (billing.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="text-center">No invoices available</td></tr>';
                    return;
                }
                
                billing.forEach(bill => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${bill.invoice_number}</td>
                        <td>${bill.customer_name}</td>
                        <td>₹${bill.total_amount.toFixed(2)}</td>
                        <td><span class="status-badge status-${bill.status.toLowerCase()}">${bill.status}</span></td>
                        <td>${bill.due_date}</td>
                        <td>
                            ${bill.status === 'Pending' ? `<button class="btn btn-success" onclick="updateBillStatus('${bill.id}', 'Paid')">Mark Paid</button>` : ''}
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            }
        }
        
        // Load notes data
        async function loadNotes() {
            const notes = await apiCall('/api/notes');
            if (notes) {
                const tbody = document.getElementById('notesTableBody');
                tbody.innerHTML = '';
                
                if (notes.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4" class="text-center">No notes available</td></tr>';
                    return;
                }
                
                notes.forEach(note => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${note.title}</td>
                        <td>${note.category}</td>
                        <td>${new Date(note.created_at).toLocaleDateString()}</td>
                        <td>
                            <button class="btn btn-danger" onclick="deleteNote('${note.id}')">Delete</button>
                        </td>
                    `;
                    tbody.appendChild(row);
                });
            }
        }
        
        // Inventory form handling
        document.getElementById('inventoryForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            const result = await apiCall('/api/inventory', 'POST', data);
            if (result) {
                resetInventoryForm();
                loadInventory();
                loadDashboard();
                showSuccess('Item added successfully!');
            }
        });
        
        function resetInventoryForm() {
            document.getElementById('inventoryForm').reset();
        }
        
        async function deleteInventoryItem(itemId) {
            if (confirm('Are you sure you want to delete this item?')) {
                const result = await apiCall(`/api/inventory/${itemId}`, 'DELETE');
                if (result) {
                    loadInventory();
                    loadDashboard();
                    showSuccess('Item deleted successfully!');
                }
            }
        }
        
        // Billing form handling
        document.getElementById('billingForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            // Get items from the form
            const items = [];
            const itemElements = document.querySelectorAll('.billing-item-row');
            itemElements.forEach(element => {
                const name = element.querySelector('.item-name').value;
                const quantity = parseInt(element.querySelector('.item-quantity').value);
                const price = parseFloat(element.querySelector('.item-price').value);
                const sku = element.querySelector('.item-sku').value;
                
                if (name && quantity && price) {
                    items.push({ name, quantity, price, sku });
                }
            });
            
            if (items.length === 0) {
                alert('Please add at least one item to the invoice');
                return;
            }
            
            data.items = items;
            data.total_amount = items.reduce((sum, item) => sum + (item.quantity * item.price), 0);
            
            const result = await apiCall('/api/billing', 'POST', data);
            if (result) {
                e.target.reset();
                resetBillingItems();
                loadBilling();
                loadDashboard();
                showSuccess('Invoice created successfully!');
            }
        });
        
        function addBillingItem() {
            const container = document.getElementById('billingItems');
            const newItem = document.createElement('div');
            newItem.className = 'billing-item-row';
            newItem.innerHTML = `
                <input type="text" placeholder="Item name" class="item-name" required>
                <input type="number" placeholder="Quantity" class="item-quantity" min="1" required>
                <input type="number" placeholder="Price (₹)" class="item-price" min="0" step="0.01" required>
                <input type="text" placeholder="SKU" class="item-sku">
                <button type="button" class="btn btn-danger" onclick="removeBillingItem(this)">Remove</button>
            `;
            container.appendChild(newItem);
            
            // Add event listeners to update total
            newItem.querySelectorAll('input').forEach(input => {
                input.addEventListener('input', updateBillingTotal);
            });
        }
        
        function removeBillingItem(button) {
            const container = document.getElementById('billingItems');
            if (container.children.length > 1) {
                button.parentElement.remove();
                updateBillingTotal();
            } else {
                alert('You must have at least one item');
            }
        }
        
        function updateBillingTotal() {
            const items = document.querySelectorAll('.billing-item-row');
            let total = 0;
            
            items.forEach(item => {
                const quantity = parseInt(item.querySelector('.item-quantity').value) || 0;
                const price = parseFloat(item.querySelector('.item-price').value) || 0;
                total += quantity * price;
            });
            
            document.getElementById('totalAmount').textContent = total.toFixed(2);
        }
        
        function resetBillingItems() {
            const container = document.getElementById('billingItems');
            container.innerHTML = `
                <div class="billing-item-row">
                    <input type="text" placeholder="Item name" class="item-name" required>
                    <input type="number" placeholder="Quantity" class="item-quantity" min="1" required>
                    <input type="number" placeholder="Price (₹)" class="item-price" min="0" step="0.01" required>
                    <input type="text" placeholder="SKU" class="item-sku">
                    <button type="button" class="btn btn-danger" onclick="removeBillingItem(this)">Remove</button>
                </div>
            `;
            updateBillingTotal();
        }
        
        async function updateBillStatus(billId, status) {
            const result = await apiCall(`/api/billing/${billId}/status`, 'PUT', { status });
            if (result) {
                loadBilling();
                loadDashboard();
                showSuccess('Bill status updated successfully!');
            }
        }
        
        // Notes form handling
        document.getElementById('notesForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData.entries());
            
            const result = await apiCall('/api/notes', 'POST', data);
            if (result) {
                e.target.reset();
                loadNotes();
                loadDashboard();
                showSuccess('Note added successfully!');
            }
        });
        
        async function deleteNote(noteId) {
            if (confirm('Are you sure you want to delete this note?')) {
                const result = await apiCall(`/api/notes/${noteId}`, 'DELETE');
                if (result) {
                    loadNotes();
                    loadDashboard();
                    showSuccess('Note deleted successfully!');
                }
            }
        }
        
        // Check for existing token on page load
        window.addEventListener('load', () => {
            const token = localStorage.getItem('token');
            if (token) {
                authToken = token;
                document.getElementById('loginPage').classList.remove('active');
                document.getElementById('mainApp').classList.add('active');
                loadDashboard();
            }
        });
        
        // Add event listeners for billing total calculation
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('#billingItems input').forEach(input => {
                input.addEventListener('input', updateBillingTotal);
            });
        });
    </script>
    
    <style>
        .billing-item-row {
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr auto;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            align-items: center;
        }
        
        .billing-item-row input {
            padding: 0.5rem;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        
        .billing-item-row .btn {
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
        }
    </style>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "database": "In-Memory Demo",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    app.run(debug=True)

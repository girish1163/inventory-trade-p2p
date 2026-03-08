from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import uuid
import os

app = Flask(__name__)
CORS(app, origins=["*"])

# Simple in-memory database (will work on Vercel)
inventory_items = []
billing_items = []
notes_items = []

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inventory Management System</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f5f5f5; }
        .header { background: #0071ce; color: white; padding: 1rem; text-align: center; }
        .container { max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }
        .card { background: white; padding: 2rem; margin-bottom: 2rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .nav { display: flex; gap: 1rem; margin-bottom: 2rem; justify-content: center; }
        .nav button { padding: 1rem 2rem; background: #0071ce; color: white; border: none; border-radius: 4px; cursor: pointer; }
        .nav button.active { background: #ffa500; }
        .page { display: none; }
        .page.active { display: block; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
        .form-group input, .form-group select, .form-group textarea { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; }
        .btn { background: #0071ce; color: white; padding: 0.75rem 1.5rem; border: none; border-radius: 4px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .btn-danger { background: #dc3545; }
        .table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        .table th, .table td { padding: 0.75rem; text-align: left; border-bottom: 1px solid #ddd; }
        .table th { background: #f8f9fa; font-weight: bold; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .stat-card { background: white; padding: 1.5rem; text-align: center; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .stat-value { font-size: 2rem; font-weight: bold; color: #0071ce; }
        .login-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background: linear-gradient(135deg, #0071ce, #004080); }
        .login-card { background: white; padding: 2rem; border-radius: 8px; width: 100%; max-width: 400px; }
        .hidden { display: none; }
        .error { background: #f8d7da; color: #721c24; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .success { background: #d4edda; color: #155724; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .billing-item { display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 0.5rem; margin-bottom: 0.5rem; }
    </style>
</head>
<body>
    <div id="app">
        <!-- Login Page -->
        <div id="loginPage" class="page active">
            <div class="login-container">
                <div class="login-card">
                    <h2 style="text-align: center; color: #0071ce; margin-bottom: 2rem;">Inventory Management</h2>
                    <div id="loginError" class="error hidden"></div>
                    <form id="loginForm">
                        <div class="form-group">
                            <label>User ID</label>
                            <input type="text" id="email" required placeholder="Enter user ID">
                        </div>
                        <div class="form-group">
                            <label>Password</label>
                            <input type="password" id="password" required placeholder="Enter password">
                        </div>
                        <button type="submit" class="btn" style="width: 100%;">Login</button>
                    </form>
                </div>
            </div>
        </div>
        
        <!-- Main App -->
        <div id="mainApp" class="page hidden">
            <div class="header">
                <h1>📦 Inventory Management System</h1>
            </div>
            
            <div class="container">
                <div class="nav">
                    <button class="nav-btn active" onclick="showPage('dashboard')">Dashboard</button>
                    <button class="nav-btn" onclick="showPage('inventory')">Add Product</button>
                    <button class="nav-btn" onclick="showPage('billing')">Billing</button>
                    <button class="nav-btn" onclick="showPage('notes')">Notes</button>
                    <button class="nav-btn" onclick="logout()">Logout</button>
                </div>
                
                <!-- Dashboard -->
                <div id="dashboardPage" class="page active">
                    <div class="card">
                        <div class="stats">
                            <div class="stat-card">
                                <div class="stat-value" id="totalItems">0</div>
                                <div>Total Products</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value" id="totalBills">0</div>
                                <div>Total Bills</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value" id="totalNotes">0</div>
                                <div>Total Notes</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-value" id="totalValue">₹0</div>
                                <div>Total Value</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Inventory -->
                <div id="inventoryPage" class="page">
                    <div class="card">
                        <h2>Add Product</h2>
                        <div id="inventorySuccess" class="success hidden"></div>
                        <form id="inventoryForm">
                            <div class="form-group">
                                <label>Product Name *</label>
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
                                <label>Price (₹) *</label>
                                <input type="number" name="price" required min="0" step="0.01">
                            </div>
                            <button type="submit" class="btn">Add Product</button>
                        </form>
                        
                        <h3 style="margin-top: 2rem;">Products List</h3>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Name</th>
                                    <th>SKU</th>
                                    <th>Category</th>
                                    <th>Quantity</th>
                                    <th>Price (₹)</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="inventoryList">
                                <tr><td colspan="6" style="text-align: center;">No products added yet</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Billing -->
                <div id="billingPage" class="page">
                    <div class="card">
                        <h2>Create Invoice</h2>
                        <div id="billingSuccess" class="success hidden"></div>
                        <form id="billingForm">
                            <div class="form-group">
                                <label>Customer Name *</label>
                                <input type="text" name="customer_name" required>
                            </div>
                            <div class="form-group">
                                <label>Invoice Number *</label>
                                <input type="text" name="invoice_number" required>
                            </div>
                            <div class="form-group">
                                <label>Items</label>
                                <div id="billingItems">
                                    <div class="billing-item">
                                        <input type="text" placeholder="Item name" class="item-name" required>
                                        <input type="number" placeholder="Quantity" class="item-quantity" min="1" required>
                                        <input type="number" placeholder="Price (₹)" class="item-price" min="0" step="0.01" required>
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
                        
                        <h3 style="margin-top: 2rem;">Invoices</h3>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Invoice #</th>
                                    <th>Customer</th>
                                    <th>Amount (₹)</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody id="billingList">
                                <tr><td colspan="4" style="text-align: center;">No invoices created yet</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <!-- Notes -->
                <div id="notesPage" class="page">
                    <div class="card">
                        <h2>Add Note</h2>
                        <div id="notesSuccess" class="success hidden"></div>
                        <form id="notesForm">
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
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Content *</label>
                                <textarea name="content" rows="4" required></textarea>
                            </div>
                            <button type="submit" class="btn">Add Note</button>
                        </form>
                        
                        <h3 style="margin-top: 2rem;">Notes List</h3>
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Title</th>
                                    <th>Category</th>
                                    <th>Created</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody id="notesList">
                                <tr><td colspan="4" style="text-align: center;">No notes added yet</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let isLoggedIn = false;
        let inventory = [];
        let billing = [];
        let notes = [];
        
        // Login
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if ((email === '743663' || email === 'admin@inventory.com') && password === 'girish7890@A') {
                isLoggedIn = true;
                document.getElementById('loginPage').classList.remove('active');
                document.getElementById('mainApp').classList.add('active');
                loadDashboard();
                updateInventoryList();
                updateBillingList();
                updateNotesList();
            } else {
                document.getElementById('loginError').textContent = 'Invalid credentials';
                document.getElementById('loginError').classList.remove('hidden');
            }
        });
        
        function logout() {
            isLoggedIn = false;
            document.getElementById('mainApp').classList.remove('active');
            document.getElementById('loginPage').classList.add('active');
            document.getElementById('loginForm').reset();
        }
        
        function showPage(pageName) {
            document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(pageName + 'Page').classList.add('active');
            event.target.classList.add('active');
        }
        
        function showSuccess(elementId, message) {
            const element = document.getElementById(elementId);
            element.textContent = message;
            element.classList.remove('hidden');
            setTimeout(() => element.classList.add('hidden'), 3000);
        }
        
        function loadDashboard() {
            document.getElementById('totalItems').textContent = inventory.length;
            document.getElementById('totalBills').textContent = billing.length;
            document.getElementById('totalNotes').textContent = notes.length;
            
            const totalValue = inventory.reduce((sum, item) => sum + (item.quantity * item.price), 0);
            document.getElementById('totalValue').textContent = '₹' + totalValue.toFixed(2);
        }
        
        function updateInventoryList() {
            const tbody = document.getElementById('inventoryList');
            tbody.innerHTML = '';
            
            if (inventory.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center;">No products added yet</td></tr>';
                return;
            }
            
            inventory.forEach(item => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${item.name}</td>
                    <td>${item.sku}</td>
                    <td>${item.category}</td>
                    <td>${item.quantity}</td>
                    <td>₹${item.price.toFixed(2)}</td>
                    <td><button class="btn btn-danger" onclick="deleteInventory('${item.id}')">Delete</button></td>
                `;
            });
        }
        
        function updateBillingList() {
            const tbody = document.getElementById('billingList');
            tbody.innerHTML = '';
            
            if (billing.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No invoices created yet</td></tr>';
                return;
            }
            
            billing.forEach(bill => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${bill.invoice_number}</td>
                    <td>${bill.customer_name}</td>
                    <td>₹${bill.total_amount.toFixed(2)}</td>
                    <td>${bill.status}</td>
                `;
            });
        }
        
        function updateNotesList() {
            const tbody = document.getElementById('notesList');
            tbody.innerHTML = '';
            
            if (notes.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No notes added yet</td></tr>';
                return;
            }
            
            notes.forEach(note => {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${note.title}</td>
                    <td>${note.category}</td>
                    <td>${new Date().toLocaleDateString()}</td>
                    <td><button class="btn btn-danger" onclick="deleteNote('${note.id}')">Delete</button></td>
                `;
            });
        }
        
        // Inventory Form
        document.getElementById('inventoryForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            const item = {
                id: Date.now().toString(),
                name: formData.get('name'),
                sku: formData.get('sku'),
                category: formData.get('category'),
                quantity: parseInt(formData.get('quantity')),
                price: parseFloat(formData.get('price'))
            };
            
            inventory.push(item);
            updateInventoryList();
            loadDashboard();
            e.target.reset();
            showSuccess('inventorySuccess', 'Product added successfully!');
        });
        
        function deleteInventory(id) {
            inventory = inventory.filter(item => item.id !== id);
            updateInventoryList();
            loadDashboard();
        }
        
        // Billing Form
        function addBillingItem() {
            const container = document.getElementById('billingItems');
            const newItem = document.createElement('div');
            newItem.className = 'billing-item';
            newItem.innerHTML = `
                <input type="text" placeholder="Item name" class="item-name" required>
                <input type="number" placeholder="Quantity" class="item-quantity" min="1" required>
                <input type="number" placeholder="Price (₹)" class="item-price" min="0" step="0.01" required>
                <button type="button" class="btn btn-danger" onclick="removeBillingItem(this)">Remove</button>
            `;
            container.appendChild(newItem);
            
            newItem.querySelectorAll('input').forEach(input => {
                input.addEventListener('input', updateBillingTotal);
            });
        }
        
        function removeBillingItem(button) {
            const container = document.getElementById('billingItems');
            if (container.children.length > 1) {
                button.parentElement.remove();
                updateBillingTotal();
            }
        }
        
        function updateBillingTotal() {
            const items = document.querySelectorAll('.billing-item');
            let total = 0;
            
            items.forEach(item => {
                const quantity = parseInt(item.querySelector('.item-quantity').value) || 0;
                const price = parseFloat(item.querySelector('.item-price').value) || 0;
                total += quantity * price;
            });
            
            document.getElementById('totalAmount').textContent = total.toFixed(2);
        }
        
        document.getElementById('billingForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const items = [];
            document.querySelectorAll('.billing-item').forEach(itemRow => {
                const name = itemRow.querySelector('.item-name').value;
                const quantity = parseInt(itemRow.querySelector('.item-quantity').value);
                const price = parseFloat(itemRow.querySelector('.item-price').value);
                
                if (name && quantity && price) {
                    items.push({ name, quantity, price });
                }
            });
            
            const bill = {
                id: Date.now().toString(),
                customer_name: formData.get('customer_name'),
                invoice_number: formData.get('invoice_number'),
                items: items,
                total_amount: items.reduce((sum, item) => sum + (item.quantity * item.price), 0),
                status: 'Pending'
            };
            
            billing.push(bill);
            updateBillingList();
            loadDashboard();
            e.target.reset();
            
            // Reset billing items
            document.getElementById('billingItems').innerHTML = `
                <div class="billing-item">
                    <input type="text" placeholder="Item name" class="item-name" required>
                    <input type="number" placeholder="Quantity" class="item-quantity" min="1" required>
                    <input type="number" placeholder="Price (₹)" class="item-price" min="0" step="0.01" required>
                    <button type="button" class="btn btn-danger" onclick="removeBillingItem(this)">Remove</button>
                </div>
            `;
            updateBillingTotal();
            showSuccess('billingSuccess', 'Invoice created successfully!');
        });
        
        // Notes Form
        document.getElementById('notesForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const note = {
                id: Date.now().toString(),
                title: formData.get('title'),
                category: formData.get('category'),
                content: formData.get('content'),
                created_at: new Date().toISOString()
            };
            
            notes.push(note);
            updateNotesList();
            loadDashboard();
            e.target.reset();
            showSuccess('notesSuccess', 'Note added successfully!');
        });
        
        function deleteNote(id) {
            notes = notes.filter(note => note.id !== id);
            updateNotesList();
            loadDashboard();
        }
        
        // Make functions global
        window.deleteInventory = deleteInventory;
        window.deleteNote = deleteNote;
        window.addBillingItem = addBillingItem;
        window.removeBillingItem = removeBillingItem;
        window.updateBillingTotal = updateBillingTotal;
        window.showPage = showPage;
        window.logout = logout;
        
        // Initialize billing total calculation
        document.addEventListener('DOMContentLoaded', function() {
            document.querySelectorAll('#billingItems input').forEach(input => {
                input.addEventListener('input', updateBillingTotal);
            });
        });
    </script>
</body>
</html>
''')

@app.route('/health')
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True)

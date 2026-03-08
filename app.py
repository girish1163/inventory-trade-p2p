from flask import Flask, render_template_string
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Inventory Management</title>
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
                    <form onsubmit="handleLogin(event)">
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
                    <button class="nav-btn" onclick="handleLogout()">Logout</button>
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
                                <input type="text" id="productName" required>
                            </div>
                            <div class="form-group">
                                <label>SKU *</label>
                                <input type="text" id="productSku" required>
                            </div>
                            <div class="form-group">
                                <label>Category *</label>
                                <select id="productCategory" required>
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
                                <input type="number" id="productQuantity" required min="0">
                            </div>
                            <div class="form-group">
                                <label>Price (₹) *</label>
                                <input type="number" id="productPrice" required min="0" step="0.01">
                            </div>
                            <button type="button" class="btn" onclick="addProduct()">Add Product</button>
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
                                <input type="text" id="customerName" required>
                            </div>
                            <div class="form-group">
                                <label>Invoice Number *</label>
                                <input type="text" id="invoiceNumber" required>
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
                            <button type="button" class="btn" onclick="createInvoice()">Create Invoice</button>
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
                        <form onsubmit="handleAddNote(event)">
                            <div class="form-group">
                                <label>Title *</label>
                                <input type="text" id="noteTitle" required>
                            </div>
                            <div class="form-group">
                                <label>Category *</label>
                                <select id="noteCategory" required>
                                    <option value="">Select Category</option>
                                    <option value="General">General</option>
                                    <option value="Important">Important</option>
                                    <option value="Meeting">Meeting</option>
                                    <option value="Task">Task</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Content *</label>
                                <textarea id="noteContent" rows="4" required></textarea>
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
        let inventory = [];
        let billing = [];
        let notes = [];
        
        function handleLogin(event) {
            event.preventDefault();
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            if ((email === '743663' || email === 'admin@inventory.com') && password === 'girish7890@A') {
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
        }
        
        function handleLogout() {
            document.getElementById('mainApp').classList.remove('active');
            document.getElementById('loginPage').classList.add('active');
            document.getElementById('email').value = '';
            document.getElementById('password').value = '';
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
                row.innerHTML = '<td>' + item.name + '</td><td>' + item.sku + '</td><td>' + item.category + '</td><td>' + item.quantity + '</td><td>₹' + item.price.toFixed(2) + '</td><td><button class="btn btn-danger" onclick="deleteInventory(\\'' + item.id + '\\')">Delete</button></td>';
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
                row.innerHTML = '<td>' + bill.invoice_number + '</td><td>' + bill.customer_name + '</td><td>₹' + bill.total_amount.toFixed(2) + '</td><td>' + bill.status + '</td>';
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
                row.innerHTML = '<td>' + note.title + '</td><td>' + note.category + '</td><td>' + new Date().toLocaleDateString() + '</td><td><button class="btn btn-danger" onclick="deleteNote(\\'' + note.id + '\\')">Delete</button></td>';
            });
        }
        
        function addProduct() {
            const name = document.getElementById('productName').value;
            const sku = document.getElementById('productSku').value;
            const category = document.getElementById('productCategory').value;
            const quantity = document.getElementById('productQuantity').value;
            const price = document.getElementById('productPrice').value;
            
            if (!name || !sku || !category || !quantity || !price) {
                alert('Please fill all required fields');
                return;
            }
            
            const item = {
                id: Date.now().toString(),
                name: name,
                sku: sku,
                category: category,
                quantity: parseInt(quantity),
                price: parseFloat(price)
            };
            
            inventory.push(item);
            updateInventoryList();
            loadDashboard();
            
            // Reset form
            document.getElementById('productName').value = '';
            document.getElementById('productSku').value = '';
            document.getElementById('productCategory').value = '';
            document.getElementById('productQuantity').value = '';
            document.getElementById('productPrice').value = '';
            
            showSuccess('inventorySuccess', 'Product added successfully!');
        }
        
        function createInvoice() {
            const customerName = document.getElementById('customerName').value;
            const invoiceNumber = document.getElementById('invoiceNumber').value;
            
            if (!customerName || !invoiceNumber) {
                alert('Please fill all required fields');
                return;
            }
            
            const items = [];
            document.querySelectorAll('.billing-item').forEach(itemRow => {
                const name = itemRow.querySelector('.item-name').value;
                const quantity = parseInt(itemRow.querySelector('.item-quantity').value);
                const price = parseFloat(itemRow.querySelector('.item-price').value);
                
                if (name && quantity && price) {
                    items.push({ name, quantity, price });
                }
            });
            
            if (items.length === 0) {
                alert('Please add at least one item');
                return;
            }
            
            const bill = {
                id: Date.now().toString(),
                customer_name: customerName,
                invoice_number: invoiceNumber,
                items: items,
                total_amount: items.reduce((sum, item) => sum + (item.quantity * item.price), 0),
                status: 'Pending'
            };
            
            billing.push(bill);
            updateBillingList();
            loadDashboard();
            
            // Reset form
            document.getElementById('customerName').value = '';
            document.getElementById('invoiceNumber').value = '';
            document.getElementById('billingItems').innerHTML = '<div class="billing-item"><input type="text" placeholder="Item name" class="item-name" required><input type="number" placeholder="Quantity" class="item-quantity" min="1" required><input type="number" placeholder="Price (₹)" class="item-price" min="0" step="0.01" required><button type="button" class="btn btn-danger" onclick="removeBillingItem(this)">Remove</button></div>';
            updateBillingTotal();
            
            showSuccess('billingSuccess', 'Invoice created successfully!');
        }
        
        function deleteInventory(id) {
            inventory = inventory.filter(item => item.id !== id);
            updateInventoryList();
            loadDashboard();
        }
        
        function addBillingItem() {
            const container = document.getElementById('billingItems');
            const newItem = document.createElement('div');
            newItem.className = 'billing-item';
            newItem.innerHTML = '<input type="text" placeholder="Item name" class="item-name" required><input type="number" placeholder="Quantity" class="item-quantity" min="1" required><input type="number" placeholder="Price (₹)" class="item-price" min="0" step="0.01" required><button type="button" class="btn btn-danger" onclick="removeBillingItem(this)">Remove</button>';
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
        
        function handleCreateInvoice(event) {
            event.preventDefault();
        }
        
        function handleAddNote(event) {
            event.preventDefault();
            
            const note = {
                id: Date.now().toString(),
                title: document.getElementById('noteTitle').value,
                category: document.getElementById('noteCategory').value,
                content: document.getElementById('noteContent').value,
                created_at: new Date().toISOString()
            };
            
            notes.push(note);
            updateNotesList();
            loadDashboard();
            
            // Reset form
            document.getElementById('noteTitle').value = '';
            document.getElementById('noteCategory').value = '';
            document.getElementById('noteContent').value = '';
            
            showSuccess('notesSuccess', 'Note added successfully!');
        }
        
        function deleteNote(id) {
            notes = notes.filter(note => note.id !== id);
            updateNotesList();
            loadDashboard();
        }
        
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
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

if __name__ == '__main__':
    app.run(debug=True)

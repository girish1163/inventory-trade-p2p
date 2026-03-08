# Inventory Management System

A comprehensive inventory management software built with FastAPI, MongoDB, and React.

## Features

- User authentication with default credentials
- Real-time inventory tracking with MongoDB
- Stock level monitoring and alerts
- Complete CRUD operations for inventory items
- Transaction history and audit trail
- Dashboard with statistics
- Search and filter capabilities
- Responsive React frontend

## Default Credentials

- **User ID**: 743663
- **Password**: girish7890@A

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Frontend**: React.js
- **Authentication**: JWT
- **ODM**: Motor (Async MongoDB Driver)

## Installation

### Prerequisites

1. Python 3.8+
2. Node.js 14+
3. MongoDB running on localhost:27017

### Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
# Copy .env file and update if needed
cp .env.example .env
```

3. Start MongoDB (if not already running):
```bash
mongod
```

4. Run the FastAPI server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to client directory:
```bash
cd client
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the React development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## API Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation.

### Authentication Endpoints

- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/verify` - Verify JWT token
- `GET /api/auth/me` - Get current user info

### Inventory Endpoints

- `GET /api/inventory` - Get all inventory items (with filtering)
- `GET /api/inventory/{id}` - Get specific item
- `POST /api/inventory` - Create new item
- `PUT /api/inventory/{id}` - Update item
- `DELETE /api/inventory/{id}` - Delete item
- `POST /api/inventory/{id}/stock` - Update stock levels
- `GET /api/inventory/{id}/transactions` - Get item transactions
- `GET /api/inventory/alerts/low-stock` - Get low stock alerts

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string",
  "password_hash": "string",
  "role": "string",
  "created_at": "datetime"
}
```

### Inventory Items Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "sku": "string",
  "description": "string",
  "category": "string",
  "quantity": "number",
  "min_stock_level": "number",
  "max_stock_level": "number",
  "unit_price": "number",
  "supplier": "string",
  "location": "string",
  "status": "string",
  "created_at": "datetime",
  "last_updated": "datetime"
}
```

### Transactions Collection
```json
{
  "_id": "ObjectId",
  "inventory_item_id": "string",
  "type": "string",
  "quantity": "number",
  "reference": "string",
  "notes": "string",
  "user_id": "string",
  "created_at": "datetime"
}
```

## Usage

1. Open your browser and navigate to `http://localhost:3000`
2. Login with default credentials (User ID: 743663, Password: girish7890@A)
3. Access the dashboard to manage inventory

## Features in Detail

### Authentication
- JWT-based authentication
- Default admin user creation
- Role-based access control
- Secure password hashing

### Inventory Management
- Add, edit, delete inventory items
- Automatic stock status calculation
- SKU uniqueness validation
- Category-based organization

### Stock Tracking
- Real-time stock updates
- Transaction history
- Low stock alerts
- Stock movements (Stock In/Out/Adjustment)

### Dashboard
- Inventory statistics
- Quick overview of stock levels
- Total inventory value calculation
- Alert notifications

## Development

### Running Tests
```bash
# Backend tests
pytest

# Frontend tests
cd client && npm test
```

### Building for Production
```bash
# Build frontend
cd client && npm run build

# Run backend with production settings
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
inventory-management-system/
├── app/
│   ├── models/              # Pydantic models
│   │   ├── user.py
│   │   └── inventory.py
│   ├── routers/             # API routes
│   │   ├── auth.py
│   │   └── inventory.py
│   ├── services/            # Business logic
│   │   └── mongodb_db.py
│   └── utils/               # Utilities
│       └── auth.py
├── client/                  # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── utils/
│   └── public/
├── main.py                  # FastAPI application entry
├── requirements.txt         # Python dependencies
├── .env                    # Environment variables
└── README.md
```

## License

MIT License

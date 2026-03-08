# MongoDB Setup Guide

This guide explains the details required for setting up MongoDB with your inventory management system.

## MongoDB Connection Options

### Option 1: MongoDB Atlas (Cloud Database) - RECOMMENDED

#### Required Details:
1. **Connection String** - Complete MongoDB URI
2. **Database Name** - Your database name
3. **Username** - MongoDB user credentials
4. **Password** - MongoDB user password
5. **Cluster Name** - Your Atlas cluster name

#### Connection String Format:
```
mongodb+srv://<username>:<password>@<cluster-name>.mongodb.net/<database-name>?retryWrites=true&w=majority
```

#### Example:
```
mongodb+srv://myuser:mypassword@mycluster.mongodb.net/inventory_management?retryWrites=true&w=majority
```

### Option 2: Local MongoDB Installation

#### Required Details:
1. **Host** - Usually `localhost` or `127.0.0.1`
2. **Port** - Default is `27017`
3. **Database Name** - Your database name

#### Connection String Format:
```
mongodb://<host>:<port>/<database-name>
```

#### Example:
```
mongodb://localhost:27017/inventory_management_fastapi
```

## Step-by-Step MongoDB Atlas Setup

### 1. Create MongoDB Atlas Account
- Go to [https://www.mongodb.com/atlas](https://www.mongodb.com/atlas)
- Sign up for a free account
- Verify your email

### 2. Create a Cluster
- Click "Build a Cluster"
- Choose "FREE" tier (M0 Sandbox)
- Select a cloud provider and region (closest to your users)
- Name your cluster
- Click "Create Cluster"

### 3. Create Database User
- Go to "Database Access" in the left menu
- Click "Add New Database User"
- **Username**: Choose a username (e.g., `admin`)
- **Password**: Create a strong password
- **Database User Privileges**: Choose "Read and write to any database"
- Click "Add User"

### 4. Configure Network Access
- Go to "Network Access" in the left menu
- Click "Add IP Address"
- Choose "Allow Access from Anywhere" (0.0.0.0/0) for development
- Click "Confirm"

### 5. Get Connection String
- Go to "Database" in the left menu
- Click "Connect" on your cluster
- Choose "Connect your application"
- Select "Python" and version "3.6 or later"
- Copy the connection string

### 6. Update Connection String
Replace the placeholder values in your connection string:
- `<password>` - Replace with your actual database user password
- `<database-name>` - Replace with `inventory_management_fastapi`

#### Final Connection String Example:
```
mongodb+srv://admin:YourActualPassword123@mycluster.mongodb.net/inventory_management_fastapi?retryWrites=true&w=majority
```

## Environment Variables

Update your `.env` file with the following:

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/inventory_management_fastapi?retryWrites=true&w=majority

# JWT Configuration
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Default User Credentials
DEFAULT_USER_ID=743663
DEFAULT_PASSWORD=girish7890@A
```

## Security Best Practices

### 1. Use Environment Variables
- Never hard-code credentials in your code
- Use `.env` files for local development
- Use environment variables in production

### 2. Strong Passwords
- Use complex passwords for database users
- Include uppercase, lowercase, numbers, and special characters
- Minimum 12 characters recommended

### 3. Network Access
- In production, restrict IP access to specific addresses
- Don't use "Allow Access from Anywhere" in production

### 4. Database Users
- Create separate users for different applications
- Grant minimum required permissions
- Don't use root/admin users in applications

## Connection String Components Explained

```
mongodb+srv://                    # Protocol for MongoDB Atlas
username:password                 # Your database credentials
@cluster.mongodb.net              # Your cluster endpoint
/database-name                    # Your database name
?retryWrites=true&w=majority      # Connection options
```

### Connection Options:
- `retryWrites=true` - Automatically retry write operations
- `w=majority` - Acknowledge writes after majority of replicas
- `tls=true` - Enable TLS/SSL encryption (default with +srv)

## Troubleshooting Common Issues

### 1. Authentication Failed
- Check username and password are correct
- Ensure user has proper permissions
- Verify database user is created in Atlas

### 2. Network Access Denied
- Add your IP address to whitelist
- Check if firewall is blocking connection
- Verify network access settings in Atlas

### 3. Connection Timeout
- Check internet connection
- Verify cluster is running in Atlas
- Try different connection string format

### 4. Database Not Found
- Database is created automatically on first use
- Check spelling of database name
- Verify connection string format

## Testing Your Connection

### Python Test Script:
```python
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

async def test_connection():
    try:
        client = AsyncIOMotorClient(
            "your-connection-string-here",
            server_api=ServerApi('1')
        )
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # List databases
        databases = await client.list_database_names()
        print(f"Available databases: {databases}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

# Run test
import asyncio
asyncio.run(test_connection())
```

## What Your Application Creates Automatically

When you run your FastAPI application, it will automatically create:

1. **Database**: `inventory_management_fastapi`
2. **Collections**:
   - `users` - User accounts and authentication
   - `inventory_items` - Inventory products
   - `transactions` - Stock movement history

3. **Indexes** for performance:
   - Users: email, username
   - Inventory: sku, category, status
   - Transactions: inventory_item_id, created_at

## Production Considerations

1. **Backup Strategy**: Enable automated backups in Atlas
2. **Monitoring**: Set up alerts for performance metrics
3. **Scaling**: Upgrade cluster tier based on usage
4. **Security**: Use VPC peering for private connections
5. **Compliance**: Enable audit logging for regulatory requirements

## Cost Management

- Free tier includes 512MB storage
- Monitor your data usage in Atlas dashboard
- Set up billing alerts to avoid unexpected charges
- Consider data archiving for old transactions

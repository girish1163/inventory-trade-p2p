const mongoose = require('mongoose');

const InventoryItemSchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
        trim: true,
        maxlength: 100
    },
    sku: {
        type: String,
        required: true,
        unique: true,
        trim: true,
        uppercase: true
    },
    description: {
        type: String,
        maxlength: 500
    },
    category: {
        type: String,
        required: true,
        enum: ['Electronics', 'Clothing', 'Food', 'Furniture', 'Books', 'Tools', 'Other']
    },
    quantity: {
        type: Number,
        required: true,
        min: 0,
        default: 0
    },
    minStockLevel: {
        type: Number,
        required: true,
        min: 0,
        default: 10
    },
    maxStockLevel: {
        type: Number,
        required: true,
        min: 0,
        default: 100
    },
    unitPrice: {
        type: Number,
        required: true,
        min: 0
    },
    supplier: {
        type: String,
        trim: true
    },
    location: {
        type: String,
        trim: true
    },
    status: {
        type: String,
        enum: ['In Stock', 'Low Stock', 'Out of Stock', 'Discontinued'],
        default: 'In Stock'
    },
    lastUpdated: {
        type: Date,
        default: Date.now
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

// Update status based on quantity
InventoryItemSchema.pre('save', function(next) {
    if (this.quantity === 0) {
        this.status = 'Out of Stock';
    } else if (this.quantity <= this.minStockLevel) {
        this.status = 'Low Stock';
    } else {
        this.status = 'In Stock';
    }
    this.lastUpdated = Date.now();
    next();
});

module.exports = mongoose.model('InventoryItem', InventoryItemSchema);

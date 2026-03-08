const mongoose = require('mongoose');

const TransactionSchema = new mongoose.Schema({
    inventoryItem: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'InventoryItem',
        required: true
    },
    type: {
        type: String,
        enum: ['Stock In', 'Stock Out', 'Adjustment', 'Transfer'],
        required: true
    },
    quantity: {
        type: Number,
        required: true
    },
    reference: {
        type: String,
        trim: true
    },
    notes: {
        type: String,
        maxlength: 200
    },
    user: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

module.exports = mongoose.model('Transaction', TransactionSchema);

const express = require('express');
const InventoryItem = require('../models/InventoryItem');
const Transaction = require('../models/Transaction');
const router = express.Router();

// Get all inventory items
router.get('/', async (req, res) => {
    try {
        const { category, status, search } = req.query;
        let query = {};

        if (category) query.category = category;
        if (status) query.status = status;
        if (search) {
            query.$or = [
                { name: { $regex: search, $options: 'i' } },
                { sku: { $regex: search, $options: 'i' } },
                { description: { $regex: search, $options: 'i' } }
            ];
        }

        const items = await InventoryItem.find(query).sort({ createdAt: -1 });
        res.json(items);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Get single inventory item
router.get('/:id', async (req, res) => {
    try {
        const item = await InventoryItem.findById(req.params.id);
        if (!item) {
            return res.status(404).json({ message: 'Item not found' });
        }
        res.json(item);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Create new inventory item
router.post('/', async (req, res) => {
    try {
        const item = new InventoryItem(req.body);
        const newItem = await item.save();
        res.status(201).json(newItem);
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
});

// Update inventory item
router.put('/:id', async (req, res) => {
    try {
        const item = await InventoryItem.findByIdAndUpdate(
            req.params.id,
            req.body,
            { new: true, runValidators: true }
        );
        if (!item) {
            return res.status(404).json({ message: 'Item not found' });
        }
        res.json(item);
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
});

// Delete inventory item
router.delete('/:id', async (req, res) => {
    try {
        const item = await InventoryItem.findByIdAndDelete(req.params.id);
        if (!item) {
            return res.status(404).json({ message: 'Item not found' });
        }
        res.json({ message: 'Item deleted successfully' });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Update stock (stock in/out)
router.post('/:id/stock', async (req, res) => {
    try {
        const { type, quantity, notes, userId } = req.body;
        
        const item = await InventoryItem.findById(req.params.id);
        if (!item) {
            return res.status(404).json({ message: 'Item not found' });
        }

        // Update quantity based on transaction type
        if (type === 'Stock In') {
            item.quantity += quantity;
        } else if (type === 'Stock Out') {
            if (item.quantity < quantity) {
                return res.status(400).json({ message: 'Insufficient stock' });
            }
            item.quantity -= quantity;
        } else if (type === 'Adjustment') {
            item.quantity = quantity;
        }

        await item.save();

        // Create transaction record
        const transaction = new Transaction({
            inventoryItem: item._id,
            type,
            quantity,
            notes,
            user: userId
        });
        await transaction.save();

        res.json({ item, transaction });
    } catch (error) {
        res.status(400).json({ message: error.message });
    }
});

// Get transactions for an item
router.get('/:id/transactions', async (req, res) => {
    try {
        const transactions = await Transaction.find({ inventoryItem: req.params.id })
            .populate('user', 'username')
            .sort({ createdAt: -1 });
        res.json(transactions);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

// Get low stock items
router.get('/alerts/low-stock', async (req, res) => {
    try {
        const items = await InventoryItem.find({
            $expr: { $lte: ['$quantity', '$minStockLevel'] }
        }).sort({ quantity: 1 });
        res.json(items);
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
});

module.exports = router;

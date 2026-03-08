import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import axios from 'axios';

const Billing = () => {
  const [billingItems, setBillingItems] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingBill, setEditingBill] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    invoice_number: '',
    customer_name: '',
    items: [],
    total_amount: 0,
    due_date: ''
  });

  const [currentItem, setCurrentItem] = useState({
    sku: '',
    name: '',
    quantity: 1,
    price: 0
  });

  useEffect(() => {
    fetchBillingItems();
  }, []);

  const fetchBillingItems = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/billing', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setBillingItems(response.data);
    } catch (error) {
      console.error('Error fetching billing items:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'total_amount' ? parseFloat(value) || 0 : value
    }));
  };

  const handleItemChange = (e) => {
    const { name, value } = e.target;
    setCurrentItem(prev => ({
      ...prev,
      [name]: name === 'quantity' || name === 'price' ? parseFloat(value) || 0 : value
    }));
  };

  const addItemToBill = () => {
    if (currentItem.sku && currentItem.name && currentItem.quantity > 0 && currentItem.price > 0) {
      const newItem = {
        ...currentItem,
        total: currentItem.quantity * currentItem.price
      };
      
      setFormData(prev => ({
        ...prev,
        items: [...prev.items, newItem],
        total_amount: prev.total_amount + newItem.total
      }));
      
      setCurrentItem({
        sku: '',
        name: '',
        quantity: 1,
        price: 0
      });
    }
  };

  const removeItemFromBill = (index) => {
    const itemToRemove = formData.items[index];
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index),
      total_amount: prev.total_amount - itemToRemove.total
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      
      if (editingBill) {
        // For demo, we'll just update the status
        await axios.put(`/api/billing/${editingBill.id}/status`, 
          { status: 'Updated' }, 
          { headers: { Authorization: `Bearer ${token}` } }
        );
      } else {
        await axios.post('/api/billing', formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      
      resetForm();
      fetchBillingItems();
    } catch (error) {
      console.error('Error saving billing item:', error);
    }
  };

  const handleEdit = (bill) => {
    setEditingBill(bill);
    setFormData({
      invoice_number: bill.invoice_number,
      customer_name: bill.customer_name,
      items: bill.items,
      total_amount: bill.total_amount,
      due_date: bill.due_date
    });
    setShowAddForm(true);
  };

  const handleStatusUpdate = async (billId, newStatus) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`/api/billing/${billId}/status`, 
        { status: newStatus }, 
        { headers: { Authorization: `Bearer ${token}` } }
      );
      fetchBillingItems();
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const resetForm = () => {
    setFormData({
      invoice_number: '',
      customer_name: '',
      items: [],
      total_amount: 0,
      due_date: ''
    });
    setCurrentItem({
      sku: '',
      name: '',
      quantity: 1,
      price: 0
    });
    setEditingBill(null);
    setShowAddForm(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Paid': return '#28a745';
      case 'Pending': return '#ffc107';
      case 'Overdue': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getStatusBadge = (status) => {
    return (
      <span style={{
        backgroundColor: getStatusColor(status),
        color: 'white',
        padding: '4px 8px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: 'bold'
      }}>
        {status}
      </span>
    );
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '2rem' }}>Loading billing data...</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>💰 Billing</h1>
        <div>
          <span style={{ marginRight: '1rem' }}>Welcome, {user?.username}</span>
          <button className="logout-button" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Navigation */}
        <div style={{
          display: 'flex',
          gap: '1rem',
          marginBottom: '2rem',
          flexWrap: 'wrap'
        }}>
          <button 
            onClick={() => navigate('/')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            📊 Dashboard
          </button>
          <button 
            onClick={() => navigate('/stock')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#17a2b8',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            📋 Stock List
          </button>
          <button 
            onClick={() => navigate('/inventory')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            📦 Inventory
          </button>
          <button 
            onClick={() => navigate('/notes')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#6f42c1',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            📝 Notes
          </button>
        </div>

        {/* Billing Summary */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '1rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Total Invoices</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#007bff' }}>
              {billingItems.length}
            </div>
          </div>
          <div style={{
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Pending</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ffc107' }}>
              {billingItems.filter(bill => bill.status === 'Pending').length}
            </div>
          </div>
          <div style={{
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Paid</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745' }}>
              {billingItems.filter(bill => bill.status === 'Paid').length}
            </div>
          </div>
          <div style={{
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Total Revenue</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745' }}>
              ₹{billingItems.reduce((sum, bill) => sum + bill.total_amount, 0).toFixed(2)}
            </div>
          </div>
        </div>

        {/* Add Invoice Button */}
        <div style={{ marginBottom: '2rem' }}>
          <button 
            onClick={() => setShowAddForm(!showAddForm)}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            {showAddForm ? 'Cancel' : '➕ Create Invoice'}
          </button>
        </div>

        {/* Add/Edit Invoice Form */}
        {showAddForm && (
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            marginBottom: '2rem'
          }}>
            <h2 style={{ marginTop: 0, marginBottom: '1.5rem' }}>
              {editingBill ? 'Edit Invoice' : 'Create New Invoice'}
            </h2>
            
            <form onSubmit={handleSubmit}>
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                gap: '1rem',
                marginBottom: '1.5rem'
              }}>
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    Invoice Number *
                  </label>
                  <input
                    type="text"
                    name="invoice_number"
                    value={formData.invoice_number}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    Customer Name *
                  </label>
                  <input
                    type="text"
                    name="customer_name"
                    value={formData.customer_name}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
                
                <div>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                    Due Date *
                  </label>
                  <input
                    type="date"
                    name="due_date"
                    value={formData.due_date}
                    onChange={handleInputChange}
                    required
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  />
                </div>
              </div>
              
              {/* Items Section */}
              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ marginBottom: '1rem' }}>Invoice Items</h3>
                
                {/* Add Item Form */}
                <div style={{
                  backgroundColor: '#f8f9fa',
                  padding: '1rem',
                  borderRadius: '4px',
                  marginBottom: '1rem'
                }}>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
                    gap: '0.5rem',
                    alignItems: 'end'
                  }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem' }}>SKU</label>
                      <input
                        type="text"
                        name="sku"
                        value={currentItem.sku}
                        onChange={handleItemChange}
                        placeholder="SKU"
                        style={{
                          width: '100%',
                          padding: '0.4rem',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    
                    <div>
                      <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem' }}>Item Name</label>
                      <input
                        type="text"
                        name="name"
                        value={currentItem.name}
                        onChange={handleItemChange}
                        placeholder="Item name"
                        style={{
                          width: '100%',
                          padding: '0.4rem',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    
                    <div>
                      <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem' }}>Quantity</label>
                      <input
                        type="number"
                        name="quantity"
                        value={currentItem.quantity}
                        onChange={handleItemChange}
                        min="1"
                        style={{
                          width: '100%',
                          padding: '0.4rem',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    
                    <div>
                      <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.9rem' }}>Price</label>
                      <input
                        type="number"
                        name="price"
                        value={currentItem.price}
                        onChange={handleItemChange}
                        min="0"
                        step="0.01"
                        style={{
                          width: '100%',
                          padding: '0.4rem',
                          border: '1px solid #ddd',
                          borderRadius: '4px',
                          fontSize: '0.9rem'
                        }}
                      />
                    </div>
                    
                    <div>
                      <button
                        type="button"
                        onClick={addItemToBill}
                        style={{
                          padding: '0.4rem 0.8rem',
                          backgroundColor: '#007bff',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '0.9rem'
                        }}
                      >
                        Add Item
                      </button>
                    </div>
                  </div>
                </div>
                
                {/* Items List */}
                {formData.items.length > 0 && (
                  <div style={{ marginBottom: '1rem' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#f8f9fa' }}>
                          <th style={{ padding: '0.5rem', textAlign: 'left', fontSize: '0.9rem' }}>SKU</th>
                          <th style={{ padding: '0.5rem', textAlign: 'left', fontSize: '0.9rem' }}>Item</th>
                          <th style={{ padding: '0.5rem', textAlign: 'center', fontSize: '0.9rem' }}>Qty</th>
                          <th style={{ padding: '0.5rem', textAlign: 'right', fontSize: '0.9rem' }}>Price</th>
                          <th style={{ padding: '0.5rem', textAlign: 'right', fontSize: '0.9rem' }}>Total</th>
                          <th style={{ padding: '0.5rem', textAlign: 'center', fontSize: '0.9rem' }}>Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {formData.items.map((item, index) => (
                          <tr key={index}>
                            <td style={{ padding: '0.5rem', fontSize: '0.9rem' }}>{item.sku}</td>
                            <td style={{ padding: '0.5rem', fontSize: '0.9rem' }}>{item.name}</td>
                            <td style={{ padding: '0.5rem', textAlign: 'center', fontSize: '0.9rem' }}>{item.quantity}</td>
                            <td style={{ padding: '0.5rem', textAlign: 'right', fontSize: '0.9rem' }}>₹{item.price.toFixed(2)}</td>
                            <td style={{ padding: '0.5rem', textAlign: 'right', fontSize: '0.9rem' }}>₹{item.total.toFixed(2)}</td>
                            <td style={{ padding: '0.5rem', textAlign: 'center' }}>
                              <button
                                type="button"
                                onClick={() => removeItemFromBill(index)}
                                style={{
                                  padding: '0.2rem 0.5rem',
                                  backgroundColor: '#dc3545',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '4px',
                                  cursor: 'pointer',
                                  fontSize: '0.8rem'
                                }}
                              >
                                Remove
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                      <tfoot>
                        <tr style={{ borderTop: '2px solid #dee2e6' }}>
                          <td colSpan="4" style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>
                            Total Amount:
                          </td>
                          <td style={{ padding: '0.5rem', textAlign: 'right', fontWeight: 'bold' }}>
                            ₹{formData.total_amount.toFixed(2)}
                          </td>
                          <td></td>
                        </tr>
                      </tfoot>
                    </table>
                  </div>
                )}
              </div>
              
              <div>
                <button
                  type="submit"
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    marginRight: '1rem'
                  }}
                >
                  {editingBill ? 'Update Invoice' : 'Create Invoice'}
                </button>
                <button
                  type="button"
                  onClick={resetForm}
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Invoices Table */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '8px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '1rem',
            borderBottom: '1px solid #dee2e6'
          }}>
            <h2 style={{ margin: 0 }}>All Invoices ({billingItems.length})</h2>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8f9fa' }}>
                  <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Invoice #</th>
                  <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Customer</th>
                  <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Items</th>
                  <th style={{ padding: '1rem', textAlign: 'right', borderBottom: '1px solid #dee2e6' }}>Total</th>
                  <th style={{ padding: '1rem', textAlign: 'center', borderBottom: '1px solid #dee2e6' }}>Due Date</th>
                  <th style={{ padding: '1rem', textAlign: 'center', borderBottom: '1px solid #dee2e6' }}>Status</th>
                  <th style={{ padding: '1rem', textAlign: 'center', borderBottom: '1px solid #dee2e6' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {billingItems.map((bill) => (
                  <tr key={bill.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>{bill.invoice_number}</td>
                    <td style={{ padding: '1rem' }}>{bill.customer_name}</td>
                    <td style={{ padding: '1rem' }}>
                      <div style={{ fontSize: '0.9rem' }}>
                        {bill.items.length} item(s)
                        <div style={{ color: '#6c757d' }}>
                          {bill.items.map(item => item.name).join(', ')}
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right', fontWeight: 'bold' }}>
                      ₹{bill.total_amount.toFixed(2)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>{bill.due_date}</td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      {getStatusBadge(bill.status)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      {bill.status === 'Pending' && (
                        <button
                          onClick={() => handleStatusUpdate(bill.id, 'Paid')}
                          style={{
                            padding: '0.25rem 0.5rem',
                            backgroundColor: '#28a745',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            marginRight: '0.5rem',
                            fontSize: '0.8rem'
                          }}
                        >
                          Mark Paid
                        </button>
                      )}
                      <button
                        onClick={() => handleEdit(bill)}
                        style={{
                          padding: '0.25rem 0.5rem',
                          backgroundColor: '#007bff',
                          color: 'white',
                          border: 'none',
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '0.8rem'
                        }}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Billing;

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import axios from 'axios';

const StockList = () => {
  const [stockItems, setStockItems] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchStockData();
  }, []);

  const fetchStockData = async () => {
    try {
      const token = localStorage.getItem('token');
      const [stockResponse, alertsResponse] = await Promise.all([
        axios.get('/api/stock', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        axios.get('/api/stock/alerts', {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);
      
      setStockItems(stockResponse.data);
      setAlerts(alertsResponse.data);
    } catch (error) {
      console.error('Error fetching stock data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'In Stock': return '#28a745';
      case 'Low Stock': return '#ffc107';
      case 'Out of Stock': return '#dc3545';
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
    return <div style={{ textAlign: 'center', padding: '2rem' }}>Loading stock data...</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>📦 Stock List</h1>
        <div>
          <span style={{ marginRight: '1rem' }}>Welcome, {user?.username}</span>
          <button className="logout-button" onClick={logout}>
            Logout
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Stock Alerts */}
        {alerts.length > 0 && (
          <div style={{
            backgroundColor: '#fff3cd',
            border: '1px solid #ffeaa7',
            borderRadius: '8px',
            padding: '1rem',
            marginBottom: '2rem'
          }}>
            <h3 style={{ color: '#856404', marginBottom: '0.5rem' }}>⚠️ Stock Alerts</h3>
            <p style={{ color: '#856404', margin: 0 }}>
              You have {alerts.length} item(s) that need attention
            </p>
          </div>
        )}

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
            📦 Inventory Management
          </button>
          <button 
            onClick={() => navigate('/billing')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#17a2b8',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            💰 Billing
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

        {/* Stock Summary */}
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
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Total Items</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#007bff' }}>
              {stockItems.length}
            </div>
          </div>
          <div style={{
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Low Stock</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#ffc107' }}>
              {stockItems.filter(item => item.status === 'Low Stock').length}
            </div>
          </div>
          <div style={{
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Out of Stock</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#dc3545' }}>
              {stockItems.filter(item => item.status === 'Out of Stock').length}
            </div>
          </div>
          <div style={{
            backgroundColor: 'white',
            padding: '1rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            textAlign: 'center'
          }}>
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Total Value</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#28a745' }}>
              ₹{stockItems.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0).toFixed(2)}
            </div>
          </div>
        </div>

        {/* Stock Table */}
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
            <h2 style={{ margin: 0 }}>Current Stock Levels</h2>
          </div>
          
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f8f9fa' }}>
                  <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>SKU</th>
                  <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Item Name</th>
                  <th style={{ padding: '1rem', textAlign: 'left', borderBottom: '1px solid #dee2e6' }}>Category</th>
                  <th style={{ padding: '1rem', textAlign: 'center', borderBottom: '1px solid #dee2e6' }}>Quantity</th>
                  <th style={{ padding: '1rem', textAlign: 'center', borderBottom: '1px solid #dee2e6' }}>Min Level</th>
                  <th style={{ padding: '1rem', textAlign: 'right', borderBottom: '1px solid #dee2e6' }}>Unit Price</th>
                  <th style={{ padding: '1rem', textAlign: 'center', borderBottom: '1px solid #dee2e6' }}>Status</th>
                  <th style={{ padding: '1rem', textAlign: 'right', borderBottom: '1px solid #dee2e6' }}>Total Value</th>
                </tr>
              </thead>
              <tbody>
                {stockItems.map((item, index) => (
                  <tr key={item.id} style={{ borderBottom: '1px solid #dee2e6' }}>
                    <td style={{ padding: '1rem', fontWeight: 'bold' }}>{item.sku}</td>
                    <td style={{ padding: '1rem' }}>
                      <div>
                        <strong>{item.name}</strong>
                        {item.description && (
                          <div style={{ fontSize: '0.8rem', color: '#6c757d' }}>
                            {item.description}
                          </div>
                        )}
                      </div>
                    </td>
                    <td style={{ padding: '1rem' }}>{item.category}</td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>{item.quantity}</td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>{item.min_stock_level}</td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>₹{item.unit_price.toFixed(2)}</td>
                    <td style={{ padding: '1rem', textAlign: 'center' }}>
                      {getStatusBadge(item.status)}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right', fontWeight: 'bold' }}>
                      ₹{(item.quantity * item.unit_price).toFixed(2)}
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

export default StockList;

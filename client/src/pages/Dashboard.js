import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import axios from 'axios';

const Dashboard = () => {
  const [stats, setStats] = useState({
    total_items: 0,
    low_stock: 0,
    out_of_stock: 0,
    total_value: 0,
    pending_bills: 0,
    total_notes: 0
  });
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/dashboard', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '2rem' }}>Loading dashboard...</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>📊 Inventory Dashboard</h1>
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
            onClick={() => navigate('/stock')}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#17a2b8',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            📋 Stock List
          </button>
          <button 
            onClick={() => navigate('/inventory')}
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
            📦 Inventory Management
          </button>
          <button 
            onClick={() => navigate('/billing')}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#fd7e14',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            💰 Billing
          </button>
          <button 
            onClick={() => navigate('/notes')}
            style={{
              padding: '0.75rem 1.5rem',
              backgroundColor: '#6f42c1',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            📝 Notes
          </button>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Items</h3>
            <div className="value">{stats.total_items}</div>
            <div style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
              All inventory items
            </div>
          </div>
          <div className="stat-card">
            <h3>Low Stock Items</h3>
            <div className="value" style={{ color: '#ffc107' }}>{stats.low_stock}</div>
            <div style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Need reordering
            </div>
          </div>
          <div className="stat-card">
            <h3>Out of Stock</h3>
            <div className="value" style={{ color: '#dc3545' }}>{stats.out_of_stock}</div>
            <div style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Items unavailable
            </div>
          </div>
          <div className="stat-card">
            <h3>Total Value</h3>
            <div className="value">₹{stats.total_value.toFixed(2)}</div>
            <div style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Inventory worth
            </div>
          </div>
          <div className="stat-card">
            <h3>Pending Bills</h3>
            <div className="value" style={{ color: '#fd7e14' }}>{stats.pending_bills}</div>
            <div style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Unpaid invoices
            </div>
          </div>
          <div className="stat-card">
            <h3>Total Notes</h3>
            <div className="value" style={{ color: '#6f42c1' }}>{stats.total_notes}</div>
            <div style={{ fontSize: '0.9rem', color: '#6c757d', marginTop: '0.5rem' }}>
              Important notes
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📦</div>
            <h2 style={{ marginBottom: '1rem' }}>Inventory Management</h2>
            <p style={{ color: '#666', lineHeight: '1.6', marginBottom: '1.5rem' }}>
              Add, edit, and delete inventory items. Track stock levels and manage product information.
            </p>
            <button 
              onClick={() => navigate('/inventory')}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#28a745',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Manage Inventory
            </button>
          </div>

          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📋</div>
            <h2 style={{ marginBottom: '1rem' }}>Stock List</h2>
            <p style={{ color: '#666', lineHeight: '1.6', marginBottom: '1.5rem' }}>
              View current stock levels, check alerts, and monitor inventory status across all items.
            </p>
            <button 
              onClick={() => navigate('/stock')}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#17a2b8',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              View Stock List
            </button>
          </div>

          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>💰</div>
            <h2 style={{ marginBottom: '1rem' }}>Billing</h2>
            <p style={{ color: '#666', lineHeight: '1.6', marginBottom: '1.5rem' }}>
              Create invoices, manage billing, and track payments from customers.
            </p>
            <button 
              onClick={() => navigate('/billing')}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#fd7e14',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Manage Billing
            </button>
          </div>

          <div style={{
            background: 'white',
            padding: '2rem',
            borderRadius: '10px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <div style={{ fontSize: '2rem', marginBottom: '1rem' }}>📝</div>
            <h2 style={{ marginBottom: '1rem' }}>Notes</h2>
            <p style={{ color: '#666', lineHeight: '1.6', marginBottom: '1.5rem' }}>
              Keep important notes, meeting minutes, and organizational information.
            </p>
            <button 
              onClick={() => navigate('/notes')}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#6f42c1',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Manage Notes
            </button>
          </div>
        </div>

        {/* Recent Activity */}
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '10px',
          boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)'
        }}>
          <h2 style={{ marginBottom: '1rem' }}>System Overview</h2>
          <p style={{ color: '#666', lineHeight: '1.6', marginBottom: '2rem' }}>
            Welcome to your Inventory Management System! This comprehensive platform helps you manage all aspects of your inventory and business operations.
          </p>
          
          <h3 style={{ marginBottom: '1rem', color: '#495057' }}>Available Features:</h3>
          <ul style={{ color: '#666', lineHeight: '1.8', paddingLeft: '1.5rem' }}>
            <li><strong>Stock List:</strong> Real-time stock monitoring and alerts</li>
            <li><strong>Inventory Management:</strong> Complete CRUD operations for items</li>
            <li><strong>Billing:</strong> Invoice creation and payment tracking</li>
            <li><strong>Notes:</strong> Organized note-taking system with categories</li>
            <li><strong>Dashboard:</strong> Overview with key metrics and statistics</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

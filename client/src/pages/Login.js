import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';

const Login = () => {
  const [credentials, setCredentials] = useState({
    email: '743663',
    password: 'girish7890@A'
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // For demo purposes, accept the default credentials without email format validation
    const loginEmail = credentials.email === '743663' ? 'admin@inventory.com' : credentials.email;

    const response = await axios.post('/api/auth/login', {
      email: loginEmail, // Use loginEmail instead of credentials.email
      password: credentials.password
    });

    if (response.data.success) {
      navigate('/');
    } else {
      setError(response.data.message);
    }
    setLoading(false);
  };

  const handleQuickLogin = () => {
    setCredentials({
      email: '743663',
      password: 'girish7890@A'
    });
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>Inventory Management</h1>
          <p>Sign in to manage your inventory</p>
        </div>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">User ID</label>
            <input
              type="text"
              id="email"
              name="email"
              value={credentials.email}
              onChange={handleChange}
              required
              placeholder="Enter your user ID"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={credentials.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
          </div>

          <button 
            type="submit" 
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div style={{ marginTop: '1rem', textAlign: 'center' }}>
          <button 
            type="button" 
            onClick={handleQuickLogin}
            style={{
              background: 'none',
              border: '1px solid #667eea',
              color: '#667eea',
              padding: '0.5rem 1rem',
              borderRadius: '5px',
              cursor: 'pointer',
              fontSize: '0.8rem'
            }}
          >
            Use Default Credentials
          </button>
        </div>

        <div style={{ 
          marginTop: '1rem', 
          padding: '1rem', 
          backgroundColor: '#f8f9fa', 
          borderRadius: '5px',
          fontSize: '0.8rem',
          color: '#666'
        }}>
          <strong>Default Credentials:</strong><br />
          User ID: 743663<br />
          Password: girish7890@A
        </div>
      </div>
    </div>
  );
};

export default Login;

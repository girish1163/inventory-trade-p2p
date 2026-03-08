import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../utils/AuthContext';
import axios from 'axios';

const Notes = () => {
  const [notes, setNotes] = useState([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'General'
  });

  useEffect(() => {
    fetchNotes();
  }, []);

  const fetchNotes = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/notes', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setNotes(response.data);
    } catch (error) {
      console.error('Error fetching notes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      
      if (editingNote) {
        await axios.put(`/api/notes/${editingNote.id}`, formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } else {
        await axios.post('/api/notes', formData, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      
      resetForm();
      fetchNotes();
    } catch (error) {
      console.error('Error saving note:', error);
    }
  };

  const handleEdit = (note) => {
    setEditingNote(note);
    setFormData({
      title: note.title,
      content: note.content,
      category: note.category
    });
    setShowAddForm(true);
  };

  const handleDelete = async (noteId) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`/api/notes/${noteId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        fetchNotes();
      } catch (error) {
        console.error('Error deleting note:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      category: 'General'
    });
    setEditingNote(null);
    setShowAddForm(false);
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'Management': return '#007bff';
      case 'Procurement': return '#28a745';
      case 'Sales': return '#17a2b8';
      case 'Operations': return '#ffc107';
      case 'General': return '#6c757d';
      default: return '#6f42c1';
    }
  };

  const getCategoryBadge = (category) => {
    return (
      <span style={{
        backgroundColor: getCategoryColor(category),
        color: 'white',
        padding: '4px 8px',
        borderRadius: '4px',
        fontSize: '12px',
        fontWeight: 'bold'
      }}>
        {category}
      </span>
    );
  };

  const searchNotes = (searchTerm) => {
    if (!searchTerm) {
      return notes;
    }
    
    const lowerSearchTerm = searchTerm.toLowerCase();
    return notes.filter(note => 
      note.title.toLowerCase().includes(lowerSearchTerm) ||
      note.content.toLowerCase().includes(lowerSearchTerm) ||
      note.category.toLowerCase().includes(lowerSearchTerm)
    );
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '2rem' }}>Loading notes...</div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>📝 Notes</h1>
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
            onClick={() => navigate('/billing')}
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: '#fd7e14',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            💰 Billing
          </button>
        </div>

        {/* Notes Summary */}
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
            <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>Total Notes</h3>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: '#007bff' }}>
              {notes.length}
            </div>
          </div>
          
          {['Management', 'Procurement', 'Sales', 'Operations', 'General'].map(category => {
            const count = notes.filter(note => note.category === category).length;
            return (
              <div key={category}
                style={{
                  backgroundColor: 'white',
                  padding: '1rem',
                  borderRadius: '8px',
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                  textAlign: 'center'
                }}>
                <h3 style={{ margin: '0 0 0.5rem 0', color: '#495057' }}>{category}</h3>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: getCategoryColor(category) }}>
                  {count}
                </div>
              </div>
            );
          })}
        </div>

        {/* Add Note Button */}
        <div style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <button 
            onClick={() => setShowAddForm(!showAddForm)}
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
            {showAddForm ? 'Cancel' : '➕ Add New Note'}
          </button>
          
          <input
            type="text"
            placeholder="🔍 Search notes..."
            onChange={(e) => {
              const searchResults = searchNotes(e.target.value);
              if (e.target.value) {
                setNotes(searchResults);
              } else {
                fetchNotes();
              }
            }}
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              width: '300px'
            }}
          />
        </div>

        {/* Add/Edit Note Form */}
        {showAddForm && (
          <div style={{
            backgroundColor: 'white',
            padding: '2rem',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            marginBottom: '2rem'
          }}>
            <h2 style={{ marginTop: 0, marginBottom: '1.5rem' }}>
              {editingNote ? 'Edit Note' : 'Add New Note'}
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
                    Title *
                  </label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
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
                    Category *
                  </label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    style={{
                      width: '100%',
                      padding: '0.5rem',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }}
                  >
                    <option value="Management">Management</option>
                    <option value="Procurement">Procurement</option>
                    <option value="Sales">Sales</option>
                    <option value="Operations">Operations</option>
                    <option value="General">General</option>
                  </select>
                </div>
              </div>
              
              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                  Content *
                </label>
                <textarea
                  name="content"
                  value={formData.content}
                  onChange={handleInputChange}
                  required
                  rows="6"
                  placeholder="Enter your note content here..."
                  style={{
                    width: '100%',
                    padding: '0.5rem',
                    border: '1px solid #ddd',
                    borderRadius: '4px',
                    resize: 'vertical',
                    fontFamily: 'inherit'
                  }}
                />
              </div>
              
              <div>
                <button
                  type="submit"
                  style={{
                    padding: '0.75rem 1.5rem',
                    backgroundColor: '#6f42c1',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    marginRight: '1rem'
                  }}
                >
                  {editingNote ? 'Update Note' : 'Add Note'}
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

        {/* Notes Grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))',
          gap: '1.5rem'
        }}>
          {notes.map((note) => (
            <div
              key={note.id}
              style={{
                backgroundColor: 'white',
                borderRadius: '8px',
                boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                overflow: 'hidden',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
              }}
            >
              <div style={{
                backgroundColor: '#f8f9fa',
                padding: '1rem',
                borderBottom: '1px solid #dee2e6'
              }}>
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '0.5rem'
                }}>
                  <h3 style={{ margin: 0, color: '#495057', fontSize: '1.1rem' }}>
                    {note.title}
                  </h3>
                  {getCategoryBadge(note.category)}
                </div>
                <div style={{ fontSize: '0.8rem', color: '#6c757d' }}>
                  Created: {new Date(note.created_at).toLocaleDateString()}
                  {note.updated_at !== note.created_at && (
                    <span> • Updated: {new Date(note.updated_at).toLocaleDateString()}</span>
                  )}
                </div>
              </div>
              
              <div style={{ padding: '1rem' }}>
                <p style={{
                  margin: 0,
                  color: '#495057',
                  lineHeight: '1.5',
                  maxHeight: '150px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  display: '-webkit-box',
                  WebkitLineClamp: 6,
                  WebkitBoxOrient: 'vertical'
                }}>
                  {note.content}
                </p>
              </div>
              
              <div style={{
                padding: '1rem',
                borderTop: '1px solid #dee2e6',
                backgroundColor: '#f8f9fa',
                display: 'flex',
                justifyContent: 'flex-end',
                gap: '0.5rem'
              }}>
                <button
                  onClick={() => handleEdit(note)}
                  style={{
                    padding: '0.4rem 0.8rem',
                    backgroundColor: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.8rem'
                  }}
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(note.id)}
                  style={{
                    padding: '0.4rem 0.8rem',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '0.8rem'
                  }}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>

        {notes.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '3rem',
            backgroundColor: 'white',
            borderRadius: '8px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
          }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📝</div>
            <h3 style={{ color: '#495057', marginBottom: '0.5rem' }}>No notes yet</h3>
            <p style={{ color: '#6c757d', marginBottom: '1.5rem' }}>
              Start by adding your first note to keep track of important information.
            </p>
            <button
              onClick={() => setShowAddForm(true)}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: '#6f42c1',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Add Your First Note
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Notes;

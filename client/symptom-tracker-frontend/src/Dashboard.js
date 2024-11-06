import React, { useState, useEffect } from 'react';

const Dashboard = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [symptoms, setSymptoms] = useState([]);
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [loginForm, setLoginForm] = useState({ username: '', password: '' });
  const [showRegister, setShowRegister] = useState(false);
  const [registerForm, setRegisterForm] = useState({
    username: '',
    password: '',
    age: '',
    gender: '',
    location: ''
  });
  const [error, setError] = useState('');

  // Check for existing token on component mount
  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
      setIsLoggedIn(true);
      fetchSymptoms(JSON.parse(storedUser).id, storedToken);
    }
  }, []);

  const fetchSymptoms = async (userId, currentToken) => {
    try {
      const response = await fetch(`http://localhost:5000/users/${userId}/symptoms`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${currentToken}`,
          'Content-Type': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        setSymptoms(data);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to fetch symptoms');
      }
    } catch (error) {
      console.error('Error fetching symptoms:', error);
      setError('Failed to fetch symptoms');
      
      // Handle expired token
      if (error.message === 'Token has expired') {
        handleLogout();
      }
    }
  };
  
  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch('http://localhost:5000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginForm),
      });
  
      const data = await response.json();
      
      if (response.ok) {
        setToken(data.token);
        setUser(data.user);
        setIsLoggedIn(true);
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        await fetchSymptoms(data.user.id, data.token);
      } else {
        setError(data.message || 'Login failed');
        console.error('Login response:', data);
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Login failed. Please try again.');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('http://localhost:5000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(registerForm),
      });

      const data = await response.json();

      if (response.ok) {
        setToken(data.token);
        setUser(data.user);
        setIsLoggedIn(true);
        localStorage.setItem('token', data.token);
        localStorage.setItem('user', JSON.stringify(data.user));
        fetchSymptoms(data.user.id, data.token);
      } else {
        setError(data.message || 'Registration failed');
      }
    } catch (error) {
      console.error('Registration error:', error);
      setError('Registration failed. Please try again.');
    }
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setUser(null);
    setToken(null);
    setSymptoms([]);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const handleAddSymptom = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await fetch(`http://localhost:5000/users/${user.id}/symptoms`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          label: e.target.label.value,
          description: e.target.description.value,
        }),
      });

      if (response.ok) {
        fetchSymptoms(user.id, token);
        e.target.reset();
      } else {
        const data = await response.json();
        throw new Error(data.message || 'Failed to add symptom');
      }
    } catch (error) {
      console.error('Error adding symptom:', error);
      setError('Failed to add symptom. Please try again.');
    }
  };

  if (!isLoggedIn) {
    return (
      <div className="login-container" style={{ maxWidth: '400px', margin: '40px auto', padding: '20px' }}>
        <h2 style={{ marginBottom: '20px' }}>{showRegister ? 'Register' : 'Login'}</h2>
        {error && (
          <div style={{ 
            padding: '10px', 
            backgroundColor: '#f8d7da', 
            color: '#721c24', 
            borderRadius: '4px',
            marginBottom: '10px'
          }}>
            {error}
          </div>
        )}
        
        {showRegister ? (
          <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input
              type="text"
              placeholder="Username"
              style={{ padding: '8px', marginBottom: '10px' }}
              value={registerForm.username}
              onChange={(e) => setRegisterForm({...registerForm, username: e.target.value})}
              required
            />
            <input
              type="password"
              placeholder="Password"
              style={{ padding: '8px', marginBottom: '10px' }}
              value={registerForm.password}
              onChange={(e) => setRegisterForm({...registerForm, password: e.target.value})}
              required
            />
            <input
              type="number"
              placeholder="Age"
              style={{ padding: '8px', marginBottom: '10px' }}
              value={registerForm.age}
              onChange={(e) => setRegisterForm({...registerForm, age: e.target.value})}
            />
            <select
              style={{ padding: '8px', marginBottom: '10px' }}
              value={registerForm.gender}
              onChange={(e) => setRegisterForm({...registerForm, gender: e.target.value})}
            >
              <option value="">Select Gender</option>
              <option value="M">Male</option>
              <option value="F">Female</option>
              <option value="O">Other</option>
            </select>
            <input
              type="text"
              placeholder="Location"
              style={{ padding: '8px', marginBottom: '10px' }}
              value={registerForm.location}
              onChange={(e) => setRegisterForm({...registerForm, location: e.target.value})}
            />
            <button 
              type="submit"
              style={{ 
                padding: '10px', 
                backgroundColor: '#28a745', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Register
            </button>
          </form>
        ) : (
          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input
              type="text"
              placeholder="Username"
              style={{ padding: '8px', marginBottom: '10px' }}
              value={loginForm.username}
              onChange={(e) => setLoginForm({...loginForm, username: e.target.value})}
              required
            />
            <input
              type="password"
              placeholder="Password"
              style={{ padding: '8px', marginBottom: '10px' }}
              value={loginForm.password}
              onChange={(e) => setLoginForm({...loginForm, password: e.target.value})}
              required
            />
            <button 
              type="submit"
              style={{ 
                padding: '10px', 
                backgroundColor: '#007bff', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Login
            </button>
          </form>
        )}
        
        <button
          onClick={() => {
            setShowRegister(!showRegister);
            setError('');
          }}
          style={{ 
            marginTop: '10px',
            padding: '10px',
            backgroundColor: 'transparent',
            color: '#007bff',
            border: 'none',
            cursor: 'pointer',
            textAlign: 'center',
            width: '100%'
          }}
        >
          {showRegister ? 'Already have an account? Login' : 'Need an account? Register'}
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <header style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '20px',
        padding: '20px',
        backgroundColor: '#f8f9fa',
        borderRadius: '4px'
      }}>
        <h1>Symptom Tracker</h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <span>Welcome, {user?.username}!</span>
          <button 
            onClick={handleLogout}
            style={{ 
              padding: '8px 16px', 
              backgroundColor: '#dc3545', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </header>

      {error && (
        <div style={{ 
          padding: '10px', 
          backgroundColor: '#f8d7da', 
          color: '#721c24', 
          borderRadius: '4px',
          marginBottom: '20px'
        }}>
          {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <div style={{ 
          padding: '20px', 
          backgroundColor: 'white', 
          borderRadius: '4px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ marginBottom: '20px' }}>Add New Symptom</h2>
          <form onSubmit={handleAddSymptom} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <input
              type="text"
              name="label"
              placeholder="Symptom Label"
              style={{ padding: '8px', marginBottom: '10px' }}
              required
            />
            <textarea
              name="description"
              placeholder="Symptom Description"
              style={{ padding: '8px', marginBottom: '10px', minHeight: '100px' }}
              required
            />
            <button 
              type="submit"
              style={{ 
                padding: '10px', 
                backgroundColor: '#28a745', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              Add Symptom
            </button>
          </form>
        </div>

        <div style={{ 
          padding: '20px', 
          backgroundColor: 'white', 
          borderRadius: '4px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ marginBottom: '20px' }}>Your Symptoms</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {symptoms.map((symptom) => (
              <div 
                key={symptom.id}
                style={{ 
                  padding: '15px', 
                  backgroundColor: '#f8f9fa', 
                  borderRadius: '4px',
                  border: '1px solid #dee2e6'
                }}
              >
                <h3 style={{ marginBottom: '5px' }}>{symptom.label}</h3>
                <p style={{ color: '#6c757d', marginBottom: '5px' }}>{symptom.description}</p>
                <small style={{ color: '#6c757d' }}>
                  {new Date(symptom.timestamp).toLocaleString()}
                </small>
              </div>
            ))}
            {symptoms.length === 0 && (
              <p style={{ textAlign: 'center', color: '#6c757d' }}>No symptoms recorded yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
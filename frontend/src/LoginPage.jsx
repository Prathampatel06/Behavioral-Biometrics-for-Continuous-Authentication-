import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

export default function LoginPage() {
  const [mode, setMode] = useState('login');
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const clearMessages = () => {
    setError('');
    setSuccess('');
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    clearMessages();
    setLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/users/login`, {
        username,
        password
      });

      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user_id', response.data.user_id);
      localStorage.setItem('username', username);
      window.location.reload();
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    clearMessages();
    setLoading(true);

    try {
      await axios.post(`${API_BASE}/users/register`, {
        username,
        email,
        password
      });
      setSuccess('Registration successful. Please log in.');
      setMode('login');
      setPassword('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const title = mode === 'login' ? 'Login to Behavioral Biometrics' : 'Create a New Account';
  const buttonLabel = mode === 'login' ? 'Login' : 'Register';

  return (
    <div style={styles.container}>
      <div style={styles.formContainer}>
        <h1 style={styles.title}>{title}</h1>
        <p style={styles.subtitle}>
          Securely enroll your behavioral biometrics and protect access with typing, mouse, and touch signals.
        </p>
        <form onSubmit={mode === 'login' ? handleLogin : handleRegister} style={styles.form}>
          <div style={styles.formGroup}>
            <label>Username</label>
            <input
              autoComplete="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              style={styles.input}
              required
            />
          </div>

          {mode === 'register' && (
            <div style={styles.formGroup}>
              <label>Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter email"
                style={styles.input}
                required
              />
            </div>
          )}

          <div style={styles.formGroup}>
            <label>Password</label>
            <input
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              style={styles.input}
              required
            />
          </div>

          {error && <div style={styles.error}>{error}</div>}
          {success && <div style={styles.success}>{success}</div>}

          <button type="submit" style={styles.button} disabled={loading}>
            {loading ? `${buttonLabel}...` : buttonLabel}
          </button>
        </form>

        <p style={styles.link}>
          {mode === 'login' ? (
            <>Don't have an account? <button onClick={() => { clearMessages(); setMode('register'); }} style={styles.linkButton}>Register here</button></>
          ) : (
            <>Already have an account? <button onClick={() => { clearMessages(); setMode('login'); }} style={styles.linkButton}>Login here</button></>
          )}
        </p>
      </div>
    </div>
  );
}

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    minHeight: '100vh',
    backgroundColor: '#f5f5f5'
  },
  formContainer: {
    backgroundColor: 'white',
    padding: '40px',
    borderRadius: '8px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    width: '100%',
    maxWidth: '400px'
  },
  title: {
    textAlign: 'center',
    marginBottom: '30px',
    color: '#333'
  },
  form: {
    display: 'flex',
    flexDirection: 'column'
  },
  formGroup: {
    marginBottom: '20px'
  },
  subtitle: {
    color: '#555',
    marginBottom: '24px',
    fontSize: '14px',
    lineHeight: '1.6'
  },
  input: {
    width: '100%',
    padding: '10px',
    marginTop: '5px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    fontSize: '14px',
    boxSizing: 'border-box'
  },
  button: {
    padding: '10px',
    backgroundColor: '#007bff',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
    marginTop: '10px'
  },
  error: {
    color: '#d32f2f',
    marginBottom: '10px',
    padding: '10px',
    backgroundColor: '#ffebee',
    borderRadius: '4px'
  },
  success: {
    color: '#155724',
    marginBottom: '10px',
    padding: '10px',
    backgroundColor: '#d4edda',
    borderRadius: '4px'
  },
  link: {
    textAlign: 'center',
    marginTop: '20px',
    color: '#666'
  },
  linkButton: {
    padding: 0,
    margin: 0,
    border: 'none',
    background: 'none',
    color: '#007bff',
    textDecoration: 'underline',
    cursor: 'pointer',
    fontSize: '14px'
  }
};

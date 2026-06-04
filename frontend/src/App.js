import React from 'react';
import LoginPage from './LoginPage';
import EnrollmentPage from './EnrollmentPage';

export default function App() {
  const token = localStorage.getItem('token');
  const username = localStorage.getItem('username') || 'User';

  return (
    <div style={styles.app}>
      <nav style={styles.nav}>
        <div style={styles.navContent}>
          <div>
            <h2 style={styles.brand}>Behavioral Biometrics</h2>
            <p style={styles.brandTag}>Continuous authentication with typing, mouse, and touch signals.</p>
          </div>

          {token && (
            <div style={styles.navActions}>
              <span style={styles.userLabel}>Hello, {username}</span>
              <button
                onClick={() => {
                  localStorage.clear();
                  window.location.href = '/';
                }}
                style={styles.logoutBtn}
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </nav>

      <main style={styles.main}>
        {!token ? (
          <LoginPage />
        ) : (
          <EnrollmentPage />
        )}
      </main>
    </div>
  );
}

const styles = {
  app: {
    minHeight: '100vh',
    backgroundColor: '#eef4fb'
  },
  nav: {
    backgroundColor: '#1f2937',
    color: 'white',
    padding: '20px 0',
    boxShadow: '0 3px 10px rgba(0,0,0,0.12)'
  },
  navContent: {
    maxWidth: '1200px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingLeft: '20px',
    paddingRight: '20px'
  },
  brand: {
    margin: 0,
    fontSize: '22px'
  },
  brandTag: {
    margin: '4px 0 0',
    fontSize: '13px',
    color: '#cbd5e1'
  },
  navActions: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px'
  },
  userLabel: {
    fontSize: '14px',
    color: '#e2e8f0'
  },
  logoutBtn: {
    padding: '10px 18px',
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    borderRadius: '999px',
    cursor: 'pointer',
    fontWeight: 600
  },
  main: {
    maxWidth: '1000px',
    margin: '0 auto',
    padding: '32px 20px'
  }
};

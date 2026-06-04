import React, { useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000/api';

export default function EnrollmentPage() {
  const [sessionToken, setSessionToken] = useState('');
  const [enrollmentStatus, setEnrollmentStatus] = useState(null);
  const [isEnrolling, setIsEnrolling] = useState(false);
  const [error, setError] = useState('');
  const userId = localStorage.getItem('user_id');

  const startEnrollment = async () => {
    if (!userId) {
      setError('User is not logged in. Please log in first.');
      return;
    }

    try {
      const response = await axios.post(`${API_BASE}/enrollment/start`, {
        user_id: parseInt(userId, 10)
      });
      setSessionToken(response.data.session_token);
      setEnrollmentStatus({
        samples_collected: 0,
        target_samples: response.data.target_samples
      });
      setError('');
      setIsEnrolling(true);
    } catch (err) {
      const message = err.response?.data?.detail || err.response?.data?.message || err.message;
      setError(`Failed to start enrollment: ${message}`);
    }
  };

  const captureData = async () => {
    // Simulated biometric data capture
    const keystrokeData = {
      dwell_times: Array.from({ length: 10 }, () => Math.random() * 200),
      flight_times: Array.from({ length: 9 }, () => Math.random() * 100)
    };

    try {
      await axios.post(`${API_BASE}/enrollment/capture`, {
        user_id: parseInt(userId, 10),
        event_type: 'keystroke',
        features: keystrokeData,
        session_token: sessionToken
      });

      // Update status
      const statusResponse = await axios.get(
        `${API_BASE}/enrollment/status/${sessionToken}`
      );
      setEnrollmentStatus(statusResponse.data);

      if (statusResponse.data.enrollment_complete) {
        completeEnrollment();
      }
    } catch (err) {
      const message = err.response?.data?.detail || err.response?.data?.message || err.message;
      setError(`Failed to capture data: ${message}`);
    }
  };

  const completeEnrollment = async () => {
    try {
      await axios.post(`${API_BASE}/enrollment/complete`, {
        session_token: sessionToken,
        user_id: parseInt(userId, 10)
      });
      alert('Enrollment completed successfully!');
      setError('');
      setIsEnrolling(false);
    } catch (err) {
      const message = err.response?.data?.detail || err.response?.data?.message || err.message;
      setError(`Failed to complete enrollment: ${message}`);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <div>
            <h1 style={styles.title}>Biometric Enrollment</h1>
            <p style={styles.description}>
              Use the enrollment flow to capture typing and movement patterns. The app will collect samples and build a behavioral profile.
            </p>
          </div>

          <div style={styles.statusBadge}>
            <span style={styles.badgeLabel}>User</span>
            <span style={styles.badgeValue}>{localStorage.getItem('username') || 'Guest'}</span>
          </div>
        </div>

        {!isEnrolling ? (
          <div style={styles.emptyState}>
            <p style={styles.emptyText}>
              Ready to begin your biometric enrollment? Click the button below and capture data until your profile is trained.
            </p>
            <button onClick={startEnrollment} style={styles.primaryButton}>
              Start Enrollment
            </button>
          </div>
        ) : (
          <div style={styles.enrollmentBox}>
            <div style={styles.progressHeader}>
              <div>
                <h2 style={styles.stepTitle}>Enrollment in Progress</h2>
                <p style={styles.stepSubtitle}>Keep capturing samples until the progress reaches 100%.</p>
              </div>
              <span style={styles.sessionToken}>Session: {sessionToken.slice(0, 8)}…</span>
            </div>

            <div style={styles.progressSection}>
              <div style={styles.progressText}>Samples collected</div>
              <div style={styles.progressBar}>
                <div
                  style={{
                    ...styles.progressFill,
                    width: `${(enrollmentStatus?.samples_collected / enrollmentStatus?.target_samples) * 100}%`
                  }}
                />
              </div>
              <div style={styles.progressCount}>
                {enrollmentStatus?.samples_collected} / {enrollmentStatus?.target_samples}
              </div>
            </div>

            <div style={styles.buttonRow}>
              <button onClick={captureData} style={styles.primaryButton}>
                Capture Biometric Data
              </button>
              {enrollmentStatus?.samples_collected >= enrollmentStatus?.target_samples && (
                <button onClick={completeEnrollment} style={styles.secondaryButton}>
                  Complete Enrollment
                </button>
              )}
            </div>

            <div style={styles.tipBox}>
              <strong>Tip:</strong> Click capture multiple times to simulate behavior data. Once the session completes, finalize enrollment to save your profile.
            </div>
          </div>
        )}

        {error && <div style={styles.error}>{error}</div>}
      </div>
    </div>
  );
}

const styles = {
  container: {
    padding: '30px',
    maxWidth: '900px',
    margin: '0 auto'
  },
  card: {
    backgroundColor: 'white',
    borderRadius: '16px',
    boxShadow: '0 20px 40px rgba(15, 23, 42, 0.08)',
    padding: '32px',
    border: '1px solid #e5e7eb'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    gap: '24px',
    marginBottom: '24px'
  },
  title: {
    margin: 0,
    fontSize: '32px',
    color: '#111827'
  },
  description: {
    marginTop: '12px',
    fontSize: '15px',
    lineHeight: '1.7',
    color: '#4b5563',
    maxWidth: '680px'
  },
  statusBadge: {
    display: 'inline-flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    gap: '6px',
    minWidth: '120px'
  },
  badgeLabel: {
    fontSize: '12px',
    color: '#6b7280',
    textTransform: 'uppercase',
    letterSpacing: '0.1em'
  },
  badgeValue: {
    fontSize: '16px',
    color: '#111827',
    fontWeight: 700
  },
  emptyState: {
    display: 'grid',
    gap: '20px',
    padding: '24px',
    borderRadius: '14px',
    border: '1px dashed #cbd5e1',
    backgroundColor: '#f8fafc'
  },
  emptyText: {
    margin: 0,
    color: '#374151',
    lineHeight: '1.7'
  },
  primaryButton: {
    padding: '14px 26px',
    backgroundColor: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: '999px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 600,
    transition: 'background-color 0.2s ease'
  },
  secondaryButton: {
    padding: '14px 26px',
    backgroundColor: '#10b981',
    color: 'white',
    border: 'none',
    borderRadius: '999px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 600,
    transition: 'background-color 0.2s ease'
  },
  enrollmentBox: {
    display: 'grid',
    gap: '20px',
    padding: '24px',
    borderRadius: '16px',
    backgroundColor: '#f9fafb',
    border: '1px solid #e5e7eb'
  },
  progressHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '12px'
  },
  stepTitle: {
    margin: 0,
    fontSize: '22px',
    color: '#111827'
  },
  stepSubtitle: {
    margin: '8px 0 0',
    color: '#6b7280',
    fontSize: '14px'
  },
  sessionToken: {
    fontSize: '13px',
    color: '#6b7280',
    textAlign: 'right'
  },
  progressSection: {
    display: 'grid',
    gap: '12px'
  },
  progressText: {
    fontSize: '14px',
    color: '#4b5563'
  },
  progressBar: {
    width: '100%',
    height: '20px',
    backgroundColor: '#e5e7eb',
    borderRadius: '999px',
    overflow: 'hidden'
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#34d399',
    transition: 'width 0.3s ease'
  },
  progressCount: {
    color: '#111827',
    fontWeight: 600
  },
  buttonRow: {
    display: 'flex',
    flexWrap: 'wrap',
    gap: '14px'
  },
  tipBox: {
    padding: '16px',
    borderRadius: '12px',
    backgroundColor: '#ecfccb',
    color: '#365314',
    border: '1px solid #d9f99d'
  },
  error: {
    color: '#b91c1c',
    marginTop: '20px',
    padding: '14px',
    backgroundColor: '#fee2e2',
    borderRadius: '12px',
    border: '1px solid #fecaca'
  }
};

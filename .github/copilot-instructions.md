<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Behavioral Biometrics Continuous Authentication Project

## Project Overview
ML-powered continuous authentication system that analyzes user behavior patterns (typing rhythm, mouse movement, touchscreen patterns) for seamless, passwordless security without re-prompting for login.

## Key Technologies
- **Backend**: Python (FastAPI/Flask), PostgreSQL
- **ML Models**: scikit-learn, TensorFlow, XGBoost
- **Frontend**: React.js with real-time event tracking
- **Data Collection**: Keyboard, mouse, touchscreen event capturing
- **Deployment**: Docker, Redis for caching

## Project Structure
```
├── backend/              # FastAPI server, authentication logic
├── frontend/             # React app for testing & enrollment
├── ml_models/            # Typing, mouse, touch prediction models
├── data_collection/      # Event capturing & preprocessing
└── docs/                 # Architecture & deployment guides
```

## Development Guidelines
- Python 3.9+ for ML components
- Real-time event processing with minimal latency
- Privacy-first approach: biometric data stored locally when possible
- Continuous model retraining for adaptive authentication

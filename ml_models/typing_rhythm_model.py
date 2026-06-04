import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class TypingRhythmModel:
    """ML model for typing rhythm authentication"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path or "./ml_models/trained_models/typing_rhythm.pkl"
        self.feature_names = [
            "dwell_time_mean", "dwell_time_std",
            "flight_time_mean", "flight_time_std",
            "keystroke_interval_mean", "keystroke_interval_std",
            "keystroke_velocity_mean", "keystroke_velocity_std",
            "key_pressure_mean", "key_pressure_std",
            "typing_speed", "error_rate",
            "repeat_key_count", "special_key_ratio", "capitalization_ratio"
        ]
        self.load_model()
    
    def load_model(self):
        """Load pre-trained model from disk"""
        if Path(self.model_path).exists():
            try:
                model_data = joblib.load(self.model_path)
                self.model = model_data.get('model')
                self.scaler = model_data.get('scaler', StandardScaler())
                logger.info(f"Loaded typing rhythm model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Could not load model: {e}. Will train new model.")
                self.model = None
    
    def _normalize_events(self, keystroke_events):
        """Normalize keystroke payloads into numeric arrays."""
        if isinstance(keystroke_events, dict):
            return {
                'dwell_times': np.asarray(keystroke_events.get('dwell_times', []), dtype=float),
                'flight_times': np.asarray(keystroke_events.get('flight_times', []), dtype=float),
                'key_pressures': np.asarray(keystroke_events.get('key_pressures', []), dtype=float),
                'timestamps': np.asarray(keystroke_events.get('timestamps', []), dtype=float)
            }

        if isinstance(keystroke_events, list) and keystroke_events and isinstance(keystroke_events[0], dict):
            return {
                'dwell_times': np.asarray([event.get('dwell_time', 0) for event in keystroke_events], dtype=float),
                'flight_times': np.asarray([event.get('flight_time', 0) for event in keystroke_events], dtype=float),
                'key_pressures': np.asarray([event.get('key_pressure', 0) for event in keystroke_events], dtype=float),
                'timestamps': np.asarray([event.get('timestamp', idx) for idx, event in enumerate(keystroke_events)], dtype=float)
            }

        events = np.asarray(keystroke_events)
        if events.ndim == 1:
            return {
                'dwell_times': events[0] if len(events) > 0 else np.asarray([], dtype=float),
                'flight_times': events[1] if len(events) > 1 else np.asarray([], dtype=float),
                'key_pressures': events[2] if len(events) > 2 else np.asarray([], dtype=float),
                'timestamps': events[3] if len(events) > 3 else np.arange(len(events), dtype=float)
            }

        return {
            'dwell_times': events[:, 0] if events.shape[1] > 0 else np.asarray([], dtype=float),
            'flight_times': events[:, 1] if events.shape[1] > 1 else np.asarray([], dtype=float),
            'key_pressures': events[:, 2] if events.shape[1] > 2 else np.asarray([], dtype=float),
            'timestamps': events[:, 3] if events.shape[1] > 3 else np.arange(events.shape[0], dtype=float)
        }

    def extract_features(self, keystroke_events) -> np.ndarray:
        """Extract typing rhythm features from keystroke events"""
        normalized = self._normalize_events(keystroke_events)
        dwell_times = normalized['dwell_times']
        flight_times = normalized['flight_times']
        key_pressures = normalized['key_pressures']
        timestamps = normalized['timestamps']

        if len(dwell_times) < 2 or len(flight_times) < 2:
            return np.zeros(len(self.feature_names))

        features = []

        # Dwell time features (time key is held)
        features.extend([np.mean(dwell_times), np.std(dwell_times) or 0])

        # Flight time features (time between key releases and presses)
        features.extend([np.mean(flight_times), np.std(flight_times) or 0])

        # Keystroke interval features
        intervals = np.diff(timestamps) if len(timestamps) > 1 else np.asarray([])
        features.extend([np.mean(intervals) if len(intervals) > 0 else 0, np.std(intervals) if len(intervals) > 0 else 0])

        # Velocity and pressure features
        min_len = min(len(dwell_times), len(flight_times))
        velocity = np.asarray(dwell_times[:min_len]) + np.asarray(flight_times[:min_len])
        features.extend([np.mean(velocity), np.std(velocity) if len(velocity) > 1 else 0])

        # Pressure features
        features.extend([np.mean(key_pressures) if len(key_pressures) > 0 else 0, np.std(key_pressures) if len(key_pressures) > 1 else 0])

        # Additional metrics
        typing_speed = len(dwell_times) / 60  # keystrokes per second
        error_rate = 0.02  # placeholder
        repeat_count = int(np.sum(np.asarray(key_pressures) == 1)) if len(key_pressures) > 0 else 0

        features.extend([
            typing_speed,
            error_rate,
            repeat_count,
            0.1,  # special_key_ratio
            0.15  # capitalization_ratio
        ])

        return np.array(features[: len(self.feature_names)])
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the typing rhythm model"""
        X_scaled = self.scaler.fit_transform(X_train)
        
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_scaled, y_train)
        
        # Save model
        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler
        }, self.model_path)
        
        logger.info(f"Typing rhythm model trained and saved to {self.model_path}")
    
    def predict(self, keystroke_events: list) -> dict:
        """Predict authenticity based on typing pattern"""
        if self.model is None:
            return {"confidence": 0.5, "is_authentic": False}
        
        features = self.extract_features(keystroke_events).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        
        confidence = self.model.predict_proba(features_scaled)[0][1]
        
        return {
            "confidence": float(confidence),
            "is_authentic": confidence > 0.5,
            "model": "typing_rhythm"
        }

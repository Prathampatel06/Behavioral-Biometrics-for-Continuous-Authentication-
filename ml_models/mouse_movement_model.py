import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class MouseMovementModel:
    """ML model for mouse movement authentication"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path or "./ml_models/trained_models/mouse_movement.pkl"
        self.feature_names = [
            "velocity_mean", "velocity_std",
            "acceleration_mean", "acceleration_std",
            "curvature_mean", "curvature_std",
            "direction_changes",
            "pause_duration_mean",
            "movement_angle_mean",
            "jitter_mean",
            "distance_traveled",
            "movement_duration"
        ]
        self.load_model()
    
    def load_model(self):
        """Load pre-trained model from disk"""
        if Path(self.model_path).exists():
            try:
                model_data = joblib.load(self.model_path)
                self.model = model_data.get('model')
                self.scaler = model_data.get('scaler', StandardScaler())
                logger.info(f"Loaded mouse movement model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Could not load model: {e}. Will train new model.")
                self.model = None
    
    def _normalize_events(self, mouse_events):
        """Normalize mouse payloads into numeric arrays."""
        if isinstance(mouse_events, dict):
            positions = np.asarray(mouse_events.get('positions', []), dtype=float)
            timestamps = np.asarray(mouse_events.get('timestamps', []), dtype=float)
            return positions, timestamps

        if isinstance(mouse_events, list) and mouse_events and isinstance(mouse_events[0], dict):
            positions = np.asarray([[event.get('x', 0), event.get('y', 0)] for event in mouse_events], dtype=float)
            timestamps = np.asarray([event.get('timestamp', idx) for idx, event in enumerate(mouse_events)], dtype=float)
            return positions, timestamps

        events = np.asarray(mouse_events)
        if events.ndim == 1 and events.size > 0:
            positions = events[:2].reshape(-1, 2) if events.size >= 2 else np.zeros((len(events), 2))
            timestamps = events[2] if events.size > 2 else np.arange(len(events), dtype=float)
            return positions, timestamps

        positions = events[:, :2] if events.ndim == 2 and events.shape[1] >= 2 else np.zeros((events.shape[0], 2))
        timestamps = events[:, 2] if events.ndim == 2 and events.shape[1] > 2 else np.arange(events.shape[0], dtype=float)
        return positions, timestamps

    def extract_features(self, mouse_events) -> np.ndarray:
        """Extract mouse movement features"""
        positions, timestamps = self._normalize_events(mouse_events)
        if positions.shape[0] < 2:
            return np.zeros(len(self.feature_names))

        # Calculate velocity
        displacements = np.diff(positions, axis=0)
        distances = np.sqrt(np.sum(displacements**2, axis=1))
        time_diffs = np.diff(timestamps)
        time_diffs = np.where(time_diffs == 0, 1, time_diffs)
        velocities = distances / time_diffs

        # Calculate acceleration
        accelerations = np.diff(velocities) if len(velocities) > 1 else np.array([0])

        # Calculate curvature (deviation from straight line)
        if len(positions) > 2:
            angles = np.arctan2(displacements[:, 1], displacements[:, 0])
            angle_changes = np.abs(np.diff(angles))
            curvatures = angle_changes
        else:
            angles = np.array([])
            angle_changes = np.array([])
            curvatures = np.array([0])

        features = []

        # Velocity features
        features.extend([np.mean(velocities), np.std(velocities) or 0])

        # Acceleration features
        features.extend([np.mean(accelerations), np.std(accelerations) or 0])

        # Curvature features
        features.extend([np.mean(curvatures), np.std(curvatures) or 0])

        # Direction changes
        direction_changes = int(np.sum(angle_changes > 0.5)) if len(angle_changes) > 0 else 0
        features.append(direction_changes)

        # Pause duration
        pause_durations = [td for td in time_diffs if td > 0.5]
        features.append(np.mean(pause_durations) if pause_durations else 0)

        # Movement angle
        features.append(np.mean(angles) if len(angles) > 0 else 0)

        # Jitter (small vibrations)
        features.append(np.std(distances) if len(distances) > 1 else 0)

        # Total distance traveled
        features.append(np.sum(distances))

        # Movement duration
        movement_duration = timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0
        features.append(movement_duration)

        return np.array(features[: len(self.feature_names)])
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the mouse movement model"""
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
        
        logger.info(f"Mouse movement model trained and saved to {self.model_path}")
    
    def predict(self, mouse_events: list) -> dict:
        """Predict authenticity based on mouse movement pattern"""
        if self.model is None:
            return {"confidence": 0.5, "is_authentic": False}
        
        features = self.extract_features(mouse_events).reshape(1, -1)
        features_scaled = self.scaler.transform(features)
        
        confidence = self.model.predict_proba(features_scaled)[0][1]
        
        return {
            "confidence": float(confidence),
            "is_authentic": confidence > 0.5,
            "model": "mouse_movement"
        }

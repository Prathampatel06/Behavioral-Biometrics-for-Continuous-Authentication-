import numpy as np
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)

class TouchscreenModel:
    """ML model for touchscreen pattern authentication"""
    
    def __init__(self, model_path: str = None):
        self.model = None
        self.model_path = model_path or "./ml_models/trained_models/touchscreen.pkl"
        self.feature_names = [
            "touch_pressure_mean", "touch_pressure_std",
            "touch_area_mean", "touch_area_std",
            "swipe_speed_mean", "swipe_speed_std",
            "swipe_duration_mean",
            "gesture_type_count",
            "finger_count_max",
            "touch_angle_mean"
        ]
        self.load_model()

    def load_model(self):
        """Load model placeholder from disk"""
        from pathlib import Path
        if Path(self.model_path).exists():
            try:
                self.model = "trained"
                logger.info(f"Loaded touchscreen model placeholder from {self.model_path}")
            except Exception as e:
                logger.warning(f"Could not load touchscreen model: {e}. Will retrain.")
                self.model = None

    def train(self, X_train, y_train):
        """Save touchscreen model placeholder"""
        from pathlib import Path
        Path(self.model_path).parent.mkdir(parents=True, exist_ok=True)
        import joblib
        joblib.dump({
            'model': 'touchscreen_placeholder',
            'feature_names': self.feature_names
        }, self.model_path)
        self.model = 'trained'
        logger.info(f"Touchscreen placeholder model saved to {self.model_path}")
    
    def _normalize_events(self, touch_events):
        """Normalize touchscreen payloads into numeric arrays."""
        if isinstance(touch_events, dict):
            pressures = np.asarray(touch_events.get('pressures', []), dtype=float)
            touch_areas = np.asarray(touch_events.get('areas', []), dtype=float)
            positions = np.asarray(touch_events.get('positions', []), dtype=float)
            timestamps = np.asarray(touch_events.get('timestamps', []), dtype=float)
            return pressures, touch_areas, positions, timestamps

        if isinstance(touch_events, list) and touch_events and isinstance(touch_events[0], dict):
            pressures = np.asarray([event.get('pressure', 0) for event in touch_events], dtype=float)
            touch_areas = np.asarray([event.get('area', 0) for event in touch_events], dtype=float)
            positions = np.asarray([[event.get('x', 0), event.get('y', 0)] for event in touch_events], dtype=float)
            timestamps = np.asarray([event.get('timestamp', idx) for idx, event in enumerate(touch_events)], dtype=float)
            return pressures, touch_areas, positions, timestamps

        events = np.asarray(touch_events)
        if events.ndim == 1:
            return (
                np.asarray([events[0]], dtype=float) if events.size > 0 else np.asarray([], dtype=float),
                np.asarray([events[1]], dtype=float) if events.size > 1 else np.asarray([], dtype=float),
                events[2:4].reshape(-1, 2) if events.size >= 4 else np.zeros((events.size, 2)),
                np.asarray([events[4]], dtype=float) if events.size > 4 else np.arange(events.size, dtype=float)
            )

        pressures = events[:, 0] if events.ndim == 2 and events.shape[1] > 0 else np.asarray([], dtype=float)
        touch_areas = events[:, 1] if events.ndim == 2 and events.shape[1] > 1 else np.asarray([], dtype=float)
        positions = events[:, 2:4] if events.ndim == 2 and events.shape[1] >= 4 else np.zeros((events.shape[0], 2))
        timestamps = events[:, 4] if events.ndim == 2 and events.shape[1] > 4 else np.arange(events.shape[0], dtype=float)
        return pressures, touch_areas, positions, timestamps

    def extract_features(self, touch_events) -> np.ndarray:
        """Extract touchscreen features from touch events"""
        pressures, touch_areas, positions, timestamps = self._normalize_events(touch_events)
        if len(pressures) < 2 and len(touch_areas) < 2 and positions.shape[0] < 2:
            return np.zeros(len(self.feature_names))

        features = []
        
        # Pressure features
        features.extend([np.mean(pressures) if len(pressures) > 0 else 0, np.std(pressures) if len(pressures) > 1 else 0])
        
        # Touch area features
        features.extend([np.mean(touch_areas) if len(touch_areas) > 0 else 0, np.std(touch_areas) if len(touch_areas) > 1 else 0])
        
        # Swipe speed features
        if positions.shape[0] > 1:
            displacements = np.diff(positions, axis=0)
            distances = np.sqrt(np.sum(displacements**2, axis=1))
            time_diffs = np.diff(timestamps) if len(timestamps) > 1 else np.ones(len(distances))
            time_diffs = np.where(time_diffs == 0, 1, time_diffs)
            swipe_speeds = distances / time_diffs
            features.extend([np.mean(swipe_speeds), np.std(swipe_speeds) if len(swipe_speeds) > 1 else 0])
        else:
            features.extend([0, 0])
        
        # Swipe duration
        features.append(timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0)
        
        # Gesture types and finger count (simplified)
        features.append(1)
        
        # Max fingers
        features.append(1)
        
        # Touch angle
        if positions.shape[0] > 1:
            angles = np.arctan2(np.diff(positions[:, 1]), np.diff(positions[:, 0]))
            features.append(np.mean(angles) if len(angles) > 0 else 0)
        else:
            features.append(0)
        
        return np.array(features[: len(self.feature_names)])
    
    def predict(self, touch_events: list) -> dict:
        """Predict authenticity based on touchscreen pattern"""
        features = self.extract_features(touch_events)
        
        # Simplified prediction without trained model
        confidence = 0.5 + 0.3 * (1 - np.std(features) / (np.mean(np.abs(features)) + 1e-6))
        confidence = np.clip(confidence, 0, 1)
        
        return {
            "confidence": float(confidence),
            "is_authentic": confidence > 0.5,
            "model": "touchscreen"
        }

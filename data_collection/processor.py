import numpy as np
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class BiometricDataProcessor:
    """Process raw biometric data for ML model training"""
    
    @staticmethod
    def normalize_features(features: np.ndarray) -> np.ndarray:
        """Normalize feature values to [0, 1] range"""
        min_vals = np.min(features, axis=0)
        max_vals = np.max(features, axis=0)
        
        # Avoid division by zero
        ranges = max_vals - min_vals
        ranges = np.where(ranges == 0, 1, ranges)
        
        normalized = (features - min_vals) / ranges
        return normalized
    
    @staticmethod
    def remove_outliers(features: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """Remove outliers using z-score method"""
        z_scores = np.abs((features - np.mean(features, axis=0)) / (np.std(features, axis=0) + 1e-6))
        return features[np.all(z_scores < threshold, axis=1)]
    
    @staticmethod
    def augment_data(features: np.ndarray, augmentation_factor: int = 2) -> np.ndarray:
        """
        Augment training data by adding small noise
        
        Args:
            features: Original features
            augmentation_factor: How many augmented samples to generate per original
        
        Returns:
            Augmented features combined with original
        """
        augmented = [features]
        
        for _ in range(augmentation_factor - 1):
            noise = np.random.normal(0, 0.01, features.shape)
            augmented.append(features + noise)
        
        return np.vstack(augmented)
    
    @staticmethod
    def extract_statistical_features(raw_events: List[Dict]) -> Dict:
        """Extract statistical features from raw events"""
        if not raw_events:
            return {}
        
        # Extract numerical values from events
        values = []
        for event in raw_events:
            for key, val in event.items():
                if isinstance(val, (int, float)):
                    values.append(val)
        
        if not values:
            return {}
        
        values = np.array(values)
        
        return {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "median": float(np.median(values)),
            "q25": float(np.percentile(values, 25)),
            "q75": float(np.percentile(values, 75)),
            "skewness": float((np.mean(values) - np.median(values)) / (np.std(values) + 1e-6))
        }
    
    @staticmethod
    def prepare_training_batch(
        keystroke_events: List[Dict],
        mouse_events: List[Dict],
        touch_events: List[Dict],
        label: int
    ) -> Dict:
        """
        Prepare a training batch from raw biometric events
        
        Args:
            keystroke_events: List of keystroke events
            mouse_events: List of mouse events
            touch_events: List of touch events
            label: True (1) or imposter (0) label
        
        Returns:
            Dictionary containing processed features and labels
        """
        return {
            "keystroke_features": BiometricDataProcessor.extract_statistical_features(keystroke_events),
            "mouse_features": BiometricDataProcessor.extract_statistical_features(mouse_events),
            "touch_features": BiometricDataProcessor.extract_statistical_features(touch_events),
            "label": label
        }

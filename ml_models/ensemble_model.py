import numpy as np
from ml_models.typing_rhythm_model import TypingRhythmModel
from ml_models.mouse_movement_model import MouseMovementModel
from ml_models.touchscreen_model import TouchscreenModel
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

class EnsembleModel:
    """Ensemble model combining typing, mouse, and touchscreen authentication"""
    
    def __init__(self):
        self.typing_model = TypingRhythmModel()
        self.mouse_model = MouseMovementModel()
        self.touch_model = TouchscreenModel()
        self.weights = settings.ENSEMBLE_WEIGHTS
    
    def predict(self, keystroke_events=None, mouse_events=None, touch_events=None) -> dict:
        """
        Predict user authenticity using ensemble of models
        
        Returns:
            dict with overall confidence and per-model scores
        """
        predictions = {}
        weighted_scores = []
        
        # Get predictions from each model
        if keystroke_events:
            typing_pred = self.typing_model.predict(keystroke_events)
            predictions['typing'] = typing_pred
            weighted_scores.append(typing_pred['confidence'] * self.weights.get('typing_rhythm', 0.4))
        
        if mouse_events:
            mouse_pred = self.mouse_model.predict(mouse_events)
            predictions['mouse'] = mouse_pred
            weighted_scores.append(mouse_pred['confidence'] * self.weights.get('mouse_movement', 0.35))
        
        if touch_events:
            touch_pred = self.touch_model.predict(touch_events)
            predictions['touch'] = touch_pred
            weighted_scores.append(touch_pred['confidence'] * self.weights.get('touchscreen', 0.25))
        
        # Calculate ensemble confidence
        if weighted_scores:
            ensemble_confidence = sum(weighted_scores) / len(weighted_scores)
        else:
            ensemble_confidence = 0.5
        
        # Normalize confidence
        ensemble_confidence = np.clip(ensemble_confidence, 0, 1)
        
        return {
            "ensemble_confidence": float(ensemble_confidence),
            "is_authentic": ensemble_confidence > settings.CONFIDENCE_THRESHOLD,
            "threshold": settings.CONFIDENCE_THRESHOLD,
            "model_predictions": predictions,
            "model": "ensemble"
        }
    
    def get_model_status(self) -> dict:
        """Get status of all models"""
        return {
            "typing_model_loaded": self.typing_model.model is not None,
            "mouse_model_loaded": self.mouse_model.model is not None,
            "ensemble_weights": self.weights
        }

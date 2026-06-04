import numpy as np
import logging
from ml_models.typing_rhythm_model import TypingRhythmModel
from ml_models.mouse_movement_model import MouseMovementModel
from ml_models.touchscreen_model import TouchscreenModel

logger = logging.getLogger(__name__)


def _build_feature_matrix(model, records):
    X = []
    for record in records:
        features = model.extract_features(record)
        if features.size:
            X.append(features)
    return np.vstack(X) if X else np.empty((0, len(model.feature_names)))


def _generate_synthetic_negatives(sample_count, feature_count):
    return np.random.randn(sample_count, feature_count) * 0.25


def train_models_from_enrollment(events):
    """Train biometric models from enrollment events."""
    trained_models = []

    typing_records = [event.features for event in events if event.event_type == "keystroke"]
    mouse_records = [event.features for event in events if event.event_type == "mouse_move"]
    touch_records = [event.features for event in events if event.event_type == "touch"]

    if typing_records:
        logger.info("Preparing typing rhythm training data from enrollment events...")
        typing_model = TypingRhythmModel()
        X_typing = _build_feature_matrix(typing_model, typing_records)
        if X_typing.shape[0] >= 5:
            negative_count = max(10, X_typing.shape[0])
            X_neg = _generate_synthetic_negatives(negative_count, X_typing.shape[1])
            X_train = np.vstack([X_typing, X_neg])
            y_train = np.concatenate([np.ones(X_typing.shape[0]), np.zeros(X_neg.shape[0])])
            typing_model.train(X_train, y_train)
            trained_models.append("typing_rhythm")
        else:
            logger.warning("Not enough typing samples to train the typing rhythm model.")

    if mouse_records:
        logger.info("Preparing mouse movement training data from enrollment events...")
        mouse_model = MouseMovementModel()
        X_mouse = _build_feature_matrix(mouse_model, mouse_records)
        if X_mouse.shape[0] >= 5:
            negative_count = max(10, X_mouse.shape[0])
            X_neg = _generate_synthetic_negatives(negative_count, X_mouse.shape[1])
            X_train = np.vstack([X_mouse, X_neg])
            y_train = np.concatenate([np.ones(X_mouse.shape[0]), np.zeros(X_neg.shape[0])])
            mouse_model.train(X_train, y_train)
            trained_models.append("mouse_movement")
        else:
            logger.warning("Not enough mouse samples to train the mouse movement model.")

    if touch_records:
        logger.info("Preparing touchscreen training data from enrollment events...")
        touch_model = TouchscreenModel()
        X_touch = _build_feature_matrix(touch_model, touch_records)
        if X_touch.shape[0] >= 5:
            negative_count = max(10, X_touch.shape[0])
            X_neg = _generate_synthetic_negatives(negative_count, X_touch.shape[1])
            X_train = np.vstack([X_touch, X_neg])
            y_train = np.concatenate([np.ones(X_touch.shape[0]), np.zeros(X_neg.shape[0])])
            touch_model.train(X_train, y_train)
            trained_models.append("touchscreen")
        else:
            logger.warning("Not enough touch samples to train the touchscreen model.")

    return trained_models


def train_all_models():
    """Train all biometric models with synthetic sample data."""
    logger.info("Generating sample training data...")

    typing_samples = 1000
    X_typing = np.random.rand(typing_samples, 15)
    y_typing = np.random.randint(0, 2, typing_samples)

    mouse_samples = 1000
    X_mouse = np.random.rand(mouse_samples, 12)
    y_mouse = np.random.randint(0, 2, mouse_samples)

    touch_samples = 1000
    X_touch = np.random.rand(touch_samples, 10)
    y_touch = np.random.randint(0, 2, touch_samples)

    logger.info("Training typing rhythm model...")
    typing_model = TypingRhythmModel()
    typing_model.train(X_typing, y_typing)

    logger.info("Training mouse movement model...")
    mouse_model = MouseMovementModel()
    mouse_model.train(X_mouse, y_mouse)

    logger.info("Training touchscreen model placeholder...")
    touch_model = TouchscreenModel()
    touch_model.train(X_touch, y_touch)

    logger.info("All models trained successfully!")


if __name__ == "__main__":
    train_all_models()

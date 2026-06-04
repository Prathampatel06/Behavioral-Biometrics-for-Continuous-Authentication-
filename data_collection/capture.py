import time
import json
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)

class KeyboardCapture:
    """Capture and process keyboard events"""
    
    def __init__(self):
        self.events = []
        self.is_capturing = False
    
    def start_capture(self):
        """Start capturing keyboard events"""
        self.events = []
        self.is_capturing = True
        logger.info("Keyboard capture started")
    
    def stop_capture(self) -> List[Dict]:
        """Stop capturing and return collected events"""
        self.is_capturing = False
        logger.info(f"Keyboard capture stopped. Captured {len(self.events)} events")
        return self.events
    
    def capture_event(self, key_code: int, key_name: str, duration: float, pressure: float = 1.0):
        """
        Capture a single keystroke
        
        Args:
            key_code: Key code from keyboard
            key_name: Name of the key
            duration: How long key was pressed (dwell time)
            pressure: Key pressure (if supported)
        """
        if not self.is_capturing:
            return
        
        event = {
            "timestamp": time.time(),
            "key_code": key_code,
            "key_name": key_name,
            "dwell_time": duration,  # ms
            "pressure": pressure,
            "type": "keystroke"
        }
        self.events.append(event)
    
    def extract_features(self) -> Dict:
        """Extract typing rhythm features from captured events"""
        if len(self.events) < 2:
            return {}
        
        dwell_times = [e['dwell_time'] for e in self.events]
        timestamps = [e['timestamp'] for e in self.events]
        
        # Calculate flight times (intervals between keystrokes)
        flight_times = []
        for i in range(len(timestamps) - 1):
            flight = timestamps[i + 1] - timestamps[i] - dwell_times[i]
            if flight > 0:
                flight_times.append(flight)
        
        features = {
            "dwell_time_mean": np.mean(dwell_times),
            "dwell_time_std": np.std(dwell_times),
            "flight_time_mean": np.mean(flight_times) if flight_times else 0,
            "flight_time_std": np.std(flight_times) if flight_times else 0,
            "keystroke_count": len(self.events),
            "typing_duration": timestamps[-1] - timestamps[0]
        }
        
        return features

class MouseCapture:
    """Capture and process mouse events"""
    
    def __init__(self):
        self.events = []
        self.is_capturing = False
    
    def start_capture(self):
        """Start capturing mouse events"""
        self.events = []
        self.is_capturing = True
        logger.info("Mouse capture started")
    
    def stop_capture(self) -> List[Dict]:
        """Stop capturing and return collected events"""
        self.is_capturing = False
        logger.info(f"Mouse capture stopped. Captured {len(self.events)} events")
        return self.events
    
    def capture_event(self, x: float, y: float, button: str = None, is_movement: bool = False):
        """
        Capture a mouse event
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button (left, right, middle)
            is_movement: Whether this is a movement event
        """
        if not self.is_capturing:
            return
        
        event = {
            "timestamp": time.time(),
            "x": x,
            "y": y,
            "button": button,
            "is_movement": is_movement,
            "type": "mouse_event"
        }
        self.events.append(event)
    
    def extract_features(self) -> Dict:
        """Extract mouse movement features"""
        if len(self.events) < 2:
            return {}
        
        positions = [(e['x'], e['y']) for e in self.events]
        timestamps = [e['timestamp'] for e in self.events]
        
        # Calculate movement distances
        distances = []
        for i in range(len(positions) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i + 1]
            dist = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            distances.append(dist)
        
        # Calculate velocities
        velocities = []
        for i, dist in enumerate(distances):
            time_diff = timestamps[i + 1] - timestamps[i]
            if time_diff > 0:
                velocities.append(dist / time_diff)
        
        features = {
            "velocity_mean": np.mean(velocities) if velocities else 0,
            "velocity_std": np.std(velocities) if velocities else 0,
            "total_distance": sum(distances),
            "movement_count": len(self.events),
            "movement_duration": timestamps[-1] - timestamps[0]
        }
        
        return features

class TouchCapture:
    """Capture and process touch events"""
    
    def __init__(self):
        self.events = []
        self.is_capturing = False
    
    def start_capture(self):
        """Start capturing touch events"""
        self.events = []
        self.is_capturing = True
        logger.info("Touch capture started")
    
    def stop_capture(self) -> List[Dict]:
        """Stop capturing and return collected events"""
        self.is_capturing = False
        logger.info(f"Touch capture stopped. Captured {len(self.events)} events")
        return self.events
    
    def capture_event(
        self,
        x: float,
        y: float,
        pressure: float,
        touch_area: float,
        gesture_type: str = None
    ):
        """
        Capture a touch event
        
        Args:
            x: X coordinate
            y: Y coordinate
            pressure: Touch pressure
            touch_area: Contact area
            gesture_type: Type of gesture (tap, swipe, pinch, etc.)
        """
        if not self.is_capturing:
            return
        
        event = {
            "timestamp": time.time(),
            "x": x,
            "y": y,
            "pressure": pressure,
            "touch_area": touch_area,
            "gesture_type": gesture_type,
            "type": "touch_event"
        }
        self.events.append(event)
    
    def extract_features(self) -> Dict:
        """Extract touch pattern features"""
        if len(self.events) < 2:
            return {}
        
        pressures = [e['pressure'] for e in self.events]
        areas = [e['touch_area'] for e in self.events]
        
        features = {
            "pressure_mean": np.mean(pressures),
            "pressure_std": np.std(pressures),
            "area_mean": np.mean(areas),
            "area_std": np.std(areas),
            "touch_count": len(self.events),
            "touch_duration": self.events[-1]['timestamp'] - self.events[0]['timestamp']
        }
        
        return features

# Import numpy for feature calculations
import numpy as np

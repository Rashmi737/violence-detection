import cv2
import torch
import numpy as np
from collections import deque
import socketio
import time
import threading

# Connect to Flask server
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to Flask server")

@sio.event
def disconnect():
    print("Disconnected from Flask server")

# Simple motion-based detector (works without a trained model)
# We will replace this with the real ML model in a later step
class SimpleViolenceDetector:
    def __init__(self, threshold=25.0, window=10):
        self.threshold = threshold
        self.window = window
        self.motion_scores = deque(maxlen=window)
        self.prev_frame = None

    def analyze_frame(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.prev_frame is None:
            self.prev_frame = gray
            return False, 0.0

        # Calculate difference between frames
        diff = cv2.absdiff(self.prev_frame, gray)
        self.prev_frame = gray

        # Motion score = average pixel change
        score = np.mean(diff)
        self.motion_scores.append(score)

        avg_score = np.mean(self.motion_scores)

        # Normalize to 0-1 confidence
        confidence = min(avg_score / (self.threshold * 2), 1.0)
        is_violent = avg_score > self.threshold

        return is_violent, float(confidence)


def run_detection():
    detector = SimpleViolenceDetector(threshold=25.0)

    # 0 = your webcam, replace with RTSP URL for CCTV
    # Example RTSP: "rtsp://username:password@192.168.1.1:554/stream"
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("ERROR: Could not open webcam")
        return

    print("Webcam opened — starting detection...")
    print("Press Q in the video window to quit")

    try:
        sio.connect("http://localhost:5000")
    except Exception as e:
        print(f"Could not connect to server: {e}")
        print("Start app.py first, then run this script")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Could not read frame")
            break

        is_violent, confidence = detector.analyze_frame(frame)

        # Draw status on the video frame
        color = (0, 0, 255) if is_violent else (0, 255, 0)
        label = f"VIOLENCE DETECTED {confidence:.0%}" if is_violent else f"Normal {confidence:.0%}"
        cv2.putText(frame, label, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        # Draw border color based on detection
        border = 10
        cv2.rectangle(frame, (border, border),
                      (frame.shape[1]-border, frame.shape[0]-border),
                      color, border)

        cv2.imshow("Violence Detection - Press Q to quit", frame)

        # Send alert to server if violence detected
        if is_violent:
            sio.emit("violence_event", {
                "confidence": confidence,
                "timestamp": time.time()
            })

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    sio.disconnect()

if __name__ == "__main__":
    run_detection()
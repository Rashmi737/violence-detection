from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import time
import threading

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Stores last 50 incidents in memory
incidents = []
ALERT_COOLDOWN = 10  # seconds between alerts
last_alert_time = 0

@app.route("/")
def home():
    return jsonify({"status": "Violence Detection Server Running"})

@app.route("/incidents")
def get_incidents():
    return jsonify({"incidents": incidents})

@socketio.on("connect")
def handle_connect():
    print("Dashboard connected")
    emit("status", {"message": "Connected to server"})

@socketio.on("violence_event")
def handle_violence_event(data):
    global last_alert_time
    now = time.time()

    if now - last_alert_time > ALERT_COOLDOWN:
        last_alert_time = now

        # Save incident to memory
        incident = {
            "id": len(incidents) + 1,
            "confidence": data["confidence"],
            "timestamp": data["timestamp"],
            "time_readable": time.strftime(
                "%Y-%m-%d %H:%M:%S",
                time.localtime(data["timestamp"])
            )
        }
        incidents.append(incident)
        if len(incidents) > 50:
            incidents.pop(0)

        # Broadcast alert to all connected dashboards
        emit("alert", incident, broadcast=True)
        print(f"ALERT sent — confidence: {data['confidence']:.1%}")

if __name__ == "__main__":
    print("Starting Violence Detection Server on port 5000...")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
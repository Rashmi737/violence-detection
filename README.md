# AI-Based Violence Detection System

An automated real-time surveillance and alert system that detects violent activities from live camera feeds and broadcasts instant notifications to a web-based security monitoring dashboard.

---

## 📌 Project Overview

The **AI-Based Violence Detection System** bridges continuous video surveillance and rapid emergency alerting. Traditional CCTV setups rely heavily on manual human observation, which is prone to fatigue, oversight, and delayed incident reporting. This project introduces an automated pipeline that continuously analyzes video frames, identifies high-intensity physical movement indicative of violent behavior, logs incidents, and delivers real-time auditory and visual alerts to security operators through an interactive dashboard.

---

## ⚠️ Problem Statement

In public spaces, educational institutions, transit hubs, and private facilities, physical altercations and violent outbreaks often escalate within seconds before security personnel become aware. Relying solely on passive video recording or manual monitoring leads to critical response delays. An automated, real-time detection and alerting mechanism is essential to identify threats immediately, record incident metadata, and enable swift intervention.

---

## 🎯 Project Objectives

- **Automated Real-Time Surveillance:** Continuously capture and inspect video frames from webcams or RTSP-enabled CCTV streams without manual intervention.
- **Accurate Movement & Intensity Analysis:** Detect rapid frame-to-frame pixel variations using computer vision to identify abnormal motion patterns.
- **Instant Event Propagation:** Transmit detection events asynchronously to a central server using lightweight WebSocket connections.
- **Alert Throttling & Cooldown:** Enforce cooldown periods to prevent alert fatigue and notification spamming during ongoing incidents.
- **Operator Dashboard:** Provide security teams with a live web interface featuring real-time connection status, incident metrics, auditory alarms, and detailed event logs.

---

## ✨ Key Features

- **Real-Time Video Stream Processing:** Analyzes live video input frame-by-frame via OpenCV with negligible latency.
- **Visual Status Overlay:** Displays an on-screen HUD on the video stream showing system status ("Normal" in green vs. "VIOLENCE DETECTED" in red), calculated confidence percentage, and prominent color-coded border cues.
- **WebSocket Event Architecture:** Bidirectional real-time communication between the camera detector, the Flask backend, and the React dashboard via Socket.IO.
- **Smart Alert Cooldown:** Built-in 10-second alert cooldown prevents duplicate triggers while maintaining continuous monitoring.
- **Auditory Alert System:** Synthesizes an 880 Hz audible alert tone in the browser using the Web Audio API upon receipt of a new incident.
- **Incident History & Retention:** Retains the last 50 detected incidents in memory with human-readable timestamps and confidence scores.
- **RESTful Endpoints:** Provides HTTP endpoints for health monitoring (`/`) and retrieving incident history (`/incidents`).
- **Responsive Web Dashboard:** Clean, user-friendly monitoring interface showing camera connectivity, total incident counters, last-seen timestamps, and a chronological incident feed.

---

## 🛠️ Technologies Used

### Backend & Computer Vision
- **Python 3.14 / 3.x**
- **OpenCV (`opencv-python`):** Video capture, color space conversion, Gaussian blurring, and absolute frame differencing.
- **NumPy:** Matrix computation and pixel-level motion score aggregation.
- **Flask:** Lightweight web application framework and REST API host.
- **Flask-SocketIO / python-socketio:** Real-time bidirectional WebSocket event broadcasting.
- **Flask-CORS:** Cross-Origin Resource Sharing configuration for frontend-backend communication.
- **PyTorch (`torch`):** Integrated framework prepared for deep learning model extension.

### Frontend Dashboard
- **React 19:** Component-based user interface.
- **Socket.IO Client (`socket.io-client`):** Real-time event handling from the Flask backend.
- **HTML5 Web Audio API:** In-browser audio oscillator generation for alert sound synthesis.
- **Axios:** HTTP client for REST service queries.

---

## 🏗️ System Architecture

```
+-------------------------------------------------------------+
|                      Video Source                           |
|       (Local Webcam [0] or RTSP Network Camera)             |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                detector.py (Computer Vision)                |
|  - Frame Capture (OpenCV)                                   |
|  - Grayscale Conversion & Gaussian Blur                     |
|  - Absolute Frame Differencing (cv2.absdiff)                |
|  - Rolling Window Motion Score (deque maxlen=10)            |
|  - Threshold Evaluation & Confidence Computation            |
|  - On-Screen HUD & Border Color Render                      |
+------------------------------+------------------------------+
                               | Socket.IO: "violence_event"
                               v
+-------------------------------------------------------------+
|                  app.py (Flask Backend)                     |
|  - Port 5000, CORS enabled                                  |
|  - Incident Store (last 50 events)                          |
|  - Alert Cooldown Enforcement (10s window)                  |
|  - Timestamp Generation                                     |
|  - REST Endpoints: GET /, GET /incidents                    |
+------------------------------+------------------------------+
                               | Socket.IO: broadcast "alert"
                               v
+-------------------------------------------------------------+
|              React Frontend (Dashboard)                     |
|  - Port 3000                                                |
|  - Real-Time Connection Indicator (Live / Disconnected)     |
|  - Summary Cards: Total Incidents, Last Detected, Status    |
|  - Audio Chime Trigger (Web Audio API 880 Hz tone)          |
|  - Live Incident Feed with Confidence % & Timestamps        |
+-------------------------------------------------------------+
```

---

## ⚙️ Working Methodology

### 1. Violence Detection Process
1. **Frame Capture & Preprocessing:** Consecutive video frames are converted to grayscale and smoothed with a `(21, 21)` Gaussian blur kernel to eliminate high-frequency camera sensor noise.
2. **Absolute Difference Calculation:** The absolute difference between the previous frame and the current frame (`cv2.absdiff`) isolates regions of movement.
3. **Motion Metric Computation:** The mean pixel change across the difference image produces an instantaneous motion score.
4. **Temporal Window Averaging:** Scores are buffered in a sliding double-ended queue (`deque(maxlen=10)`). The rolling average smoothens sporadic single-frame spikes.
5. **Threshold Verification:** If the rolling average exceeds the calibrated threshold (`25.0`), the event is classified as violent, and confidence is computed proportionally (`min(avg_score / 50.0, 1.0)`).

### 2. Alert Generation & Dispatch Mechanism
1. When violent motion is recognized, `detector.py` emits a `violence_event` payload containing the confidence level and UNIX timestamp to the Flask server.
2. `app.py` checks the timestamp against `ALERT_COOLDOWN` (10 seconds).
3. If the cooldown period has elapsed, the incident is assigned a sequential ID, formatted with a human-readable date and time (`YYYY-MM-DD HH:MM:SS`), and appended to the in-memory log.
4. The server broadcasts the `alert` event to all active dashboard clients simultaneously.

### 3. Monitoring & Notification
1. The React dashboard receives the `alert` event via its WebSocket listener.
2. The browser automatically synthesizes a 0.3-second 880 Hz beep using the Web Audio API to notify operators.
3. The dashboard increments the total incident counter, updates the "Last Detected" timer, and prepends the incident to the top of the feed with high-visibility alert styling.

---

## 📂 Project Structure

```
violence-detection/
├── backend/
│   ├── app.py                 # Flask server with Socket.IO event handlers & REST endpoints
│   ├── detector.py            # Real-time OpenCV motion analysis & camera feed processor
│   ├── requirements.txt       # Python dependencies for the backend
│   ├── clips/                 # Directory reserved for recorded video clips (.gitkeep)
│   ├── model/                 # Directory reserved for deep learning weights (.gitkeep)
│   └── utils/                 # Directory reserved for utility scripts (.gitkeep)
├── frontend/
│   └── dashboard/
│       ├── public/            # Public static assets, index.html, favicon, manifest
│       ├── src/
│       │   ├── App.js         # Core dashboard interface, WebSocket handler, and audio alert
│       │   ├── App.css        # Dashboard styling rules
│       │   ├── index.js       # React root DOM renderer
│       │   └── index.css      # Base typography and page layout styles
│       ├── package.json       # React dependencies and scripts
│       └── package-lock.json  # NPM dependency lockfile
├── .gitignore                 # Comprehensive Git exclusion rules
└── README.md                  # Project documentation
```

---

## 🚀 Installation & Setup Instructions

### Prerequisites
- **Python 3.10+** (Python 3.14 supported)
- **Node.js 18+** and **npm**
- A functional **webcam** or an RTSP network camera stream

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/Rashmi737/violence-detection.git
cd violence-detection
```

---

### Step 2: Backend Setup

1. Open a terminal and navigate to the `backend` folder:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   - **Windows:**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

### Step 3: Frontend Dashboard Setup

1. Open a second terminal and navigate to the frontend directory:
   ```bash
   cd frontend/dashboard
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

---

## 🖥️ How to Run the Project

Run the components in the following order:

### 1. Start the Flask Backend Server
In the backend terminal (with virtual environment active):
```bash
python app.py
```
*The server will start on `http://localhost:5000`.*

### 2. Start the React Security Dashboard
In the frontend terminal:
```bash
npm start
```
*The dashboard will automatically open in your browser at `http://localhost:3000`.*  
*Verify that the status pill in the top-right shows **● Live**.*

### 3. Launch Camera Detection
In a third terminal (with virtual environment active in the `backend` folder):
```bash
python detector.py
```
- A video window titled **"Violence Detection - Press Q to quit"** will appear displaying your camera feed.
- Move or simulate sudden rapid movements in front of the camera to trigger violence alerts.
- Press **Q** in the camera window to safely stop the detection stream.

---

## 📊 Expected Output

- **Detector Window:**
  - **Normal State:** Green border box around the frame with label `Normal [confidence%]`.
  - **Violence Detected State:** Bright red border box around the frame with label `VIOLENCE DETECTED [confidence%]`.
- **Backend Console:**
  - `ALERT sent — confidence: XX.X%` with incident logging.
- **Frontend Dashboard:**
  - Real-time connection badge switches to green **● Live**.
  - Audible chime plays upon incident detection.
  - Incident cards display the incident number, confidence percentage, and timestamp in reverse chronological order.

---

## 🔮 Future Enhancements

- **Deep Learning Action Recognition:** Integration of 3D-CNN / MobileNet-LSTM models in the `model/` directory for classification of complex violence patterns beyond optical motion.
- **Automated Clip Archival:** Automatic saving of 10-second video clips of detected incidents to `backend/clips/`.
- **SMS & Email Alerts:** Notification integration via Twilio or SMTP to alert off-site administrators instantly.
- **Multi-Camera Management:** Dashboard interface to support simultaneous multi-RTSP camera grid monitoring.
- **Persistent Database:** Integration of SQLite/PostgreSQL to persist incident history across server restarts.

---

## 📄 License

This project is developed for educational and security research purposes.

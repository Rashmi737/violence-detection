import { useEffect, useState } from "react";
import { io } from "socket.io-client";

const socket = io("http://localhost:5000");

function App() {
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);
  const [stats, setStats] = useState({ total: 0, lastSeen: "Never" });

  useEffect(() => {
    socket.on("connect", () => setConnected(true));
    socket.on("disconnect", () => setConnected(false));

    socket.on("alert", (data) => {
      // Play a beep sound
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      osc.connect(ctx.destination);
      osc.frequency.value = 880;
      osc.start();
      osc.stop(ctx.currentTime + 0.3);

      setAlerts((prev) => [data, ...prev].slice(0, 50));
      setStats((prev) => ({
        total: prev.total + 1,
        lastSeen: data.time_readable,
      }));
    });

    return () => {
      socket.off("connect");
      socket.off("disconnect");
      socket.off("alert");
    };
  }, []);

  return (
    <div style={{ fontFamily: "sans-serif", padding: "24px", maxWidth: "900px", margin: "0 auto" }}>
      
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "22px", fontWeight: 500 }}>Violence Detection Dashboard</h1>
          <p style={{ margin: "4px 0 0", fontSize: "13px", color: "#888" }}>Live monitoring system</p>
        </div>
        <div style={{
          padding: "6px 14px",
          borderRadius: "20px",
          fontSize: "13px",
          fontWeight: 500,
          background: connected ? "#dcfce7" : "#fee2e2",
          color: connected ? "#16a34a" : "#dc2626"
        }}>
          {connected ? "● Live" : "○ Disconnected"}
        </div>
      </div>

      {/* Stats row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "12px", marginBottom: "24px" }}>
        {[
          { label: "Total Incidents", value: stats.total },
          { label: "Last Detected", value: stats.lastSeen },
          { label: "Camera Status", value: connected ? "Online" : "Offline" },
        ].map((s) => (
          <div key={s.label} style={{
            background: "#f9f9f9",
            border: "0.5px solid #e5e5e5",
            borderRadius: "10px",
            padding: "16px"
          }}>
            <p style={{ margin: "0 0 6px", fontSize: "12px", color: "#888" }}>{s.label}</p>
            <p style={{ margin: 0, fontSize: "20px", fontWeight: 500 }}>{s.value}</p>
          </div>
        ))}
      </div>

      {/* Alert feed */}
      <h2 style={{ fontSize: "15px", fontWeight: 500, marginBottom: "12px" }}>
        Incident Feed
      </h2>

      {alerts.length === 0 ? (
        <div style={{
          textAlign: "center",
          padding: "48px",
          color: "#aaa",
          border: "0.5px dashed #ddd",
          borderRadius: "10px",
          fontSize: "14px"
        }}>
          No incidents detected yet — monitoring is active
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
          {alerts.map((a, i) => (
            <div key={i} style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              padding: "14px 18px",
              background: "#fff5f5",
              border: "0.5px solid #fecaca",
              borderLeft: "4px solid #ef4444",
              borderRadius: "8px"
            }}>
              <div>
                <p style={{ margin: "0 0 4px", fontWeight: 500, color: "#991b1b", fontSize: "14px" }}>
                  Violence Detected
                </p>
                <p style={{ margin: 0, fontSize: "12px", color: "#b91c1c" }}>
                  Confidence: {(a.confidence * 100).toFixed(1)}%
                </p>
              </div>
              <div style={{ textAlign: "right" }}>
                <p style={{ margin: 0, fontSize: "12px", color: "#f87171" }}>
                  {a.time_readable}
                </p>
                <p style={{ margin: "4px 0 0", fontSize: "11px", color: "#fca5a5" }}>
                  Incident #{a.id}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
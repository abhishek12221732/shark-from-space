import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { HeatmapLayer } from 'react-leaflet-heatmap-layer-v3'; // <-- Use named import
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './App.css'; // <-- Re-enabled CSS

// We can leave the icon fix commented out for now unless markers break
// import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
// import markerIcon from 'leaflet/dist/images/marker-icon.png';
// import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// delete L.Icon.Default.prototype._getIconUrl;
// L.Icon.Default.mergeOptions({
//   iconRetinaUrl: markerIcon2x,
//   iconUrl: markerIcon,
//   shadowUrl: markerShadow,
// });


function App() {
  const [apiStatus, setApiStatus] = useState('Connecting...');
  const [liveEvents, setLiveEvents] = useState([]); // <-- Holds tag data
  const [hotspots, setHotspots] = useState([]); // <-- Holds ML predictions

  // Base map position
  const mapPosition = [-13.00, 46.23];

  // --- Data Fetching ---

  // 1. Fetch API Status
  useEffect(() => {
    fetch('http://127.0.0.1:8000/') // Hit your backend's root
      .then(response => response.json())
      .then(data => setApiStatus(data.status || 'Connected'))
      .catch(() => setApiStatus('Error: Could not connect to API'));
  }, []);

  // 2. Fetch Live Tag Events (Polling)
  useEffect(() => {
    const fetchEvents = () => {
      fetch('http://127.0.0.1:8000/events')
        .then(response => {
          if (!response.ok) {
            // Handle HTTP errors (e.g., 500)
            return { status: 'error', events: [] };
          }
          return response.json();
        })
        .then(data => {
          if (data.status === 'success' && data.events) {
            setLiveEvents(data.events);
          } else {
            // Handle error or empty response
            setLiveEvents([]);
          }
        })
        .catch(error => {
          console.error("Error fetching events:", error);
          setLiveEvents([]);
        });
    };

    fetchEvents(); // Fetch immediately on load
    const interval = setInterval(fetchEvents, 5000); // Poll every 5 seconds
    return () => clearInterval(interval); // Cleanup on unmount
  }, []);

  // 3. Fetch Hotspot Predictions (Once on load)
  useEffect(() => {
    const fetchHotspots = async () => {
      try {
        // Try simulated hotspots first
        const response = await fetch('http://127.0.0.1:8000/hotspots');
        
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success' && data.hotspots) {
            // Format for the heatmap: [lat, lon, intensity]
            const formattedHotspots = data.hotspots.map(h => [
              h.latitude,
              h.longitude,
              h.prediction_value,
            ]);
            setHotspots(formattedHotspots);
            return;
          }
        }
        
        // Fallback to real ML predictions if simulated fails
        const realResponse = await fetch('http://127.0.0.1:8000/hotspots/real');
        if (realResponse.ok) {
          const realData = await realResponse.json();
          if (realData.status === 'success' && realData.hotspots) {
            const formattedHotspots = realData.hotspots.map(h => [
              h.latitude,
              h.longitude,
              h.prediction_value,
            ]);
            setHotspots(formattedHotspots);
          }
        }
      } catch (error) {
        console.error("Error fetching hotspots:", error);
        setHotspots([]);
      }
    };

    fetchHotspots();
  }, []);


  return (
    <div className="app-container">
      <aside className="sidebar">
        <h1 className="title">Shark Foraging Dashboard</h1>
        
        <div className="sidebar-section">
          <h2>Controls</h2>
          <label htmlFor="model-select">Select Model</label>
          <select id="model-select">
            <option>Model A (XGBoost)</option>
            <option>Baseline (Logistic)</option>
          </select>

          <label htmlFor="date-select">Select Date</label>
          <input type="date" id="date-select" />
        </div>

        <div className="sidebar-section">
          <h2>Live Tag Events</h2>
          {liveEvents.length === 0 ? (
            <p>No live events...</p>
          ) : (
            // Use .slice(0, 10) to only show the 10 most recent
            liveEvents.slice(0, 10).map(evt => (
              <div key={evt.id} className="event-card">
                <strong>Tag {evt.tag_id}:</strong> {evt.event_trigger}
              </div>
            ))
          )}
        </div>

        <div className="sidebar-section">
            <h2>API Status</h2>
            <p className="api-status">{apiStatus}</p>
        </div>
      </aside>
      
      <main className="map-view">
        <MapContainer center={mapPosition} zoom={13} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />

          {/* --- ADD THE HEATMAP LAYER --- */}
          {hotspots.length > 0 && (
            <HeatmapLayer
              points={hotspots}
              longitudeExtractor={m => m[1]}
              latitudeExtractor={m => m[0]}
              intensityExtractor={m => m[2]}
              radius={30}
              blur={20}
              max={1.0}
            />
          )}

          {/* --- RENDER THE LIVE TAGS --- */}
          {liveEvents.map(evt => (
             <Marker key={evt.id} position={[evt.latitude, evt.longitude]}>
               <Popup>
                 <strong>Tag {evt.tag_id}</strong><br />
                 Event: {evt.event_trigger}<br />
                 Confidence: {evt.event_confidence}<br />
                 Timestamp: {new Date(evt.timestamp).toLocaleString()}
               </Popup>
             </Marker>
          ))}
        </MapContainer>
      </main>
    </div>
  );
}

export default App;


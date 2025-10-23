import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './App.css';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';


// Fix for default marker icon issue with webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});


function App() {
  const [apiStatus, setApiStatus] = useState('Connecting...');

  // Dummy data for map (from your report)
  const mapPosition = [-13.00, 46.23]; 
  const dummyEvents = [
    { id: 'SHK001', pos: [-13.004, 46.237], event: 'Possible Feeding (0.87)' },
    { id: 'SHK002', pos: [-13.010, 46.240], event: 'Transiting' },
  ];

  // Test API connection on load
  useEffect(() => {
    fetch('http://127.0.0.1:8000/') // Hit your backend's root
      .then(response => response.json())
      .then(data => setApiStatus(data.status || 'Connected'))
      .catch(() => setApiStatus('Error: Could not connect to API'));
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
          {dummyEvents.map(evt => (
            <div key={evt.id} className="event-card">
              <strong>Tag {evt.id}:</strong> {evt.event}
            </div>
          ))}
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
          {dummyEvents.map(evt => (
             <Marker key={evt.id} position={evt.pos}>
               <Popup>
                 <strong>Tag {evt.id}</strong><br />{evt.event}
               </Popup>
             </Marker>
          ))}
        </MapContainer>
      </main>
    </div>
  );
}

export default App;
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMap, Polyline } from 'react-leaflet';
import { HeatmapLayer } from 'react-leaflet-heatmap-layer-v3';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// --- LEAFLET ICON FIX ---
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// --- LIGHT MODE INLINE STYLES ---
const styles = {
  container: {
    display: 'flex', height: '100vh', width: '100vw',
    fontFamily: '"Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    backgroundColor: '#f8fafc', color: '#0f172a', overflow: 'hidden',
  },
  sidebar: {
    width: '350px', backgroundColor: '#ffffff', borderRight: '1px solid #e2e8f0',
    display: 'flex', flexDirection: 'column', padding: '20px', zIndex: 1000,
    boxShadow: '2px 0 10px rgba(0,0,0,0.05)',
  },
  header: { marginBottom: '20px', borderBottom: '1px solid #e2e8f0', paddingBottom: '15px' },
  title: { fontSize: '1.5rem', fontWeight: 'bold', color: '#0284c7', margin: 0 },
  subtitle: { fontSize: '0.85rem', color: '#64748b', marginTop: '5px' },
  statusCard: {
    backgroundColor: '#f1f5f9', padding: '15px', borderRadius: '8px',
    marginBottom: '15px', border: '1px solid #e2e8f0', display: 'flex',
    justifyContent: 'space-between', alignItems: 'center',
  },
  statusIndicator: (isOnline) => ({
    height: '10px', width: '10px', borderRadius: '50%',
    backgroundColor: isOnline ? '#22c55e' : '#ef4444', display: 'inline-block',
    marginRight: '8px', boxShadow: isOnline ? '0 0 8px #22c55e' : 'none',
  }),
  sectionTitle: {
    fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px',
    color: '#475569', marginTop: '10px', marginBottom: '10px', fontWeight: '600',
  },
  eventList: { flex: 1, overflowY: 'auto', marginTop: '10px', paddingRight: '5px' },
  eventCard: (type) => ({
    backgroundColor: type === 'possible_feeding' ? '#fef3c7' : '#f8fafc',
    borderLeft: type === 'possible_feeding' ? '4px solid #f59e0b' : '4px solid #0ea5e9',
    border: type === 'possible_feeding' ? '1px solid #fde68a' : '1px solid #e2e8f0',
    borderLeftWidth: '4px',
    padding: '12px', borderRadius: '4px', marginBottom: '10px', fontSize: '0.9rem',
  }),
  mapWrapper: { flex: 1, position: 'relative' },
  validationCard: {
    backgroundColor: '#f1f5f9', border: '1px solid #e2e8f0', borderRadius: '6px',
    padding: '12px', marginBottom: '20px'
  },
  // --- NEW: RIGHT TRACKING PANEL STYLES ---
  trackerPanel: {
    position: 'absolute', top: '20px', right: '20px', width: '320px',
    backgroundColor: '#ffffff', borderRadius: '12px', padding: '20px',
    boxShadow: '0 10px 25px rgba(0,0,0,0.1)', zIndex: 1000,
    border: '1px solid #e2e8f0', display: 'flex', flexDirection: 'column',
    maxHeight: 'calc(100vh - 40px)'
  },
  closeBtn: {
    position: 'absolute', top: '15px', right: '15px', background: 'none',
    border: 'none', fontSize: '1.2rem', cursor: 'pointer', color: '#94a3b8'
  },
  statGrid: {
    display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginBottom: '15px'
  },
  statBox: {
    backgroundColor: '#f8fafc', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0'
  },
  statLabel: { fontSize: '0.7rem', color: '#64748b', textTransform: 'uppercase' },
  statValue: { fontSize: '1.1rem', fontWeight: 'bold', color: '#0f172a' },
  historyList: {
    flex: 1, overflowY: 'auto', borderTop: '1px solid #e2e8f0', paddingTop: '10px',
    fontSize: '0.8rem', color: '#475569'
  },
  historyItem: {
    padding: '8px 0', borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between'
  }
};

// --- DYNAMIC RECENTER BUTTON COMPONENT ---
function RecenterButton({ sharks, fallbackCenter }) {
  const map = useMap();

  const handleRecenter = () => {
    if (sharks && sharks.length > 0) {
      const bounds = L.latLngBounds(sharks.map(s => [s.latitude, s.longitude]));
      map.flyToBounds(bounds, { padding: [80, 80], duration: 1.5, maxZoom: 13 });
    } else {
      map.flyTo(fallbackCenter, 11, { duration: 1.5 });
    }
  };

  return (
    <button
      onClick={handleRecenter}
      style={{
        position: 'absolute', bottom: '30px', right: '20px', zIndex: 1000, // Moved to bottom right
        padding: '10px 20px', backgroundColor: '#0284c7', color: '#ffffff',
        border: 'none', borderRadius: '6px', cursor: 'pointer',
        boxShadow: '0 4px 6px rgba(2, 132, 199, 0.3)', fontWeight: 'bold', display: 'flex', gap: '6px'
      }}
    >
      🎯 Frame All Sharks
    </button>
  );
}

function App() {
  // API URL configuration
  const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
  
  const [apiStatus, setApiStatus] = useState('Connecting...');
  const [isOnline, setIsOnline] = useState(false);
  const [liveEvents, setLiveEvents] = useState([]);
  
  const [mlHotspots, setMlHotspots] = useState([]);
  const [truthHotspots, setTruthHotspots] = useState([]);
  const [activeLayer, setActiveLayer] = useState('ml');
  const [loadingLayer, setLoadingLayer] = useState(true);
  
  // --- NEW: SELECTED SHARK STATE ---
  const [selectedSharkId, setSelectedSharkId] = useState(null);
  
  // --- SIMULATOR CONTROL STATE ---
  const [simulatorRunning, setSimulatorRunning] = useState(false);
  const [simulatorLoading, setSimulatorLoading] = useState(false);
  
  const centerPos = [-13.00, 46.23];

  useEffect(() => {
    const checkHealth = () => {
      fetch(`${API_URL}/`)
        .then(res => res.json())
        .then(data => { setApiStatus(data.status || 'Connected'); setIsOnline(true); })
        .catch(() => { setApiStatus('Offline'); setIsOnline(false); });
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchHotspots = async () => {
      setLoadingLayer(true);
      try {
        const mlRes = await fetch(`${API_URL}/hotspots/real`);
        if (mlRes.ok) {
          const data = await mlRes.json();
          if (data.status === 'success' && data.hotspots) {
            setMlHotspots(data.hotspots.map(h => [h.latitude, h.longitude, h.prediction_value]));
          }
        }

        const truthRes = await fetch(`${API_URL}/hotspots/truth`);
        if (truthRes.ok) {
          const tData = await truthRes.json();
          if (tData.status === 'success' && tData.hotspots) {
            setTruthHotspots(tData.hotspots.map(h => [h.latitude, h.longitude, h.prediction_value]));
          }
        }
      } catch (err) {
        console.error("Failed to load map data:", err);
      } finally {
        setLoadingLayer(false);
      }
    };
    fetchHotspots();
  }, []);

  useEffect(() => {
    const fetchEvents = () => {
      // BUMPED LIMIT TO 200 to get a good tail of historical data for the path
      fetch(`${API_URL}/events?limit=200`)
        .then(res => res.ok ? res.json() : { events: [] })
        .then(data => { if (data.events) setLiveEvents(data.events); })
        .catch(err => console.error("Event polling error:", err));
    };
    fetchEvents();
    const interval = setInterval(fetchEvents, 2000);
    return () => clearInterval(interval);
  }, []);

  const uniqueSharks = Array.from(new Set(liveEvents.map(e => e.tag_id)))
    .map(id => liveEvents.find(e => e.tag_id === id));

  // --- NEW: FILTER SELECTED SHARK DATA ---
  const selectedSharkEvents = selectedSharkId 
    ? liveEvents.filter(e => e.tag_id === selectedSharkId).sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
    : [];
  const activeShark = selectedSharkEvents[0]; // Most recent data point
  const sharkPath = selectedSharkEvents.map(e => [e.latitude, e.longitude]); // Array of coords for the trail

  // --- SIMULATOR CONTROL HANDLERS ---
  const startSimulator = async () => {
    setSimulatorLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/simulator/start`, { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setSimulatorRunning(true);
        console.log("Simulator started:", data);
      } else {
        console.error("Failed to start simulator:", data.detail);
      }
    } catch (err) {
      console.error("Error starting simulator:", err);
    } finally {
      setSimulatorLoading(false);
    }
  };

  const stopSimulator = async () => {
    setSimulatorLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/simulator/stop`, { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setSimulatorRunning(false);
        console.log("Simulator stopped:", data);
      } else {
        console.error("Failed to stop simulator:", data.detail);
      }
    } catch (err) {
      console.error("Error stopping simulator:", err);
    } finally {
      setSimulatorLoading(false);
    }
  };

  // Check simulator status on mount
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await fetch(`${API_URL}/api/v1/simulator/status`);
        const data = await res.json();
        if (data.is_running) {
          setSimulatorRunning(true);
        }
      } catch (err) {
        console.error("Error checking simulator status:", err);
      }
    };
    checkStatus();
  }, []);

  return (
    <div style={styles.container}>
      <aside style={styles.sidebar}>
        <div style={styles.header}>
          <h1 style={styles.title}>SharkTrack AI</h1>
          <div style={styles.subtitle}>Predictive Foraging Habitat Monitor</div>
        </div>

        <div style={styles.statusCard}>
          <div>
            <div style={styles.statusIndicator(isOnline)}></div>
            <span style={{fontWeight: 'bold', fontSize: '0.9rem', color: '#0f172a'}}>
              {isOnline ? "System Operational" : "System Offline"}
            </span>
          </div>
          <div style={{fontSize: '0.8rem', color: '#64748b'}}>v1.0.0</div>
        </div>

        <div style={styles.sectionTitle}>Data Overlays</div>
        <div style={{display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '15px'}}>
           <label style={{cursor: 'pointer', display: 'flex', alignItems: 'center'}}>
             <input type="radio" checked={activeLayer === 'ml'} onChange={() => setActiveLayer('ml')} />
             <span style={{marginLeft: '8px', color: activeLayer === 'ml' ? '#0284c7' : '#475569', fontWeight: activeLayer === 'ml' ? '600' : '400'}}>Predicted Habitat (XGBoost)</span>
           </label>
           <label style={{cursor: 'pointer', display: 'flex', alignItems: 'center'}}>
             <input type="radio" checked={activeLayer === 'truth'} onChange={() => setActiveLayer('truth')} />
             <span style={{marginLeft: '8px', color: activeLayer === 'truth' ? '#16a34a' : '#475569', fontWeight: activeLayer === 'truth' ? '600' : '400'}}>Historical Ground Truth (2020)</span>
           </label>
           <label style={{cursor: 'pointer', display: 'flex', alignItems: 'center'}}>
             <input type="radio" checked={activeLayer === 'none'} onChange={() => setActiveLayer('none')} />
             <span style={{marginLeft: '8px', color: '#64748b'}}>Hide Heatmap</span>
           </label>
        </div>
        {loadingLayer && <div style={{fontSize: '0.8rem', color: '#d97706', marginBottom: '10px'}}>Loading Datasets...</div>}

        <div style={styles.validationCard}>
           <div style={{fontSize: '0.8rem', color: '#64748b', marginBottom: '4px'}}>Model Validation Score</div>
           <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: '#16a34a'}}>84.2%</div>
           <div style={{fontSize: '0.75rem', color: '#475569', marginTop: '2px', marginBottom: '10px'}}>Spatial Correlation vs Historical Data</div>
           
           <div>
              <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#475569'}}>
                 <span>ML Confidence</span><span>88%</span>
              </div>
              <div style={{height: '4px', backgroundColor: '#cbd5e1', borderRadius: '2px', marginTop: '4px', marginBottom: '8px'}}>
                 <div style={{height: '100%', width: '88%', backgroundColor: '#0ea5e9', borderRadius: '2px'}}></div>
              </div>

              <div style={{display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#475569'}}>
                 <span>Historical Overlap</span><span>84%</span>
              </div>
              <div style={{height: '4px', backgroundColor: '#cbd5e1', borderRadius: '2px', marginTop: '4px'}}>
                 <div style={{height: '100%', width: '84%', backgroundColor: '#22c55e', borderRadius: '2px'}}></div>
              </div>
           </div>
        </div>

        <div style={styles.sectionTitle}>Global Event Feed</div>
        <div style={styles.eventList}>
          {liveEvents.length === 0 ? (
             <div style={{color: '#94a3b8', fontStyle: 'italic'}}>Waiting for sensor data...</div>
          ) : (
            // Only show the last 15 overall events in the sidebar
            liveEvents.slice(0, 15).map((evt) => (
              <div 
                key={evt.id} 
                style={{...styles.eventCard(evt.event_trigger), cursor: 'pointer', opacity: selectedSharkId && selectedSharkId !== evt.tag_id ? 0.5 : 1}}
                onClick={() => setSelectedSharkId(evt.tag_id)} // Clicking feed also selects shark
              >
                <div style={{display:'flex', justifyContent:'space-between', marginBottom:'4px'}}>
                  <strong style={{color: '#0f172a'}}>{evt.tag_id}</strong>
                  <span style={{fontSize: '0.75rem', color: '#64748b'}}>
                    {new Date(evt.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div style={{fontSize: '0.85rem', color: '#334155'}}>
                  {evt.event_trigger === 'possible_feeding' ? '🍖 FEEDING EVENT' : '🏊 Transiting'}
                </div>
              </div>
            ))
          )}
        </div>
      </aside>

      <main style={styles.mapWrapper}>
        {/* Simulator Toggle Button - Top Right */}
        <button
          onClick={simulatorRunning ? stopSimulator : startSimulator}
          disabled={simulatorLoading}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            zIndex: 1000,
            padding: '12px 24px',
            backgroundColor: simulatorRunning ? '#ef4444' : '#22c55e',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',
            cursor: simulatorLoading ? 'not-allowed' : 'pointer',
            fontSize: '0.9rem',
            fontWeight: '700',
            opacity: simulatorLoading ? 0.7 : 1,
            transition: 'all 0.3s ease',
            boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          {simulatorLoading ? (
            <>⏳ ...</>
          ) : simulatorRunning ? (
            <>⏹ Stop Simulator</>
          ) : (
            <>▶ Start Simulator</>
          )}
        </button>

        <MapContainer 
          center={centerPos} 
          zoom={11} 
          zoomSnap={0.25} 
          zoomDelta={0.5} 
          wheelPxPerZoomLevel={120} 
          style={{ height: '100%', width: '100%' }}
        >
          <RecenterButton sharks={uniqueSharks} fallbackCenter={centerPos} />

          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; OpenStreetMap contributors &copy; CARTO'
          />

          {activeLayer === 'ml' && mlHotspots.length > 0 && (
            <HeatmapLayer
              points={mlHotspots}
              longitudeExtractor={m => m[1]}
              latitudeExtractor={m => m[0]}
              intensityExtractor={m => m[2]}
              radius={80}
              blur={60}
              max={1.0}
              minOpacity={0.05}
              maxOpacity={0.5}
              gradient={{0.3: '#93c5fd', 0.6: '#4ade80', 0.8: '#facc15', 1.0: '#ef4444'}}
            />
          )}

          {activeLayer === 'truth' && truthHotspots.length > 0 && (
            <HeatmapLayer
              points={truthHotspots}
              longitudeExtractor={m => m[1]}
              latitudeExtractor={m => m[0]}
              intensityExtractor={m => m[2]}
              radius={80}
              blur={60}
              max={1.0}
              minOpacity={0.05}
              maxOpacity={0.5}
              gradient={{0.3: '#a7f3d0', 0.6: '#34d399', 0.8: '#10b981', 1.0: '#047857'}}
            />
          )}

          {/* --- NEW: SHARK PATH POLYLINE --- */}
          {selectedSharkId && sharkPath.length > 1 && (
            <Polyline 
              positions={sharkPath} 
              color="#0284c7" 
              weight={3} 
              dashArray="5, 10" 
              opacity={0.8}
            />
          )}

          {uniqueSharks.map(evt => (
             <Marker 
                key={evt.tag_id} 
                position={[evt.latitude, evt.longitude]}
                // Replaced Popup with click handler
                eventHandlers={{
                  click: () => {
                    setSelectedSharkId(evt.tag_id);
                  },
                }}
             />
          ))}
        </MapContainer>

        {/* --- NEW: RIGHT TRACKING PANEL --- */}
        {selectedSharkId && activeShark && (
          <div style={styles.trackerPanel}>
            <button style={styles.closeBtn} onClick={() => setSelectedSharkId(null)}>✖</button>
            <h2 style={{margin: '0 0 5px 0', fontSize: '1.4rem', color: '#0f172a'}}>Target: {activeShark.tag_id}</h2>
            
            <div style={{display: 'inline-block', backgroundColor: activeShark.event_trigger === 'possible_feeding' ? '#fef3c7' : '#e0f2fe', color: activeShark.event_trigger === 'possible_feeding' ? '#b45309' : '#0369a1', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', fontWeight: 'bold', marginBottom: '15px', alignSelf: 'flex-start'}}>
              {activeShark.event_trigger === 'possible_feeding' ? '🍖 FEEDING' : '🏊 TRANSITING'}
            </div>

            <div style={styles.statGrid}>
              <div style={styles.statBox}>
                <div style={styles.statLabel}>Current Depth</div>
                <div style={styles.statValue}>{activeShark.depth_m}m</div>
              </div>
              <div style={styles.statBox}>
                <div style={styles.statLabel}>Water Temp</div>
                <div style={styles.statValue}>{activeShark.env_temperature_c}°C</div>
              </div>
              <div style={styles.statBox}>
                <div style={styles.statLabel}>Battery</div>
                <div style={styles.statValue}>{activeShark.battery_level_pct}%</div>
              </div>
              <div style={styles.statBox}>
                <div style={styles.statLabel}>ML Confidence</div>
                <div style={styles.statValue}>{(activeShark.event_confidence * 100).toFixed(0)}%</div>
              </div>
            </div>

            <div style={{fontSize: '0.85rem', fontWeight: 'bold', color: '#0f172a', marginBottom: '5px'}}>Recent Path History</div>
            <div style={styles.historyList}>
              {selectedSharkEvents.map((e, idx) => (
                <div key={idx} style={styles.historyItem}>
                  <span>{new Date(e.timestamp).toLocaleTimeString()}</span>
                  <span style={{fontFamily: 'monospace'}}>[{e.latitude.toFixed(3)}, {e.longitude.toFixed(3)}]</span>
                </div>
              ))}
            </div>
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
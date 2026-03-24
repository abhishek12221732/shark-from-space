import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { HeatmapLayer } from 'react-leaflet-heatmap-layer-v3';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// --- 1. LEAFLET ICON FIX (CRITICAL) ---
// This fixes the issue where markers appear as broken images
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// --- 2. INLINE STYLES (For a Dark Mode Dashboard) ---
// We use a style object here to ensure the UI looks good even without external CSS files.
const styles = {
  container: {
    display: 'flex',
    height: '100vh',
    width: '100vw',
    fontFamily: '"Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    backgroundColor: '#0f172a', // Dark slate
    color: '#f8fafc', // Light text
    overflow: 'hidden',
  },
  sidebar: {
    width: '350px',
    backgroundColor: '#1e293b', // Slightly lighter slate
    borderRight: '1px solid #334155',
    display: 'flex',
    flexDirection: 'column',
    padding: '20px',
    zIndex: 1000,
    boxShadow: '2px 0 10px rgba(0,0,0,0.3)',
  },
  header: {
    marginBottom: '20px',
    borderBottom: '1px solid #334155',
    paddingBottom: '15px',
  },
  title: {
    fontSize: '1.5rem',
    fontWeight: 'bold',
    color: '#38bdf8', // Light blue
    margin: 0,
  },
  subtitle: {
    fontSize: '0.85rem',
    color: '#94a3b8',
    marginTop: '5px',
  },
  statusCard: {
    backgroundColor: '#0f172a',
    padding: '15px',
    borderRadius: '8px',
    marginBottom: '20px',
    border: '1px solid #334155',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  statusIndicator: (isOnline) => ({
    height: '10px',
    width: '10px',
    borderRadius: '50%',
    backgroundColor: isOnline ? '#22c55e' : '#ef4444', // Green or Red
    display: 'inline-block',
    marginRight: '8px',
    boxShadow: isOnline ? '0 0 8px #22c55e' : 'none',
  }),
  sectionTitle: {
    fontSize: '0.9rem',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    color: '#64748b',
    marginTop: '20px',
    marginBottom: '10px',
    fontWeight: '600',
  },
  toggleContainer: {
    display: 'flex',
    alignItems: 'center',
    cursor: 'pointer',
    marginBottom: '10px',
  },
  eventList: {
    flex: 1,
    overflowY: 'auto',
    marginTop: '10px',
    paddingRight: '5px',
  },
  eventCard: (type) => ({
    backgroundColor: type === 'possible_feeding' ? 'rgba(245, 158, 11, 0.1)' : '#0f172a',
    borderLeft: type === 'possible_feeding' ? '4px solid #f59e0b' : '4px solid #38bdf8',
    padding: '12px',
    borderRadius: '4px',
    marginBottom: '10px',
    fontSize: '0.9rem',
  }),
  mapWrapper: {
    flex: 1,
    position: 'relative',
  }
};

function App() {
  // --- STATE ---
  const [apiStatus, setApiStatus] = useState('Connecting...');
  const [isOnline, setIsOnline] = useState(false);
  const [liveEvents, setLiveEvents] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [loadingHotspots, setLoadingHotspots] = useState(true);
  
  // Map configuration
  const centerPos = [-13.00, 46.23]; // Mayotte/Mozambique Channel
  
  // --- EFFECT 1: API HEALTH CHECK ---
  useEffect(() => {
    const checkHealth = () => {
      fetch('http://127.0.0.1:8000/')
        .then(res => res.json())
        .then(data => {
          setApiStatus(data.status || 'Connected');
          setIsOnline(true);
        })
        .catch(() => {
          setApiStatus('Offline / Error');
          setIsOnline(false);
        });
    };
    checkHealth();
    const interval = setInterval(checkHealth, 10000); // Check every 10s
    return () => clearInterval(interval);
  }, []);

  // --- EFFECT 2: FETCH HOTSPOTS (REAL -> FALLBACK SIM) ---
  useEffect(() => {
    const fetchHotspots = async () => {
      setLoadingHotspots(true);
      try {
        console.log("Attempting to fetch REAL ML predictions...");
        const realRes = await fetch('http://127.0.0.1:8000/hotspots/real');
        
        if (realRes.ok) {
          const data = await realRes.json();
          if (data.status === 'success' && data.hotspots) {
            const points = data.hotspots.map(h => [h.latitude, h.longitude, h.prediction_value]);
            setHotspots(points);
            console.log(`Loaded ${points.length} Real ML points.`);
            setLoadingHotspots(false);
            return;
          }
        }

        console.log("Real model unavailable. Falling back to simulation...");
        const simRes = await fetch('http://127.0.0.1:8000/hotspots');
        if (simRes.ok) {
          const data = await simRes.json();
          if (data.status === 'success' && data.hotspots) {
            const points = data.hotspots.map(h => [h.latitude, h.longitude, h.prediction_value]);
            setHotspots(points);
            console.log(`Loaded ${points.length} Simulated points.`);
          }
        }
      } catch (err) {
        console.error("Failed to load hotspots:", err);
      } finally {
        setLoadingHotspots(false);
      }
    };

    fetchHotspots();
  }, []);

  // --- EFFECT 3: LIVE TAG POLLING ---
  useEffect(() => {
    const fetchEvents = () => {
      fetch('http://127.0.0.1:8000/events?limit=50')
        .then(res => res.ok ? res.json() : { events: [] })
        .then(data => {
          if (data.events) {
            // Keep only the latest event per shark for the markers, but show history in feed
            setLiveEvents(data.events);
          }
        })
        .catch(err => console.error("Event polling error:", err));
    };

    fetchEvents(); // Initial fetch
    const interval = setInterval(fetchEvents, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, []);

  // --- HELPER: Get Unique Sharks for Map Markers ---
  const uniqueSharks = Array.from(new Set(liveEvents.map(e => e.tag_id)))
    .map(id => {
      return liveEvents.find(e => e.tag_id === id);
    });

  return (
    <div style={styles.container}>
      
      {/* --- SIDEBAR --- */}
      <aside style={styles.sidebar}>
        <div style={styles.header}>
          <h1 style={styles.title}>SharkTrack AI</h1>
          <div style={styles.subtitle}>Real-time Foraging Habitat Monitor</div>
        </div>

        {/* Status Card */}
        <div style={styles.statusCard}>
          <div>
            <div style={styles.statusIndicator(isOnline)}></div>
            <span style={{fontWeight: 'bold', fontSize: '0.9rem'}}>
              {isOnline ? "System Operational" : "System Offline"}
            </span>
          </div>
          <div style={{fontSize: '0.8rem', color: '#94a3b8'}}>v1.0.0</div>
        </div>

        {/* Controls */}
        <div style={styles.sectionTitle}>Layers</div>
        <div style={styles.toggleContainer} onClick={() => setShowHeatmap(!showHeatmap)}>
          <input 
            type="checkbox" 
            checked={showHeatmap} 
            readOnly 
            style={{marginRight: '10px', cursor: 'pointer'}}
          />
          <span>Show ML Habitat Heatmap</span>
        </div>
        {loadingHotspots && <div style={{fontSize: '0.8rem', color: '#eab308'}}>Loading ML Model...</div>}

        {/* Live Feed */}
        <div style={styles.sectionTitle}>Live Telemetry ({liveEvents.length})</div>
        <div style={styles.eventList}>
          {liveEvents.length === 0 ? (
             <div style={{color: '#64748b', fontStyle: 'italic'}}>Waiting for tag data...</div>
          ) : (
            liveEvents.slice(0, 15).map((evt) => (
              <div key={evt.id} style={styles.eventCard(evt.event_trigger)}>
                <div style={{display:'flex', justifyContent:'space-between', marginBottom:'4px'}}>
                  <strong style={{color: '#e2e8f0'}}>{evt.tag_id}</strong>
                  <span style={{fontSize: '0.75rem', opacity: 0.7}}>
                    {new Date(evt.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <div style={{fontSize: '0.85rem'}}>
                  {evt.event_trigger === 'possible_feeding' ? '🍖 FEEDING EVENT' : '🏊 Transiting'}
                </div>
                <div style={{fontSize: '0.75rem', marginTop:'4px', color:'#94a3b8'}}>
                  Conf: {(evt.event_confidence * 100).toFixed(0)}% | Depth: {evt.depth_m}m
                </div>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* --- MAP VIEW --- */}
      <main style={styles.mapWrapper}>
        <MapContainer 
          center={centerPos} 
          zoom={11} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />

          {/* HEATMAP LAYER */}
          {showHeatmap && hotspots.length > 0 && (
            <HeatmapLayer
              points={hotspots}
              longitudeExtractor={m => m[1]}
              latitudeExtractor={m => m[0]}
              intensityExtractor={m => m[2]}
              radius={20}
              blur={15}
              max={1.0}
              minOpacity={0.4}
              gradient={{0.4: 'blue', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}}
            />
          )}

          {/* SHARK MARKERS */}
          {uniqueSharks.map(evt => (
             <Marker key={evt.tag_id} position={[evt.latitude, evt.longitude]}>
               <Popup>
                 <div style={{minWidth: '150px'}}>
                   <h3 style={{margin: '0 0 5px 0', color: '#0f172a'}}>{evt.tag_id}</h3>
                   <div style={{marginBottom: '5px'}}>
                     Status: <strong>{evt.event_trigger}</strong>
                   </div>
                   <div style={{fontSize: '0.9em'}}>
                    Temp: {evt.env_temperature_c}°C<br/>
                    Depth: {evt.depth_m}m<br/>
                    Battery: {evt.battery_level_pct}%
                   </div>
                   <div style={{fontSize: '0.8em', color: '#666', marginTop: '5px'}}>
                     Last seen: {new Date(evt.timestamp).toLocaleTimeString()}
                   </div>
                 </div>
               </Popup>
             </Marker>
          ))}
        </MapContainer>
      </main>
    </div>
  );
}

export default App;
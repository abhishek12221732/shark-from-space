## Frontend Documentation

### Overview
The frontend is a React-based single-page application (SPA) that provides a real-time dashboard for monitoring shark foraging habitats. It displays an interactive map with ML-generated habitat heatmaps and live IoT tag telemetry data from sharks. The application uses Leaflet for mapping and features a dark-themed dashboard interface.

### Architecture
- **Framework**: React 19 with modern hooks (useState, useEffect, useRef)
- **Build Tool**: Vite for fast development and optimized production builds
- **Mapping**: Leaflet with React-Leaflet wrapper
- **Visualization**: Heatmap layer for habitat predictions
- **Styling**: Inline CSS-in-JS with dark theme
- **State Management**: React hooks (no external state library)
- **API Communication**: Native fetch API with polling

### Project Structure
```
frontend/
├── public/                    # Static assets
├── src/
│   ├── App.jsx               # Main application component
│   ├── main.jsx              # React entry point
│   ├── App.css               # Component-specific styles (minimal)
│   ├── index.css             # Global styles
│   └── assets/               # Dynamic assets
├── index.html                # HTML template
├── vite.config.js            # Vite configuration
├── package.json              # Dependencies and scripts
└── eslint.config.js          # Linting configuration
```

### Dependencies (package.json)

#### Production Dependencies:
- `react@^19.1.1` - UI framework
- `react-dom@^19.1.1` - React DOM rendering
- `leaflet@^1.9.4` - Mapping library
- `react-leaflet@^5.0.0` - React wrapper for Leaflet
- `react-leaflet-heatmap-layer-v3@^3.0.3-beta-1` - Heatmap visualization

#### Development Dependencies:
- `@vitejs/plugin-react@^5.0.4` - Vite React plugin
- `vite@^7.1.7` - Build tool and dev server
- `@eslint/js@^9.36.0` - ESLint configuration
- `eslint@^9.36.0` - Linting
- `eslint-plugin-react-hooks@^5.2.0` - React hooks rules
- `eslint-plugin-react-refresh@^0.4.22` - Hot reload rules
- `@types/react@^19.1.16` - TypeScript types for React
- `@types/react-dom@^19.1.9` - TypeScript types for React DOM
- `globals@^16.4.0` - Global variables for ESLint

### Build Configuration (vite.config.js)
- Uses React plugin for JSX transformation
- Configures path aliases for React/React-DOM to avoid version conflicts
- Standard Vite setup with hot module replacement

### Linting (eslint.config.js)
- Modern ESLint flat config format
- Extends recommended JS rules
- Includes React hooks and refresh plugins
- Ignores `dist/` directory
- Custom rule: Allow unused vars starting with uppercase or underscore
- Browser globals enabled for client-side code

### Main Application Component (App.jsx)

#### State Management:
- `apiStatus`: Backend connection status ("Connecting...", "Connected", "Offline / Error")
- `isOnline`: Boolean indicating backend availability
- `liveEvents`: Array of recent tag telemetry events
- `hotspots`: Array of habitat prediction points [[lat, lng, intensity], ...]
- `showHeatmap`: Toggle for heatmap layer visibility
- `loadingHotspots`: Loading state for ML predictions

#### Effects:

1. **API Health Check** (10-second interval):
   - Fetches from `http://127.0.0.1:8000/`
   - Updates connection status and online indicator

2. **Hotspots Loading** (on mount):
   - Attempts to load real ML predictions first (`/hotspots/real`)
   - Falls back to simulated data (`/hotspots`) if real predictions unavailable
   - Transforms data to heatmap format: [latitude, longitude, prediction_value]

3. **Live Tag Polling** (2-second interval):
   - Fetches recent events from `/events?limit=50`
   - Updates live telemetry feed

#### UI Layout:
- **Sidebar** (350px fixed width):
  - Header with title "SharkTrack AI" and subtitle
  - Status card showing system operational status
  - Layer controls (heatmap toggle)
  - Live telemetry feed (last 15 events)

- **Map View** (flexible width):
  - Leaflet map centered on [-13.00, 46.23] (Mayotte/Mozambique Channel)
  - Dark CARTO basemap tiles
  - Heatmap layer with blue→lime→yellow→red gradient
  - Shark markers with popups showing telemetry data

#### Features:

##### Heatmap Visualization:
- Uses `react-leaflet-heatmap-layer-v3`
- Configurable radius (20px), blur (15px)
- Intensity-based coloring (0.4-1.0 range)
- Toggleable layer visibility

##### Live Telemetry:
- Real-time event feed with shark IDs, timestamps, event types
- Color-coded event cards (yellow for feeding events, blue for transiting)
- Confidence percentages and depth readings
- Battery level monitoring

##### Map Markers:
- One marker per unique shark (latest position)
- Popups with detailed telemetry:
  - Tag ID, status, temperature, depth, battery
  - Last seen timestamp

##### Responsive Design:
- Flexbox layout adapting to window size
- Sidebar with scrollable event list
- Dark theme optimized for monitoring environments

### Styling Approach
- **Inline Styles**: CSS-in-JS objects for component styling
- **Dark Theme**: Slate color palette (#0f172a, #1e293b, #334155)
- **Typography**: Segoe UI font stack with proper contrast ratios
- **Interactive Elements**: Hover states and visual feedback
- **Status Indicators**: Color-coded dots (green/red) with glow effects

### API Integration
- **Backend URL**: Hardcoded to `http://127.0.0.1:8000`
- **Endpoints Used**:
  - `GET /` - Health check
  - `GET /hotspots` - Simulated predictions
  - `GET /hotspots/real` - Real ML predictions
  - `GET /events?limit=50` - Recent telemetry
- **Error Handling**: Graceful fallbacks, console logging
- **Polling Strategy**: Regular intervals for real-time updates

### Performance Considerations
- **Efficient Rendering**: React 19 with optimized reconciliation
- **Polling Optimization**: Reasonable intervals (2-10 seconds)
- **Heatmap Caching**: Backend handles prediction caching
- **Bundle Size**: Minimal dependencies, tree-shaking enabled

### Development Setup
- **Start Dev Server**: `npm run dev` (Vite on port 5173)
- **Build Production**: `npm run build`
- **Preview Build**: `npm run preview`
- **Linting**: `npm run lint`
- **Hot Reload**: Automatic with Vite

### Browser Compatibility
- Modern browsers supporting ES2020+ features
- Leaflet requires CSS transforms and other modern APIs
- Tested with React 19's concurrent features

### Known Issues & Limitations
- **CORS**: Assumes backend allows frontend origin (localhost:5173)
- **Hardcoded URLs**: Backend URL not configurable
- **No Error Boundaries**: Network failures handled at effect level
- **No Offline Mode**: Requires active backend connection
- **Marker Icons**: Custom Leaflet icon fix for broken default markers

### Future Enhancements
- Environment-based API URL configuration
- WebSocket support for real-time updates
- Multiple map layers (satellite, terrain)
- Historical playback controls
- Alert system for feeding events
- Export functionality for telemetry data
- Mobile-responsive design improvements

## Project Progress Assessment

### Current Status: **Functional Prototype** (70-80% Complete)

#### Completed Features:
- ✅ Complete React SPA with modern architecture
- ✅ Interactive Leaflet map with dark theme
- ✅ Real-time ML habitat heatmap visualization
- ✅ Live IoT telemetry feed and shark tracking
- ✅ Responsive dashboard layout
- ✅ API integration with fallback mechanisms
- ✅ Production build configuration
- ✅ Linting and development tooling

#### Missing/Incomplete:
- ❌ Environment configuration (hardcoded URLs)
- ❌ Error boundaries and robust error handling
- ❌ Unit tests and integration tests
- ❌ Progressive Web App (PWA) features
- ❌ Mobile optimization
- ❌ Accessibility (a11y) compliance
- ❌ Performance monitoring
- ❌ Authentication and security
- ❌ Offline data caching
- ❌ Advanced map controls (zoom to extent, layer switching)

#### Development Stage:
- Working end-to-end with backend integration
- Suitable for demonstrations and initial deployments
- Requires hardening for production use
- Good separation of concerns and modern React patterns
- UI/UX focused on monitoring use case

#### Recommendations for Production:
1. Add environment variable configuration
2. Implement comprehensive error handling
3. Add testing suite (Jest, React Testing Library)
4. Performance optimization and bundle analysis
5. Accessibility audit and improvements
6. Security review (CSP, input validation)
7. Add loading states and skeleton screens
8. Implement offline capabilities with Service Workers
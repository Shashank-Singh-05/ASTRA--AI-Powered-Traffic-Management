import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Icon } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { EventResponse } from '../lib/types';
import { AlertTriangle, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

// Fix for default marker icons in Leaflet with Webpack/Vite
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

const defaultIcon = new Icon({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// A red icon for high priority events
const highPriorityIcon = new Icon({
  ...defaultIcon.options,
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  iconRetinaUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
});

interface MapWidgetProps {
  events: EventResponse[];
}

export function MapWidget({ events }: MapWidgetProps) {
  // Center of Bengaluru
  const center = { lat: 12.9716, lng: 77.5946 };

  return (
    <div className="h-[400px] w-full rounded-xl overflow-hidden border border-slate-200 shadow-sm relative z-0">
      <MapContainer 
        center={[center.lat, center.lng]} 
        zoom={12} 
        scrollWheelZoom={false}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
        
        {events.map((event) => (
          <Marker 
            key={event.id} 
            position={[event.latitude, event.longitude]}
            icon={event.priority === 'High' || event.requires_road_closure ? highPriorityIcon : defaultIcon}
          >
            <Popup className="astra-popup">
              <div className="p-1">
                <div className="flex items-center space-x-2 mb-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wide ${
                    event.priority === 'High' ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'
                  }`}>
                    {event.priority} Priority
                  </span>
                  <span className="text-xs text-slate-500">#{event.id}</span>
                </div>
                
                <h4 className="font-bold text-slate-900 text-base mb-1">
                  {event.event_cause.replace('_', ' ').toUpperCase()}
                </h4>
                
                <p className="text-sm text-slate-600 mb-3">{event.corridor || 'Unknown Location'}</p>
                
                {event.requires_road_closure && (
                  <div className="flex items-center text-amber-600 text-xs font-medium mb-3 bg-amber-50 p-1.5 rounded">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    Road Closure Required
                  </div>
                )}
                
                <div className="flex items-center justify-between border-t border-slate-100 pt-3 mt-2">
                  <div className="flex items-center text-xs text-slate-500">
                    <Clock className="w-3 h-3 mr-1" />
                    {new Date(event.start_datetime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                  </div>
                  
                  <Link 
                    to={`/recommendations/${event.id}`}
                    className="text-indigo-600 hover:text-indigo-800 text-xs font-medium"
                  >
                    View Details &rarr;
                  </Link>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

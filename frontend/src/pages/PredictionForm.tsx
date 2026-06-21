import { useState } from 'react';
import { Shield, MapPin, Clock, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../lib/api';
import type { PredictionRequest, PredictionResponse } from '../lib/types';

const corridorCoordinates: Record<string, { lat: string, lng: string }> = {
  'Bellary Road 1': { lat: '13.0334', lng: '77.5888' },
  'Hosur Road': { lat: '12.9234', lng: '77.6225' },
  'ORR East 1': { lat: '12.9345', lng: '77.6853' },
  'Mysore Road': { lat: '12.9511', lng: '77.5348' },
  'Non-corridor': { lat: '12.9716', lng: '77.5946' }
};

export function PredictionForm() {
  const navigate = useNavigate();
  const [isPredicting, setIsPredicting] = useState(false);

  // Form State
  const [eventType, setEventType] = useState('unplanned');
  const [eventCause, setEventCause] = useState('accident');
  const [priority, setPriority] = useState('High');
  const [requiresClosure, setRequiresClosure] = useState(false);
  const [corridor, setCorridor] = useState('Bellary Road 1');
  const [latitude, setLatitude] = useState(corridorCoordinates['Bellary Road 1'].lat);
  const [longitude, setLongitude] = useState(corridorCoordinates['Bellary Road 1'].lng);
  const [startDatetime, setStartDatetime] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsPredicting(true);

    const payload: PredictionRequest = {
      event_type: eventType,
      event_cause: eventCause,
      priority,
      latitude: parseFloat(latitude) || 0,
      longitude: parseFloat(longitude) || 0,
      corridor,
      requires_road_closure: requiresClosure,
      start_datetime: startDatetime || new Date().toISOString(),
      description
    };

    try {
      // 1. Create the event in the database so it shows up on the dashboard
      const eventResponse = await api.post('/events', payload);
      const eventId = eventResponse.data.id;

      // 2. Get prediction (risk score, corridor stress)
      const response = await api.post<PredictionResponse>('/predict', payload);
      
      const d = new Date(startDatetime || new Date().toISOString());
      const hour = d.getHours();
      const isPeak = (hour >= 8 && hour < 11) || (hour >= 17 && hour < 21);

      // 3. Get recommendations (strategies A/B/C) based on the risk score
      const recResponse = await api.post('/recommend', {
        event_id: eventId,
        risk_score: response.data.risk_score,
        event_cause: payload.event_cause,
        corridor: payload.corridor,
        requires_road_closure: payload.requires_road_closure,
        is_peak_hour: isPeak
      });
      
      // Merge the results so Recommendations.tsx has everything it needs
      const combined = { 
        ...response.data,
        prediction_id: eventId, // Override prediction_id with the real DB Event ID
        strategies: recResponse.data.strategies,
        overall_reasoning: recResponse.data.overall_reasoning
      };
      
      navigate('/recommendations', { state: { prediction: combined } });
    } catch (error) {
      console.error('API failed, falling back to mock prediction:', error);
      // Fallback mock logic
      const isHighSeverity = ['accident', 'vip_movement', 'protest'].includes(eventCause);
      const mockResult: PredictionResponse = {
        prediction_id: Math.floor(Math.random() * 10000),
        risk_score: isHighSeverity ? 85 : 45,
        risk_category: isHighSeverity ? 'Critical' : 'Medium',
        resolution_prediction: isHighSeverity ? 120 : 45,
        corridor_stress: isHighSeverity ? 90 : 50,
        strategies: [
          {
            name: "Aggressive Intervention",
            description: "Maximum resource deployment with full diversion",
            officers: isHighSeverity ? 8 : 4,
            barricades: isHighSeverity ? 12 : 5,
            diversion_needed: true,
            expected_risk_reduction: 35
          },
          {
            name: "Balanced Approach",
            description: "Standard protocol deployment",
            officers: isHighSeverity ? 5 : 2,
            barricades: isHighSeverity ? 8 : 2,
            diversion_needed: isHighSeverity,
            expected_risk_reduction: 20
          },
          {
            name: "Minimal Response",
            description: "Basic monitoring and traffic regulation",
            officers: 1,
            barricades: 0,
            diversion_needed: false,
            expected_risk_reduction: 5
          }
        ]
      };
      
      setTimeout(() => {
        navigate('/recommendations', { state: { prediction: mockResult } });
      }, 1000); // Simulate network delay
    } finally {
      if (!isPredicting) { // If api succeeded immediately, it navigated. 
        // We handle finally anyway
      }
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Event Prediction</h1>
        <p className="text-sm text-slate-500 mt-1">Input event details to generate risk scores and deployment strategies.</p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        <form onSubmit={handleSubmit}>
          <div className="p-6 space-y-8">
            {/* Section 1: Event Details */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                <Shield className="h-5 w-5 mr-2 text-indigo-500" />
                Event Details
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Event Type</label>
                  <select 
                    value={eventType}
                    onChange={(e) => setEventType(e.target.value)}
                    className="w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-slate-50 border p-2.5 text-sm"
                  >
                    <option value="unplanned">Unplanned Incident</option>
                    <option value="planned">Planned Event</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Cause / Category</label>
                  <select 
                    value={eventCause}
                    onChange={(e) => setEventCause(e.target.value)}
                    className="w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-slate-50 border p-2.5 text-sm"
                  >
                    <option value="accident">Accident</option>
                    <option value="vehicle_breakdown">Vehicle Breakdown</option>
                    <option value="water_logging">Water Logging</option>
                    <option value="tree_fall">Tree Fall</option>
                    <option value="vip_movement">VIP Movement</option>
                    <option value="protest">Protest / Rally</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Priority</label>
                  <select 
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-slate-50 border p-2.5 text-sm"
                  >
                    <option value="Low">Low</option>
                    <option value="High">High</option>
                  </select>
                </div>
                <div className="flex items-center mt-6">
                  <input 
                    id="closure" 
                    type="checkbox" 
                    checked={requiresClosure}
                    onChange={(e) => setRequiresClosure(e.target.checked)}
                    className="h-5 w-5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500" 
                  />
                  <label htmlFor="closure" className="ml-3 text-sm font-medium text-slate-700 flex items-center">
                    Requires Road Closure
                    <AlertCircle className="h-4 w-4 ml-1.5 text-amber-500" />
                  </label>
                </div>
              </div>
            </div>

            <hr className="border-slate-200" />

            {/* Section 2: Location */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                <MapPin className="h-5 w-5 mr-2 text-indigo-500" />
                Location
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1">Corridor</label>
                  <select 
                    value={corridor}
                    onChange={(e) => {
                      const val = e.target.value;
                      setCorridor(val);
                      if (corridorCoordinates[val]) {
                        setLatitude(corridorCoordinates[val].lat);
                        setLongitude(corridorCoordinates[val].lng);
                      }
                    }}
                    className="w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-slate-50 border p-2.5 text-sm"
                  >
                    <option value="Bellary Road 1">Bellary Road</option>
                    <option value="Hosur Road">Hosur Road</option>
                    <option value="ORR East 1">Outer Ring Road (East)</option>
                    <option value="Mysore Road">Mysore Road</option>
                    <option value="Non-corridor">Other / Non-corridor</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Latitude</label>
                  <input 
                    type="number" 
                    step="0.000001" 
                    value={latitude} 
                    onChange={(e) => setLatitude(e.target.value)}
                    className="w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-slate-50 border p-2.5 text-sm" 
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Longitude</label>
                  <input 
                    type="number" 
                    step="0.000001" 
                    value={longitude} 
                    onChange={(e) => setLongitude(e.target.value)}
                    className="w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-slate-50 border p-2.5 text-sm" 
                  />
                </div>
              </div>
            </div>

            <hr className="border-slate-200" />

            {/* Section 3: Time */}
            <div>
              <h3 className="text-lg font-semibold text-slate-900 mb-4 flex items-center">
                <Clock className="h-5 w-5 mr-2 text-indigo-500" />
                Time & Duration
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Start Date & Time</label>
                  <input 
                    type="datetime-local" 
                    value={startDatetime}
                    onChange={(e) => setStartDatetime(e.target.value)}
                    className="w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-slate-50 border p-2.5 text-sm" 
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Description (Optional)</label>
                  <input 
                    type="text" 
                    placeholder="Additional details..." 
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full rounded-lg border-slate-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 bg-slate-50 border p-2.5 text-sm" 
                  />
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-50 px-6 py-4 flex items-center justify-end border-t border-slate-200">
            <button 
              type="button" 
              onClick={() => navigate(-1)}
              className="text-sm font-medium text-slate-700 hover:text-slate-900 px-4 py-2 mr-2"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              disabled={isPredicting}
              className={`bg-indigo-600 text-white px-6 py-2.5 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm shadow-indigo-200 flex items-center ${isPredicting ? 'opacity-75 cursor-not-allowed' : ''}`}
            >
              {isPredicting ? (
                <>
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Running Models...
                </>
              ) : (
                'Generate Intelligence'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  AlertTriangle, 
  Activity, 
  Users, 
  Clock,
  TrendingUp,
  MapPin
} from 'lucide-react';
import api from '../lib/api';
import type { DashboardKPIs, EventResponse } from '../lib/types';
import { MapWidget } from '../components/MapWidget';

export function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [activeEvents, setActiveEvents] = useState<EventResponse[]>([]);
  
  const [stats, setStats] = useState<DashboardKPIs>({
    active_events: 0,
    high_risk_events: 0,
    officers_deployed: 0,
    avg_risk_score: 0,
    events_today: 0,
    events_this_week: 0,
    avg_resolution_minutes: 0,
    top_corridors: [],
    risk_distribution: {}
  });

  useEffect(() => {
    const fetchKPIs = async () => {
      try {
        // Fetch KPIs
        const response = await api.get<DashboardKPIs>('/dashboard/kpis');
        setStats(response.data);
        
        // Fetch Active Events for the map
        const eventsResponse = await api.get<{events: EventResponse[]}>('/events?status=active');
        setActiveEvents(eventsResponse.data.events);
      } catch (error) {
        console.error('Failed to fetch KPIs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchKPIs();
  }, []);

  const handleDownloadReport = () => {
    alert('Report download started');
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">System Overview</h1>
          <p className="text-sm text-slate-500 mt-1">Real-time traffic intelligence and resource allocation.</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={handleDownloadReport}
            className="bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors shadow-sm"
          >
            Download Report
          </button>
          <button 
            onClick={() => navigate('/predict')}
            className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors shadow-sm shadow-indigo-200"
          >
            + New Event
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-500">Active Events</h3>
            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <Activity className="h-5 w-5" />
            </div>
          </div>
          <p className="text-3xl font-bold text-slate-900 mt-4">{stats.active_events}</p>
          <div className="flex items-center mt-2 text-sm text-slate-500">
            <span>Events being tracked</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-500">High Risk Events</h3>
            <div className="p-2 bg-red-50 text-red-600 rounded-lg">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </div>
          <p className="text-3xl font-bold text-slate-900 mt-4">{stats.high_risk_events}</p>
          <div className="flex items-center mt-2 text-sm text-red-600 font-medium">
            <TrendingUp className="h-4 w-4 mr-1" />
            <span>Requires attention</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-500">Officers Deployed</h3>
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <Users className="h-5 w-5" />
            </div>
          </div>
          <p className="text-3xl font-bold text-slate-900 mt-4">{stats.officers_deployed}</p>
          <div className="flex items-center mt-2 text-sm text-slate-500">
            <span>Based on active events</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium text-slate-500">Avg Resolution Time</h3>
            <div className="p-2 bg-amber-50 text-amber-600 rounded-lg">
              <Clock className="h-5 w-5" />
            </div>
          </div>
          <p className="text-3xl font-bold text-slate-900 mt-4">
            {stats.avg_resolution_minutes.toFixed(1)} <span className="text-lg text-slate-500 font-normal">min</span>
          </p>
          <div className="flex items-center mt-2 text-sm text-slate-500">
            <span>Average per event</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Map replacing the placeholder chart */}
        <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-slate-900">Live Traffic Map</h2>
            <div className="flex items-center space-x-2">
              <span className="flex h-2.5 w-2.5 relative">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-indigo-500"></span>
              </span>
              <span className="text-sm font-medium text-slate-600">Live</span>
            </div>
          </div>
          <div className="flex-1">
            <MapWidget events={activeEvents} />
          </div>
        </div>

        {/* Top Corridors */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col">
          <h2 className="text-lg font-semibold text-slate-900 mb-6">Stressed Corridors</h2>
          <div className="flex-1 space-y-6">
            {stats.top_corridors.map((corridor, idx) => (
              <div key={idx} className="flex items-center justify-between group">
                <div className="flex items-start">
                  <div className={`p-2 rounded-lg mr-3 ${
                    corridor.stress_score > 80 ? 'bg-red-50 text-red-600' :
                    corridor.stress_score > 60 ? 'bg-orange-50 text-orange-600' :
                    'bg-amber-50 text-amber-600'
                  }`}>
                    <MapPin className="h-5 w-5" />
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-slate-900">{corridor.corridor}</h4>
                    <p className="text-xs text-slate-500 mt-0.5">{corridor.active_events} active events</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-lg font-bold ${
                    corridor.stress_score > 80 ? 'text-red-600' :
                    corridor.stress_score > 60 ? 'text-orange-600' :
                    'text-amber-600'
                  }`}>
                    {corridor.stress_score}
                  </div>
                  <div className="text-xs text-slate-500">stress</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

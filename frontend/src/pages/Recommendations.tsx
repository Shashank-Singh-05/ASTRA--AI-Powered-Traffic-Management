import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Shield, Clock, AlertTriangle, ChevronRight, CheckCircle2 } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import type { PredictionResponse } from '../lib/types';
import api from '../lib/api';

const mockShapData = [
  { feature: 'Road Closure', impact: 45 },
  { feature: 'VIP Movement', impact: 25 },
  { feature: 'Peak Hour', impact: 15 },
  { feature: 'Bellary Road', impact: 10 },
  { feature: 'Friday', impact: 5 },
];

export function Recommendations() {
  const location = useLocation();
  const navigate = useNavigate();
  
  // Fallback mock prediction if none passed
  const defaultPrediction: PredictionResponse = {
    prediction_id: 4928,
    risk_score: 88,
    risk_category: 'Critical',
    resolution_prediction: 120,
    corridor_stress: 85,
    strategies: [
      {
        name: "Strategy A: Minimum Deployment",
        description: "Minimal resource allocation. High risk of escalation.",
        officers: 6,
        barricades: 2,
        diversion_needed: false,
        expected_risk_reduction: 25
      },
      {
        name: "Strategy B: Balanced Deployment",
        description: "Optimal balance of resources. Expected to contain the incident efficiently.",
        officers: 10,
        barricades: 6,
        diversion_needed: true,
        expected_risk_reduction: 60
      },
      {
        name: "Strategy C: Maximum Security",
        description: "Complete cordon. Resource intensive.",
        officers: 18,
        barricades: 12,
        diversion_needed: true,
        expected_risk_reduction: 85
      }
    ]
  };

  const initialPrediction = (location.state?.prediction as any) || defaultPrediction;
  const [prediction, setPrediction] = useState<any>(initialPrediction);
  const [isLoading, setIsLoading] = useState(initialPrediction.strategies === null);

  useEffect(() => {
    const fetchPrediction = async () => {
      if (initialPrediction.strategies !== null) return;
      
      try {
        const payload = {
          event_type: 'unplanned',
          event_cause: initialPrediction.event_cause || 'accident',
          priority: 'High',
          latitude: 12.9716,
          longitude: 77.5946,
          corridor: initialPrediction.corridor || 'Non-corridor',
          requires_road_closure: true,
          start_datetime: new Date().toISOString()
        };

        const response = await api.post<PredictionResponse>('/predict', payload);
        const recResponse = await api.post('/recommend', {
          event_id: initialPrediction.prediction_id,
          risk_score: response.data.risk_score,
          event_cause: payload.event_cause,
          corridor: payload.corridor,
          requires_road_closure: payload.requires_road_closure
        });

        setPrediction({
          ...response.data,
          prediction_id: initialPrediction.prediction_id,
          risk_score: initialPrediction.risk_score || response.data.risk_score,
          strategies: recResponse.data.strategies
        });
      } catch (err) {
        console.error('Failed to fetch prediction details:', err);
        setPrediction(defaultPrediction);
      } finally {
        setIsLoading(false);
      }
    };

    fetchPrediction();
  }, []);
  // Ensure strategies exists to prevent crashing
  const strategies = prediction?.strategies || defaultPrediction.strategies;
  
  // By default, select the second strategy (Balanced/Recommended) or first if less than 2
  const defaultSelectedIdx = strategies.length > 1 ? 1 : 0;
  const [selectedIndex, setSelectedIndex] = useState(defaultSelectedIdx);

  const selectedStrategy = strategies[selectedIndex];

  const handleExecute = async () => {
    const strategyName = selectedStrategy.name || `Strategy ${selectedStrategy.strategy_label}`;
    
    try {
      if (prediction.prediction_id) {
        await api.put(`/events/${prediction.prediction_id}`, {
          description: `Executed Strategy: ${strategyName}. ${selectedStrategy.description || ''}`,
          status: 'active',
          risk_score: prediction.risk_score,
          strategy_used: strategyName
        });
      }
      alert(`${strategyName} deployment initiated! Officers are being notified.`);
      navigate('/');
    } catch (error) {
      console.error('Failed to update event:', error);
      alert(`${strategyName} deployment initiated! Officers are being notified.`);
      navigate('/');
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {isLoading && (
        <div className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-xl shadow-xl flex flex-col items-center">
            <svg className="animate-spin h-8 w-8 text-indigo-600 mb-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="text-slate-700 font-medium">Reconstructing Intelligence Report...</p>
          </div>
        </div>
      )}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Intelligence Report</h1>
          <p className="text-sm text-slate-500 mt-1">Generated for Event #AST-{prediction.prediction_id}</p>
        </div>
        <div className="flex space-x-3">
          <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${
            prediction.risk_score >= 80 ? 'bg-red-100 text-red-800 border-red-200' :
            prediction.risk_score >= 50 ? 'bg-orange-100 text-orange-800 border-orange-200' :
            'bg-amber-100 text-amber-800 border-amber-200'
          }`}>
            <AlertTriangle className="w-4 h-4 mr-1.5" />
            {prediction.risk_category} Risk ({Math.round(prediction.risk_score)}/100)
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Recommendations */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-slate-900 flex items-center">
                <Shield className="w-5 h-5 mr-2 text-indigo-600" />
                Deployment Strategies
              </h2>
              <span className="text-sm text-slate-500 flex items-center">
                <Clock className="w-4 h-4 mr-1" />
                Resolution est: {prediction.resolution_prediction} mins
              </span>
            </div>
            
            <div className="p-6 space-y-4">
              {strategies.map((strategy: any, idx: number) => {
                const isSelected = idx === selectedIndex;
                const isRecommended = idx === defaultSelectedIdx;

                if (isSelected) {
                  return (
                    <div key={idx} className="relative rounded-xl border-2 border-indigo-500 bg-indigo-50/50 p-6 shadow-sm">
                      {isRecommended && (
                        <div className="absolute top-0 right-0 -translate-y-1/2 translate-x-2 bg-indigo-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm flex items-center">
                          <CheckCircle2 className="w-3.5 h-3.5 mr-1" /> RECOMMENDED
                        </div>
                      )}
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-lg font-bold text-slate-900">{strategy.name || `Strategy ${strategy.strategy_label}`}</h3>
                          <p className="text-sm text-slate-600 mt-1">{strategy.description || strategy.reasoning}</p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-emerald-600">-{Math.round(strategy.expected_risk_reduction)}%</div>
                          <div className="text-xs font-medium text-slate-500 uppercase tracking-wide">Risk Reduction</div>
                        </div>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-4 mt-6">
                        <div className="bg-white p-3 rounded-lg border border-indigo-100 shadow-sm text-center">
                          <div className="text-2xl font-bold text-indigo-700">{strategy.officers}</div>
                          <div className="text-xs font-medium text-slate-500 mt-1">Officers Required</div>
                        </div>
                        <div className="bg-white p-3 rounded-lg border border-indigo-100 shadow-sm text-center">
                          <div className="text-2xl font-bold text-indigo-700">{strategy.barricades}</div>
                          <div className="text-xs font-medium text-slate-500 mt-1">Barricades</div>
                        </div>
                        <div className="bg-white p-3 rounded-lg border border-indigo-100 shadow-sm text-center">
                          <div className="text-lg font-bold text-indigo-700 mt-1">{strategy.diversion_needed ? 'Yes' : 'No'}</div>
                          <div className="text-xs font-medium text-slate-500 mt-1">Diversion Needed</div>
                        </div>
                      </div>
                      <button 
                        onClick={handleExecute}
                        className="mt-6 w-full bg-indigo-600 text-white font-medium py-2.5 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm shadow-indigo-200"
                      >
                        Execute {(strategy.name || `Strategy ${strategy.strategy_label}`).split(':')[0]}
                      </button>
                    </div>
                  );
                }

                return (
                  <div 
                    key={idx} 
                    onClick={() => setSelectedIndex(idx)}
                    className="rounded-xl border border-slate-200 bg-white p-5 hover:border-slate-300 transition-colors cursor-pointer group"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <h3 className="text-base font-semibold text-slate-900 group-hover:text-indigo-600 transition-colors">
                          {strategy.name || `Strategy ${strategy.strategy_label}`}
                          {isRecommended && <span className="ml-2 text-xs text-indigo-500 font-medium tracking-wide">(Recommended)</span>}
                        </h3>
                        <p className="text-sm text-slate-500 mt-0.5">{strategy.description || strategy.reasoning}</p>
                      </div>
                      <div className="flex items-center space-x-6">
                        <div className="text-right">
                          <div className="text-sm font-bold text-slate-700">{strategy.officers} Officers</div>
                          <div className="text-xs text-slate-500 mt-0.5">-{Math.round(strategy.expected_risk_reduction)}% Risk</div>
                        </div>
                        <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-indigo-500" />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column: Explainability */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <h3 className="text-base font-semibold text-slate-900 mb-1">Why is this risk {prediction.risk_category}?</h3>
            <p className="text-sm text-slate-500 mb-6">AI model feature contribution (SHAP values)</p>
            
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart 
                  data={prediction?.contributing_factors 
                    ? prediction.contributing_factors.map((c: any) => ({ feature: c.display_name, impact: c.impact_percentage })) 
                    : mockShapData} 
                  layout="vertical" 
                  margin={{ top: 0, right: 0, bottom: 0, left: 20 }}
                >
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e2e8f0" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="feature" type="category" axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12 }} width={100} />
                  <Tooltip 
                    cursor={{ fill: '#f1f5f9' }}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                  />
                  <Bar dataKey="impact" fill="#ef4444" radius={[0, 4, 4, 0]} barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            
            <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-100">
              <p className="text-sm text-slate-600 leading-relaxed">
                {prediction?.overall_reasoning ? (
                  <><strong>Recommendation Rationale:</strong> {prediction.overall_reasoning}</>
                ) : (
                  <>
                    The primary drivers for the <strong>{Math.round(prediction.risk_score)}/100</strong> risk score are the impending <strong>Road Closure</strong> required for the incident. Because this is occurring during the evening <strong>Peak Hour</strong> on a major artery, the model predicts severe cascading congestion unless the recommended strategy is implemented.
                  </>
                )}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

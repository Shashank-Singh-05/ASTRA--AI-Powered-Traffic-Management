import { useState, useMemo, useEffect } from 'react';
import { Search, Filter, Download } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../lib/api';

const ITEMS_PER_PAGE = 5;

export function History() {
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  const [historyData, setHistoryData] = useState<any[]>([]);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await api.post('/history/search', {
          page: 1,
          per_page: 100
        });
        setHistoryData(response.data.results.map((e: any) => ({
          id: `AST-${e.id}`,
          cause: e.event_cause,
          corridor: e.corridor || 'Unknown',
          time: new Date(e.created_at || e.start_datetime).toLocaleString(),
          risk: e.risk_score ? Math.round(e.risk_score) : 50,
          strategy: e.strategy_used || 'Pending',
          resolution: e.closed_at ? 'Solved' : 'Pending',
          status: e.status
        })));
      } catch (err) {
        console.error(err);
      }
    };
    fetchHistory();
  }, []);

  const handleResolveEvent = async (id: string) => {
    try {
      await api.put(`/events/${id}`, { status: 'resolved' });
      // Refresh data
      const response = await api.post('/history/search', {
        page: 1,
        per_page: 100
      });
      setHistoryData(response.data.results.map((e: any) => ({
        id: `AST-${e.id}`,
        cause: e.event_cause,
        corridor: e.corridor || 'Unknown',
        time: new Date(e.created_at || e.start_datetime).toLocaleString(),
        risk: e.risk_score ? Math.round(e.risk_score) : 50,
        strategy: e.strategy_used || 'Pending',
        resolution: e.closed_at ? 'Solved' : 'Pending',
        status: e.status
      })));
    } catch (err) {
      console.error("Failed to resolve event", err);
      alert("Failed to resolve event");
    }
  };

  // Filter Data
  const filteredData = useMemo(() => {
    return historyData.filter(event => {
      const q = searchQuery.toLowerCase();
      return (
        event.id.toLowerCase().includes(q) ||
        event.cause.toLowerCase().includes(q) ||
        event.corridor.toLowerCase().includes(q)
      );
    });
  }, [searchQuery, historyData]);

  // Paginate Data
  const totalPages = Math.ceil(filteredData.length / ITEMS_PER_PAGE);
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE;
    return filteredData.slice(start, start + ITEMS_PER_PAGE);
  }, [filteredData, currentPage]);

  const handleExportCSV = () => {
    const headers = ['Event ID', 'Cause', 'Corridor', 'Date & Time', 'Risk Score', 'Strategy Used', 'Resolution'];
    const rows = filteredData.map(e => [e.id, e.cause, e.corridor, e.time, e.risk.toString(), e.strategy, e.resolution]);
    
    let csvContent = "data:text/csv;charset=utf-8," 
      + headers.join(",") + "\n"
      + rows.map(e => e.join(",")).join("\n");
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "astra_event_history.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Event History</h1>
          <p className="text-sm text-slate-500 mt-1">Search and analyze past traffic events and model performance.</p>
        </div>
        <div className="flex space-x-3">
          <button 
            onClick={handleExportCSV}
            className="bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors shadow-sm flex items-center"
          >
            <Download className="w-4 h-4 mr-2" />
            Export CSV
          </button>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Toolbar */}
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="relative max-w-md w-full">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-slate-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1); // Reset to page 1 on search
              }}
              className="block w-full pl-10 pr-3 py-2 border border-slate-300 rounded-lg leading-5 bg-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="Search by ID, Cause, or Corridor..."
            />
          </div>
          <div className="flex items-center space-x-3">
            <button 
              onClick={() => setShowFilters(!showFilters)}
              className={`border px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm flex items-center ${
                showFilters ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-white border-slate-300 text-slate-700 hover:bg-slate-50'
              }`}
            >
              <Filter className="w-4 h-4 mr-2" />
              Filters
            </button>
          </div>
        </div>

        {/* Filters Panel */}
        {showFilters && (
          <div className="p-4 border-b border-slate-200 bg-white grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase mb-1">Status</label>
              <select className="w-full rounded-md border-slate-300 text-sm py-1.5 px-3">
                <option>All Statuses</option>
                <option>Resolved</option>
                <option>Active</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase mb-1">Risk Level</label>
              <select className="w-full rounded-md border-slate-300 text-sm py-1.5 px-3">
                <option>All Risks</option>
                <option>Critical (&gt;80)</option>
                <option>High (&gt;60)</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 uppercase mb-1">Date Range</label>
              <select className="w-full rounded-md border-slate-300 text-sm py-1.5 px-3">
                <option>Last 7 Days</option>
                <option>Last 30 Days</option>
                <option>All Time</option>
              </select>
            </div>
          </div>
        )}

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Event ID</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Cause & Location</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Date & Time</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Risk Score</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Strategy Used</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Actual Resolution</th>
                <th scope="col" className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-slate-200">
              {paginatedData.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-sm text-slate-500">
                    No events found matching your search.
                  </td>
                </tr>
              ) : paginatedData.map((event) => (
                <tr key={event.id} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-indigo-600">
                    {event.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-slate-900">{event.cause}</div>
                    <div className="text-sm text-slate-500">{event.corridor}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    {event.time}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      event.risk > 80 ? 'bg-red-100 text-red-800' :
                      event.risk > 60 ? 'bg-orange-100 text-orange-800' :
                      'bg-amber-100 text-amber-800'
                    }`}>
                      {event.risk} / 100
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    Strategy {event.strategy}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                    {event.resolution}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {event.resolution === 'Pending' && (
                      <button 
                        onClick={() => handleResolveEvent(event.id.split('-')[1])} 
                        className="text-emerald-600 hover:text-emerald-900 mr-4"
                      >
                        Resolve
                      </button>
                    )}
                    <Link to={`/recommendations`} state={{ 
                      prediction: { 
                        prediction_id: event.id.split('-')[1], 
                        risk_score: event.risk,
                        strategies: null,
                        event_cause: event.cause,
                        corridor: event.corridor
                      } 
                    }} className="text-indigo-600 hover:text-indigo-900">
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Pagination */}
        <div className="bg-white px-4 py-3 border-t border-slate-200 flex items-center justify-between sm:px-6">
          <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-slate-700">
                Showing <span className="font-medium">{(currentPage - 1) * ITEMS_PER_PAGE + 1}</span> to <span className="font-medium">{Math.min(currentPage * ITEMS_PER_PAGE, filteredData.length)}</span> of <span className="font-medium">{filteredData.length}</span> results
              </p>
            </div>
            <div>
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <button 
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-slate-300 bg-white text-sm font-medium text-slate-500 hover:bg-slate-50 disabled:opacity-50"
                >
                  Previous
                </button>
                {Array.from({ length: totalPages }).map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(i + 1)}
                    className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                      currentPage === i + 1 ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600' : 'bg-white border-slate-300 text-slate-500 hover:bg-slate-50'
                    }`}
                  >
                    {i + 1}
                  </button>
                ))}
                <button 
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages || totalPages === 0}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-slate-300 bg-white text-sm font-medium text-slate-500 hover:bg-slate-50 disabled:opacity-50"
                >
                  Next
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

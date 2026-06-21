import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Dashboard } from './pages/Dashboard';
import { PredictionForm } from './pages/PredictionForm';
import { Recommendations } from './pages/Recommendations';
import { History } from './pages/History';
import { AICopilot } from './pages/AICopilot';
import { Login } from './pages/Login';
import { ProtectedRoute } from './components/ProtectedRoute';
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <Router>
      <Routes>
        {/* Login page - standalone, no shell */}
        <Route path="/login" element={<Login />} />

        {/* App shell - only for authenticated routes */}
        <Route
          path="/*"
          element={
            <div className="flex h-screen bg-background text-foreground overflow-hidden">
              <Sidebar />
              <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
                <Header />
                <main className="flex-1 overflow-auto p-6">
                  <Routes>
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
                    <Route path="/predict" element={<ProtectedRoute><PredictionForm /></ProtectedRoute>} />
                    <Route path="/recommendations/:id?" element={<ProtectedRoute><ErrorBoundary><Recommendations /></ErrorBoundary></ProtectedRoute>} />
                    <Route path="/history" element={<ProtectedRoute><History /></ProtectedRoute>} />
                    <Route path="/copilot" element={<ProtectedRoute><AICopilot /></ProtectedRoute>} />
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </main>
              </div>
            </div>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;

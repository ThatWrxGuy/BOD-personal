import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Signals from './pages/Signals';
import Governance from './pages/Governance';
import Goals from './pages/Goals';
import Intelligence from './pages/Intelligence';
import Simulations from './pages/Simulations';
import Decisions from './pages/Decisions';
import SystemHealth from './pages/SystemHealth';
import Execution from './pages/Execution';
import Debates from './pages/Debates';
import Learning from './pages/Learning';
import DataPlatform from './pages/DataPlatform';
import Agents from './pages/Agents';
import Orchestration from './pages/Orchestration';
import { useAppStore } from './services/store';

function App() {
  const { refreshAll, fetchHealth } = useAppStore();

  useEffect(() => {
    // Initial data load
    refreshAll();
    
    // Poll for health updates every 30 seconds
    const healthInterval = setInterval(fetchHealth, 30000);
    
    return () => clearInterval(healthInterval);
  }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="signals" element={<Signals />} />
          <Route path="governance" element={<Governance />} />
          <Route path="goals" element={<Goals />} />
          <Route path="intelligence" element={<Intelligence />} />
          <Route path="simulations" element={<Simulations />} />
          <Route path="decisions" element={<Decisions />} />
          <Route path="debates" element={<Debates />} />
          <Route path="execution" element={<Execution />} />
          <Route path="learning" element={<Learning />} />
          <Route path="data-platform" element={<DataPlatform />} />
          <Route path="agents" element={<Agents />} />
          <Route path="orchestration" element={<Orchestration />} />
          <Route path="system" element={<SystemHealth />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

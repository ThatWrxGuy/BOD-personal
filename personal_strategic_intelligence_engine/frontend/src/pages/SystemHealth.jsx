import { useEffect } from 'react';
import { Activity, Server, Database, Clock, CheckCircle, AlertCircle, Zap } from 'lucide-react';
import { useAppStore } from '../services/store';
import { formatDistanceToNow } from 'date-fns';

export default function SystemHealth() {
  const { systemHealth, fetchHealth, healthLoading } = useAppStore();

  useEffect(() => {
    fetchHealth();
  }, []);

  // Mock health data if none available
  const health = systemHealth || {
    status: 'healthy',
    database: 'connected',
    workers: [
      { name: 'Signal Collector', status: 'running', last_run: new Date().toISOString() },
      { name: 'Governance Scheduler', status: 'running', last_run: new Date().toISOString() },
      { name: 'Intelligence Worker', status: 'running', last_run: new Date().toISOString() },
    ],
    uptime: '24 hours',
    last_backup: new Date().toISOString(),
  };

  const components = [
    { 
      name: 'API Server', 
      status: 'healthy', 
      icon: Server,
      details: 'Running on port 8000' 
    },
    { 
      name: 'Database', 
      status: health.database === 'connected' ? 'healthy' : 'warning', 
      icon: Database,
      details: health.database === 'connected' ? 'PostgreSQL connected' : 'Connection issues' 
    },
    { 
      name: 'Signal Collector', 
      status: health.workers?.[0]?.status === 'running' ? 'healthy' : 'warning',
      icon: Zap,
      details: 'Collecting signals every 15 minutes' 
    },
    { 
      name: 'Governance Scheduler', 
      status: health.workers?.[1]?.status === 'running' ? 'healthy' : 'warning',
      icon: Clock,
      details: 'Managing scheduled meetings' 
    },
    { 
      name: 'Intelligence Worker', 
      status: health.workers?.[2]?.status === 'running' ? 'healthy' : 'warning',
      icon: Activity,
      details: 'Running periodic analyses' 
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">System Health</h1>
          <p className="text-gray-400">Monitor technical health and worker status</p>
        </div>
        <button 
          onClick={fetchHealth}
          disabled={healthLoading}
          className="btn btn-secondary flex items-center gap-2"
        >
          <Activity className={`w-4 h-4 ${healthLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="stat-card">
          <div className="flex items-center justify-between">
            <span className="text-gray-400">Overall Status</span>
            <span className="flex items-center gap-2">
              {health.status === 'healthy' ? (
                <CheckCircle className="w-5 h-5 text-success" />
              ) : (
                <AlertCircle className="w-5 h-5 text-warning" />
              )}
            </span>
          </div>
          <div className={`text-2xl font-bold mt-2 ${
            health.status === 'healthy' ? 'text-success' : 'text-warning'
          }`}>
            {health.status === 'healthy' ? 'Healthy' : 'Degraded'}
          </div>
        </div>
        
        <div className="stat-card">
          <span className="text-gray-400">Uptime</span>
          <div className="text-2xl font-bold text-white mt-2">{health.uptime || '24 hours'}</div>
        </div>
        
        <div className="stat-card">
          <span className="text-gray-400">Last Backup</span>
          <div className="text-2xl font-bold text-white mt-2">
            {health.last_backup ? formatDistanceToNow(new Date(health.last_backup), { addSuffix: true }) : 'N/A'}
          </div>
        </div>
      </div>

      {/* Component Status */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Component Status</h2>
        <div className="space-y-3">
          {components.map(comp => (
            <div key={comp.name} className="flex items-center justify-between p-4 bg-dark-bg rounded-lg">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${
                  comp.status === 'healthy' ? 'bg-success/10' : 'bg-warning/10'
                }`}>
                  <comp.icon className={`w-5 h-5 ${
                    comp.status === 'healthy' ? 'text-success' : 'text-warning'
                  }`} />
                </div>
                <div>
                  <h3 className="font-medium text-white">{comp.name}</h3>
                  <p className="text-xs text-gray-500">{comp.details}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <span className={`w-2 h-2 rounded-full ${
                  comp.status === 'healthy' ? 'bg-success' : 'bg-warning'
                }`} />
                <span className={`text-sm ${
                  comp.status === 'healthy' ? 'text-success' : 'text-warning'
                }`}>
                  {comp.status === 'healthy' ? 'Running' : 'Warning'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Worker Status */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Worker Processes</h2>
        <div className="space-y-3">
          {health.workers?.map((worker, idx) => (
            <div key={idx} className="flex items-center justify-between p-4 bg-dark-bg rounded-lg">
              <div className="flex items-center gap-3">
                <Zap className="w-5 h-5 text-primary-400" />
                <div>
                  <h3 className="font-medium text-white">{worker.name}</h3>
                  <p className="text-xs text-gray-500">
                    Last run: {formatDistanceToNow(new Date(worker.last_run), { addSuffix: true })}
                  </p>
                </div>
              </div>
              <span className={`badge ${
                worker.status === 'running' ? 'badge-success' : 'badge-warning'
              }`}>
                {worker.status}
              </span>
            </div>
          )) || (
            <div className="text-center py-8 text-gray-500">
              No worker information available
            </div>
          )}
        </div>
      </div>

      {/* Database Info */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Database</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 bg-dark-bg rounded-lg">
            <p className="text-xs text-gray-500">Status</p>
            <p className="text-success font-medium flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              Connected
            </p>
          </div>
          <div className="p-4 bg-dark-bg rounded-lg">
            <p className="text-xs text-gray-500">Type</p>
            <p className="text-white font-medium">PostgreSQL</p>
          </div>
          <div className="p-4 bg-dark-bg rounded-lg">
            <p className="text-xs text-gray-500">Tables</p>
            <p className="text-white font-medium">20+</p>
          </div>
          <div className="p-4 bg-dark-bg rounded-lg">
            <p className="text-xs text-gray-500">Records</p>
            <p className="text-white font-medium">Active</p>
          </div>
        </div>
      </div>
    </div>
  );
}

import { useState } from 'react';
import { 
  Workflow, 
  Play, 
  Pause, 
  RotateCcw, 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Activity,
  Zap,
  Settings,
  ChevronDown,
  ChevronRight,
  RefreshCw
} from 'lucide-react';

export default function Orchestration() {
  const [selectedCycle, setSelectedCycle] = useState(null);

  // Strategy loop cycles
  const cycles = [
    {
      id: 'cycle-001',
      status: 'completed',
      trigger: 'SCHEDULED',
      startedAt: '2026-03-14T00:00:00Z',
      completedAt: '2026-03-14T00:01:32Z',
      runtimeMs: 92000,
      observedDomains: ['finance', 'health', 'operations'],
      changesDetected: 3,
      adjustmentsGenerated: 2,
      actionsExecuted: 2,
    },
    {
      id: 'cycle-002',
      status: 'completed',
      trigger: 'MANUAL',
      startedAt: '2026-03-13T18:00:00Z',
      completedAt: '2026-03-13T18:01:15Z',
      runtimeMs: 75000,
      observedDomains: ['finance', 'operations'],
      changesDetected: 1,
      adjustmentsGenerated: 1,
      actionsExecuted: 1,
    },
    {
      id: 'cycle-003',
      status: 'failed',
      trigger: 'SCHEDULED',
      startedAt: '2026-03-13T12:00:00Z',
      completedAt: '2026-03-13T12:00:45Z',
      runtimeMs: 45000,
      observedDomains: ['finance'],
      changesDetected: 0,
      adjustmentsGenerated: 0,
      actionsExecuted: 0,
      error: 'Data platform connection failed',
    },
  ];

  // Workflow definitions
  const workflows = [
    { id: 'wf-001', name: 'Daily Strategy Review', status: 'active', runs: 156, lastRun: '2 hours ago' },
    { id: 'wf-002', name: 'Health Monitoring', status: 'active', runs: 892, lastRun: '5 minutes ago' },
    { id: 'wf-003', name: 'Risk Assessment', status: 'active', runs: 324, lastRun: '1 hour ago' },
    { id: 'wf-004', name: 'Performance Review', status: 'paused', runs: 45, lastRun: '3 days ago' },
  ];

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
      case 'active':
        return <CheckCircle className="text-success" size={18} />;
      case 'failed':
        return <XCircle className="text-danger" size={18} />;
      case 'paused':
        return <Pause className="text-warning" size={18} />;
      default:
        return <AlertTriangle className="text-gray-400" size={18} />;
    }
  };

  const formatDuration = (ms) => {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
    return `${(ms / 60000).toFixed(1)}min`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Workflow className="text-primary-400" />
            Orchestration
          </h1>
          <p className="text-gray-400 mt-1">
            Monitor strategy loops, workflows, and system orchestration
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg text-white">
            <Play size={18} />
            Trigger Cycle
          </button>
          <button className="p-2 hover:bg-dark-border rounded-lg text-gray-400">
            <Settings size={18} />
          </button>
        </div>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Cycles</p>
              <p className="text-2xl font-bold text-white">{cycles.filter(c => c.status === 'running').length}</p>
            </div>
            <Activity className="text-primary-400" size={24} />
          </div>
        </div>
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Completed Today</p>
              <p className="text-2xl font-bold text-success">{cycles.filter(c => c.status === 'completed').length}</p>
            </div>
            <CheckCircle className="text-success" size={24} />
          </div>
        </div>
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Failed</p>
              <p className="text-2xl font-bold text-danger">{cycles.filter(c => c.status === 'failed').length}</p>
            </div>
            <XCircle className="text-danger" size={24} />
          </div>
        </div>
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Workflows</p>
              <p className="text-2xl font-bold text-white">{workflows.filter(w => w.status === 'active').length}</p>
            </div>
            <Zap className="text-yellow-400" size={24} />
          </div>
        </div>
      </div>

      {/* Strategy Loop Cycles */}
      <div className="bg-dark-card rounded-lg border border-dark-border">
        <div className="p-4 border-b border-dark-border">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <RotateCcw className="text-primary-400" />
            Strategy Loop Cycles
          </h2>
        </div>
        <div className="divide-y divide-dark-border">
          {cycles.map(cycle => (
            <div 
              key={cycle.id}
              className="p-4 hover:bg-dark-border/50 cursor-pointer"
              onClick={() => setSelectedCycle(selectedCycle === cycle.id ? null : cycle.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  {getStatusIcon(cycle.status)}
                  <div>
                    <h3 className="text-white font-medium">{cycle.id}</h3>
                    <p className="text-sm text-gray-400">
                      Trigger: {cycle.trigger} • {new Date(cycle.startedAt).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-6">
                  <div className="text-right">
                    <p className="text-sm text-gray-400">Runtime</p>
                    <p className="text-white font-medium">{formatDuration(cycle.runtimeMs)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-400">Changes</p>
                    <p className="text-white font-medium">{cycle.changesDetected}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-400">Adjustments</p>
                    <p className="text-white font-medium">{cycle.adjustmentsGenerated}</p>
                  </div>
                  {selectedCycle === cycle.id ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                </div>
              </div>
              
              {/* Expanded Details */}
              {selectedCycle === cycle.id && (
                <div className="mt-4 pt-4 border-t border-dark-border bg-dark-bg/50">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-xs text-gray-500 uppercase">Observed Domains</p>
                      <div className="flex gap-1 mt-1">
                        {cycle.observedDomains.map(d => (
                          <span key={d} className="px-2 py-0.5 bg-primary-600/20 text-primary-400 rounded text-xs capitalize">
                            {d}
                          </span>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase">Actions Executed</p>
                      <p className="text-white mt-1">{cycle.actionsExecuted}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase">Completed At</p>
                      <p className="text-white mt-1">{new Date(cycle.completedAt).toLocaleString()}</p>
                    </div>
                    {cycle.error && (
                      <div>
                        <p className="text-xs text-gray-500 uppercase">Error</p>
                        <p className="text-danger mt-1">{cycle.error}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Workflow Registry */}
      <div className="bg-dark-card rounded-lg border border-dark-border">
        <div className="p-4 border-b border-dark-border">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Workflow className="text-primary-400" />
            Workflow Registry
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-dark-bg">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Workflow</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Total Runs</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Last Run</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {workflows.map(workflow => (
                <tr key={workflow.id} className="hover:bg-dark-border/50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <Workflow className="text-gray-400" size={16} />
                      <span className="text-white">{workflow.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`flex items-center gap-1 ${
                      workflow.status === 'active' ? 'text-success' : 'text-warning'
                    }`}>
                      {getStatusIcon(workflow.status)}
                      {workflow.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-300">{workflow.runs}</td>
                  <td className="px-4 py-3 text-gray-300">{workflow.lastRun}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button className="p-1 hover:bg-dark-border rounded text-gray-400 hover:text-white">
                        <Play size={16} />
                      </button>
                      <button className="p-1 hover:bg-dark-border rounded text-gray-400 hover:text-white">
                        <Pause size={16} />
                      </button>
                      <button className="p-1 hover:bg-dark-border rounded text-gray-400 hover:text-white">
                        <Settings size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

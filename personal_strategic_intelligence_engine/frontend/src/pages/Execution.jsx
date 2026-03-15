import { useEffect, useState } from 'react';
import { Play, Check, X, Clock, AlertTriangle, RefreshCw, Zap, DollarSign, Calendar, Mail, CheckSquare } from 'lucide-react';
import { useAppStore } from '../services/store';
import { formatDistanceToNow } from 'date-fns';
import { executionApi } from '../services/api';

const actionTypeLabels = {
  EXECUTE_TRADE: { label: 'Execute Trade', icon: DollarSign, color: 'text-success' },
  REBALANCE_PORTFOLIO: { label: 'Rebalance Portfolio', icon: DollarSign, color: 'text-success' },
  TRANSFER_FUNDS: { label: 'Transfer Funds', icon: DollarSign, color: 'text-success' },
  PAY_BILL: { label: 'Pay Bill', icon: DollarSign, color: 'text-success' },
  CREATE_TASK: { label: 'Create Task', icon: CheckSquare, color: 'text-info' },
  SCHEDULE_EVENT: { label: 'Schedule Event', icon: Calendar, color: 'text-info' },
  SEND_EMAIL: { label: 'Send Email', icon: Mail, color: 'text-info' },
  START_PROJECT: { label: 'Start Project', icon: Zap, color: 'text-purple-400' },
  ACTIVATE_STRATEGY: { label: 'Activate Strategy', icon: Zap, color: 'text-purple-400' },
  START_RESEARCH_JOB: { label: 'Start Research', icon: Zap, color: 'text-purple-400' },
  RUN_SIMULATION_BATCH: { label: 'Run Simulation', icon: Zap, color: 'text-purple-400' },
  DEPLOY_MODEL: { label: 'Deploy Model', icon: Zap, color: 'text-purple-400' },
};

const statusColors = {
  PENDING: 'badge-warning',
  APPROVED: 'badge-info',
  REJECTED: 'badge-danger',
  EXECUTING: 'bg-primary-500 animate-pulse',
  COMPLETED: 'badge-success',
  FAILED: 'badge-danger',
};

export default function Execution() {
  const [pending, setPending] = useState([]);
  const [history, setHistory] = useState([]);
  const [executing, setExecuting] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [newExecution, setNewExecution] = useState({
    action_type: 'CREATE_TASK',
    payload: {},
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [pendingRes, historyRes, executingRes] = await Promise.all([
        executionApi.pending(),
        executionApi.history(50),
        executionApi.executing(),
      ]);
      setPending(pendingRes.data.executions || []);
      setHistory(historyRes.data.history || []);
      setExecuting(executingRes.data.executions || []);
    } catch (error) {
      console.error('Failed to fetch execution data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleApprove = async (id) => {
    try {
      await executionApi.approve(id);
      fetchData();
    } catch (error) {
      console.error('Failed to approve:', error);
    }
  };

  const handleReject = async (id) => {
    try {
      await executionApi.reject(id, 'Rejected by user');
      fetchData();
    } catch (error) {
      console.error('Failed to reject:', error);
    }
  };

  const handleRun = async (id) => {
    try {
      await executionApi.run(id);
      fetchData();
    } catch (error) {
      console.error('Failed to run:', error);
    }
  };

  const handleCreate = async () => {
    try {
      await executionApi.create({
        action_type: newExecution.action_type,
        payload: newExecution.payload,
      });
      setShowCreate(false);
      setNewExecution({ action_type: 'CREATE_TASK', payload: {} });
      fetchData();
    } catch (error) {
      console.error('Failed to create execution:', error);
    }
  };

  const stats = [
    { label: 'Pending', value: pending.length, color: 'text-warning' },
    { label: 'Executing', value: executing.length, color: 'text-primary-400' },
    { label: 'Completed', value: history.filter(h => h.status === 'COMPLETED').length, color: 'text-success' },
    { label: 'Failed', value: history.filter(h => h.status === 'FAILED').length, color: 'text-danger' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Execution Console</h1>
          <p className="text-gray-400">Manage action execution and approvals</p>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchData} disabled={loading} className="btn btn-secondary flex items-center gap-2">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button onClick={() => setShowCreate(true)} className="btn btn-primary flex items-center gap-2">
            <Play className="w-4 h-4" />
            New Execution
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {stats.map(stat => (
          <div key={stat.label} className="stat-card">
            <div className="stat-value" style={{ color: stat.color }}>{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-dark-card border border-dark-border rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Create Execution</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Action Type</label>
                <select
                  value={newExecution.action_type}
                  onChange={(e) => setNewExecution({ ...newExecution, action_type: e.target.value })}
                  className="input"
                >
                  {Object.keys(actionTypeLabels).map(type => (
                    <option key={type} value={type}>{actionTypeLabels[type].label}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Payload (JSON)</label>
                <textarea
                  value={JSON.stringify(newExecution.payload, null, 2)}
                  onChange={(e) => {
                    try {
                      setNewExecution({ ...newExecution, payload: JSON.parse(e.target.value) });
                    } catch {}
                  }}
                  className="input h-32 font-mono text-sm"
                  placeholder='{"key": "value"}'
                />
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <button onClick={handleCreate} className="btn btn-primary flex-1">
                Create
              </button>
              <button onClick={() => setShowCreate(false)} className="btn btn-secondary flex-1">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pending Executions */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-warning" />
            Pending Approval
          </h2>
          
          {pending.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No pending executions</p>
          ) : (
            <div className="space-y-3">
              {pending.map(exec => {
                const actionInfo = actionTypeLabels[exec.action_type] || { label: exec.action_type };
                const ActionIcon = actionInfo.icon;
                
                return (
                  <div key={exec.id} className="p-4 bg-dark-bg rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <ActionIcon className={`w-5 h-5 ${actionInfo.color}`} />
                        <span className="font-medium text-white">{actionInfo.label}</span>
                      </div>
                      <span className={`badge ${statusColors[exec.status]}`}>{exec.status}</span>
                    </div>
                    
                    <div className="text-sm text-gray-400 mb-3">
                      Risk Score: <span className={exec.risk_score > 0.7 ? 'text-danger' : 'text-warning'}>
                        {Math.round(exec.risk_score * 100)}%
                      </span>
                    </div>
                    
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleApprove(exec.id)}
                        className="btn btn-primary text-sm py-1 px-3 flex items-center gap-1"
                      >
                        <Check className="w-3 h-3" /> Approve
                      </button>
                      <button
                        onClick={() => handleReject(exec.id)}
                        className="btn btn-danger text-sm py-1 px-3 flex items-center gap-1"
                      >
                        <X className="w-3 h-3" /> Reject
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Executing */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <Zap className="w-5 h-5 text-primary-400 animate-pulse" />
            Currently Executing
          </h2>
          
          {executing.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No actions currently running</p>
          ) : (
            <div className="space-y-3">
              {executing.map(exec => {
                const actionInfo = actionTypeLabels[exec.action_type] || { label: exec.action_type };
                const ActionIcon = actionInfo.icon;
                
                return (
                  <div key={exec.id} className="p-4 bg-dark-bg rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <ActionIcon className={`w-5 h-5 ${actionInfo.color}`} />
                      <span className="font-medium text-white">{actionInfo.label}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-pulse" />
                      <span className="text-sm text-primary-400">Executing...</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* History */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Execution History</h2>
        
        {history.length === 0 ? (
          <p className="text-gray-500 text-center py-8">No execution history</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 text-sm border-b border-dark-border">
                  <th className="pb-2">Action</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2">Time</th>
                </tr>
              </thead>
              <tbody>
                {history.slice(0, 20).map(h => {
                  const actionInfo = actionTypeLabels[h.action_type] || { label: h.action_type };
                  
                  return (
                    <tr key={h.id} className="border-b border-dark-border">
                      <td className="py-3 text-white">{actionInfo.label}</td>
                      <td className="py-3">
                        <span className={`badge ${statusColors[h.status]}`}>{h.status}</span>
                      </td>
                      <td className="py-3 text-gray-500 text-sm">
                        {formatDistanceToNow(new Date(h.timestamp), { addSuffix: true })}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

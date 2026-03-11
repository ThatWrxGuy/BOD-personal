import { useEffect } from 'react';
import { CheckSquare, Check, X, Clock, ThumbsUp, AlertCircle } from 'lucide-react';
import { useAppStore } from '../services/store';
import { formatDistanceToNow } from 'date-fns';

export default function Decisions() {
  const { decisions, fetchDecisions } = useAppStore();

  useEffect(() => {
    fetchDecisions();
  }, []);

  const pendingDecisions = decisions.filter(d => d.status === 'PENDING');
  const approvedDecisions = decisions.filter(d => d.status === 'APPROVED');
  const rejectedDecisions = decisions.filter(d => d.status === 'REJECTED');

  const getStatusIcon = (status) => {
    switch (status) {
      case 'APPROVED': return <Check className="w-4 h-4 text-success" />;
      case 'REJECTED': return <X className="w-4 h-4 text-danger" />;
      default: return <Clock className="w-4 h-4 text-warning" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Decision Console</h1>
          <p className="text-gray-400">Review and approve strategic decisions</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="stat-card">
          <Clock className="w-5 h-5 text-warning mb-2" />
          <div className="stat-value">{pendingDecisions.length}</div>
          <div className="stat-label">Pending Review</div>
        </div>
        <div className="stat-card">
          <ThumbsUp className="w-5 h-5 text-success mb-2" />
          <div className="stat-value">{approvedDecisions.length}</div>
          <div className="stat-label">Approved</div>
        </div>
        <div className="stat-card">
          <X className="w-5 h-5 text-danger mb-2" />
          <div className="stat-value">{rejectedDecisions.length}</div>
          <div className="stat-label">Rejected</div>
        </div>
      </div>

      {/* Decisions List */}
      <div className="grid gap-4">
        {decisions.length === 0 ? (
          <div className="card flex flex-col items-center justify-center py-12 text-gray-500">
            <CheckSquare className="w-12 h-12 mb-4" />
            <p>No decisions recorded yet</p>
            <p className="text-sm mt-2">Board meetings will generate decision recommendations</p>
          </div>
        ) : (
          decisions.map(decision => (
            <div key={decision.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-white">{decision.title}</h3>
                    <span className={`badge ${
                      decision.status === 'APPROVED' ? 'badge-success' :
                      decision.status === 'REJECTED' ? 'badge-danger' : 'badge-warning'
                    }`}>
                      {decision.status}
                    </span>
                  </div>
                  <p className="text-gray-400 text-sm mb-3">{decision.description}</p>
                  
                  {decision.rationale && (
                    <div className="mb-3">
                      <p className="text-xs text-gray-500 mb-1">Rationale:</p>
                      <p className="text-sm text-gray-300 bg-dark-bg p-2 rounded">{decision.rationale}</p>
                    </div>
                  )}
                  
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>Category: {decision.category}</span>
                    <span>Impact: {decision.impact_level}</span>
                    <span>{formatDistanceToNow(new Date(decision.created_at), { addSuffix: true })}</span>
                  </div>
                </div>
                
                {decision.status === 'PENDING' && (
                  <div className="flex gap-2 ml-4">
                    <button className="btn btn-primary flex items-center gap-1">
                      <Check className="w-4 h-4" />
                      Approve
                    </button>
                    <button className="btn btn-danger flex items-center gap-1">
                      <X className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

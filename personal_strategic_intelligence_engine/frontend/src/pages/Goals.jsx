import { useState, useEffect } from 'react';
import { Target, Plus, Calendar, TrendingUp, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { useAppStore } from '../services/store';
import { formatDistanceToNow, format } from 'date-fns';

export default function Goals() {
  const { goals, plans, fetchGovernance } = useAppStore();
  const [showCreateModal, setShowCreateModal] = useState(false);

  useEffect(() => {
    fetchGovernance();
  }, []);

  const activeGoals = goals.filter(g => g.status === 'ACTIVE');
  const completedGoals = goals.filter(g => g.status === 'COMPLETED');

  const getProgress = (goal) => {
    if (!goal.target_value) return 0;
    return Math.min(100, (goal.current_value / goal.target_value) * 100);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Goals & Plans</h1>
          <p className="text-gray-400">Track your strategic objectives and progress</p>
        </div>
        <button 
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Goal
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="stat-card">
          <Target className="w-5 h-5 text-primary-400 mb-2" />
          <div className="stat-value">{activeGoals.length}</div>
          <div className="stat-label">Active Goals</div>
        </div>
        <div className="stat-card">
          <CheckCircle className="w-5 h-5 text-success mb-2" />
          <div className="stat-value">{completedGoals.length}</div>
          <div className="stat-label">Completed</div>
        </div>
        <div className="stat-card">
          <AlertTriangle className="w-5 h-5 text-warning mb-2" />
          <div className="stat-value">
            {activeGoals.filter(g => {
              const progress = getProgress(g);
              return progress < 50 && g.target_date;
            }).length}
          </div>
          <div className="stat-label">At Risk</div>
        </div>
        <div className="stat-card">
          <TrendingUp className="w-5 h-5 text-success mb-2" />
          <div className="stat-value">
            {activeGoals.length > 0 
              ? Math.round(activeGoals.reduce((acc, g) => acc + getProgress(g), 0) / activeGoals.length)
              : 0}%
          </div>
          <div className="stat-label">Avg Progress</div>
        </div>
      </div>

      {/* Active Goals */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Active Goals</h2>
        <div className="grid gap-4">
          {activeGoals.length === 0 ? (
            <div className="card flex flex-col items-center justify-center py-12 text-gray-500">
              <Target className="w-12 h-12 mb-4" />
              <p>No active goals</p>
              <button 
                onClick={() => setShowCreateModal(true)}
                className="text-primary-400 hover:text-primary-300 mt-2"
              >
                Create your first goal
              </button>
            </div>
          ) : (
            activeGoals.map(goal => {
              const progress = getProgress(goal);
              const isAtRisk = progress < 50 && goal.target_date;
              
              return (
                <div key={goal.id} className="card card-hover">
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-white text-lg">{goal.title}</h3>
                        {isAtRisk && (
                          <AlertTriangle className="w-4 h-4 text-warning" />
                        )}
                      </div>
                      <p className="text-gray-400 text-sm">{goal.description}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-3xl font-bold text-white">{Math.round(progress)}%</div>
                      <div className="text-xs text-gray-500">Complete</div>
                    </div>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="progress-bar h-3">
                      <div 
                        className={`progress-fill ${isAtRisk ? 'bg-warning' : ''}`}
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-2 text-xs text-gray-500">
                      <span>{goal.current_value || 0} / {goal.target_value || 0} {goal.unit || ''}</span>
                      {goal.target_date && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          Due {formatDistanceToNow(new Date(goal.target_date), { addSuffix: true })}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  {/* Meta */}
                  <div className="flex items-center gap-4 pt-3 border-t border-dark-border">
                    <span className="badge badge-info">{goal.category}</span>
                    <span className="text-xs text-gray-500">Priority: {goal.priority}</span>
                    <span className="text-xs text-gray-500">
                      Created {formatDistanceToNow(new Date(goal.created_at), { addSuffix: true })}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Plans */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-4">Strategic Plans</h2>
        <div className="grid gap-4">
          {plans.length === 0 ? (
            <div className="card text-gray-500 text-center py-8">
              No plans created yet
            </div>
          ) : (
            plans.map(plan => (
              <div key={plan.id} className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-white">{plan.title}</h3>
                    <p className="text-gray-400 text-sm">{plan.description}</p>
                  </div>
                  <span className={`badge ${
                    plan.status === 'ACTIVE' ? 'badge-success' :
                    plan.status === 'PAUSED' ? 'badge-warning' : 'badge-info'
                  }`}>
                    {plan.status}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

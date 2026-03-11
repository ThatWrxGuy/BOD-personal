import { useEffect } from 'react';
import { 
  Radio, 
  Target, 
  AlertTriangle, 
  TrendingUp, 
  Clock,
  CheckCircle,
  Zap,
  Brain
} from 'lucide-react';
import { useAppStore } from '../services/store';
import { formatDistanceToNow } from 'date-fns';

export default function Dashboard() {
  const { 
    dashboard, 
    signals, 
    goals, 
    risks, 
    triggers,
    fetchDashboard,
    fetchSignals,
    fetchGovernance,
    fetchIntelligence 
  } = useAppStore();

  useEffect(() => {
    fetchDashboard();
  }, []);

  const recentSignals = signals.slice(0, 5);
  const highRisks = risks.filter(r => r.risk_probability >= 0.7);
  const activeGoals = goals.filter(g => g.status === 'ACTIVE');
  const pendingTriggers = triggers.filter(t => !t.is_resolved);

  const stats = [
    { 
      label: 'Active Signals', 
      value: signals.length, 
      icon: Radio,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10'
    },
    { 
      label: 'Active Goals', 
      value: activeGoals.length, 
      icon: Target,
      color: 'text-success',
      bg: 'bg-success/10'
    },
    { 
      label: 'High Risks', 
      value: highRisks.length, 
      icon: AlertTriangle,
      color: 'text-warning',
      bg: 'bg-warning/10'
    },
    { 
      label: 'Pending Triggers', 
      value: pendingTriggers.length, 
      icon: Zap,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10'
    },
  ];

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="stat-card">
            <div className="flex items-center justify-between">
              <span className="stat-label">{stat.label}</span>
              <div className={`p-2 rounded-lg ${stat.bg}`}>
                <stat.icon className={`w-5 h-5 ${stat.color}`} />
              </div>
            </div>
            <div className="stat-value mt-2">{stat.value}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Signals */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Radio className="w-5 h-5 text-blue-400" />
              Recent Signals
            </h2>
            <a href="/signals" className="text-sm text-primary-400 hover:text-primary-300">
              View All
            </a>
          </div>
          <div className="space-y-3">
            {recentSignals.length === 0 ? (
              <p className="text-gray-500 text-sm">No signals detected yet</p>
            ) : (
              recentSignals.map((signal) => (
                <div 
                  key={signal.id} 
                  className="flex items-center justify-between p-3 bg-dark-bg rounded-lg"
                >
                  <div>
                    <p className="text-white font-medium">{signal.title}</p>
                    <p className="text-xs text-gray-500">{signal.category}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className={`badge ${
                      signal.urgency >= 8 ? 'badge-danger' :
                      signal.urgency >= 6 ? 'badge-warning' : 'badge-info'
                    }`}>
                      {signal.urgency}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Top Risks */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-warning" />
              Top Risks
            </h2>
            <a href="/intelligence" className="text-sm text-primary-400 hover:text-primary-300">
              View All
            </a>
          </div>
          <div className="space-y-3">
            {highRisks.length === 0 ? (
              <p className="text-gray-500 text-sm">No high-priority risks identified</p>
            ) : (
              highRisks.slice(0, 5).map((risk) => (
                <div 
                  key={risk.id} 
                  className="p-3 bg-dark-bg rounded-lg"
                >
                  <div className="flex items-center justify-between mb-1">
                    <p className="text-white font-medium">{risk.risk_description.slice(0, 50)}...</p>
                    <span className="text-sm text-warning">
                      {Math.round(risk.risk_probability * 100)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <span>{risk.risk_category}</span>
                    <span>•</span>
                    <span>{risk.time_horizon}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Active Goals */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Target className="w-5 h-5 text-success" />
              Active Goals
            </h2>
            <a href="/goals" className="text-sm text-primary-400 hover:text-primary-300">
              View All
            </a>
          </div>
          <div className="space-y-3">
            {activeGoals.length === 0 ? (
              <p className="text-gray-500 text-sm">No active goals</p>
            ) : (
              activeGoals.slice(0, 4).map((goal) => {
                const progress = goal.target_value 
                  ? Math.min(100, (goal.current_value / goal.target_value) * 100)
                  : 0;
                return (
                  <div key={goal.id} className="p-3 bg-dark-bg rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-white font-medium">{goal.title}</p>
                      <span className="text-sm text-gray-400">{Math.round(progress)}%</span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill" 
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                      <Clock className="w-3 h-3" />
                      {goal.target_date 
                        ? `Due ${formatDistanceToNow(new Date(goal.target_date))}`
                        : 'No deadline'}
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* Pending Triggers */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Zap className="w-5 h-5 text-purple-400" />
              Pending Triggers
            </h2>
            <a href="/governance" className="text-sm text-primary-400 hover:text-primary-300">
              View All
            </a>
          </div>
          <div className="space-y-3">
            {pendingTriggers.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-gray-500">
                <CheckCircle className="w-8 h-8 text-success mb-2" />
                <p className="text-sm">All triggers resolved</p>
              </div>
            ) : (
              pendingTriggers.slice(0, 4).map((trigger) => (
                <div 
                  key={trigger.id} 
                  className="p-3 bg-dark-bg rounded-lg"
                >
                  <div className="flex items-center justify-between">
                    <p className="text-white font-medium">{trigger.trigger_type}</p>
                    <span className={`badge ${
                      trigger.severity === 'CRITICAL' ? 'badge-danger' :
                      trigger.severity === 'HIGH' ? 'badge-warning' : 'badge-info'
                    }`}>
                      {trigger.severity}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">{trigger.trigger_reason}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Forecast Alerts */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
          <Brain className="w-5 h-5 text-primary-400" />
          Intelligence Insights
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
            <TrendingUp className="w-6 h-6 text-success mb-2" />
            <h3 className="font-medium text-white">Trend Analysis</h3>
            <p className="text-sm text-gray-500 mt-1">
              {dashboard?.goals || 0} active goals being tracked
            </p>
          </div>
          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
            <Brain className="w-6 h-6 text-primary-400 mb-2" />
            <h3 className="font-medium text-white">Forecasts</h3>
            <p className="text-sm text-gray-500 mt-1">
              {dashboard?.goals_at_risk || 0} goals at risk requiring attention
            </p>
          </div>
          <div className="p-4 bg-dark-bg rounded-lg border border-dark-border">
            <AlertTriangle className="w-6 h-6 text-warning mb-2" />
            <h3 className="font-medium text-white">Risk Assessment</h3>
            <p className="text-sm text-gray-500 mt-1">
              {dashboard?.pending_triggers || 0} triggers awaiting review
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

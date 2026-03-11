import { useState, useEffect } from 'react';
import { Shield, Calendar, Zap, Bell, RefreshCw, Play } from 'lucide-react';
import { useAppStore } from '../services/store';
import { formatDistanceToNow } from 'date-fns';

export default function Governance() {
  const { goals, plans, triggers, fetchGovernance } = useAppStore();
  const [activeTab, setActiveTab] = useState('triggers');

  useEffect(() => {
    fetchGovernance();
  }, []);

  const pendingTriggers = triggers.filter(t => !t.is_resolved);
  const resolvedTriggers = triggers.filter(t => t.is_resolved);

  const tabs = [
    { id: 'triggers', label: 'Triggers', count: pendingTriggers.length },
    { id: 'schedules', label: 'Schedules', count: 5 },
    { id: 'reviews', label: 'Reviews', count: 0 },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Governance Panel</h1>
          <p className="text-gray-400">Monitor board governance activity and triggers</p>
        </div>
        <button 
          onClick={fetchGovernance}
          className="btn btn-secondary flex items-center gap-2"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
              activeTab === tab.id
                ? 'bg-primary-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-dark-border'
            }`}
          >
            {tab.label}
            {tab.count > 0 && (
              <span className="bg-warning/20 text-warning text-xs px-2 py-0.5 rounded-full">
                {tab.count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Trigger Events */}
      {activeTab === 'triggers' && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-white">Trigger Events</h2>
          
          {/* Pending */}
          <div className="card">
            <h3 className="text-sm font-medium text-gray-400 mb-3">Pending ({pendingTriggers.length})</h3>
            {pendingTriggers.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Zap className="w-8 h-8 mx-auto mb-2 text-success" />
                <p>All triggers resolved</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pendingTriggers.map(trigger => (
                  <div key={trigger.id} className="p-4 bg-dark-bg rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Zap className={`w-5 h-5 ${
                          trigger.severity === 'CRITICAL' ? 'text-danger' :
                          trigger.severity === 'HIGH' ? 'text-warning' : 'text-info'
                        }`} />
                        <span className="font-medium text-white">{trigger.trigger_type}</span>
                      </div>
                      <span className={`badge ${
                        trigger.severity === 'CRITICAL' ? 'badge-danger' :
                        trigger.severity === 'HIGH' ? 'badge-warning' : 'badge-info'
                      }`}>
                        {trigger.severity}
                      </span>
                    </div>
                    <p className="text-gray-400 text-sm mb-2">{trigger.trigger_reason}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {formatDistanceToNow(new Date(trigger.created_at), { addSuffix: true })}
                      </span>
                      <button className="btn btn-primary text-sm py-1 px-3">
                        Review
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Resolved */}
          {resolvedTriggers.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-medium text-gray-400 mb-3">Resolved ({resolvedTriggers.length})</h3>
              <div className="space-y-3">
                {resolvedTriggers.slice(0, 5).map(trigger => (
                  <div key={trigger.id} className="p-3 bg-dark-bg rounded-lg opacity-60">
                    <div className="flex items-center justify-between">
                      <span className="text-white">{trigger.trigger_type}</span>
                      <span className="badge badge-success">Resolved</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Schedules */}
      {activeTab === 'schedules' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Board Meeting Schedules</h2>
          <div className="space-y-3">
            {[
              { type: 'DAILY', frequency: 'Every day', next: 'Tomorrow 9:00 AM' },
              { type: 'WEEKLY', frequency: 'Every Monday', next: 'Monday 9:00 AM' },
              { type: 'MONTHLY', frequency: 'First of month', next: 'April 1, 9:00 AM' },
              { type: 'QUARTERLY', frequency: 'First of quarter', next: 'April 1, 9:00 AM' },
              { type: 'ANNUAL', frequency: 'January 1st', next: 'January 1, 9:00 AM' },
            ].map(schedule => (
              <div key={schedule.type} className="flex items-center justify-between p-4 bg-dark-bg rounded-lg">
                <div>
                  <h3 className="font-medium text-white">{schedule.type}</h3>
                  <p className="text-sm text-gray-400">{schedule.frequency}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-primary-400">{schedule.next}</p>
                  <span className="badge badge-success">Active</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Reviews */}
      {activeTab === 'reviews' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Governance Reviews</h2>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {['DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'ANNUAL'].map(type => (
              <button key={type} className="p-4 bg-dark-bg rounded-lg border border-dark-border hover:border-primary-500 transition-colors text-center">
                <Calendar className="w-8 h-8 mx-auto mb-2 text-primary-400" />
                <p className="font-medium text-white">{type}</p>
                <p className="text-xs text-gray-500 mt-1">Run Review</p>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

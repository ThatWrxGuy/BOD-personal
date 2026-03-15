/**
 * FinanceHistoryPanel - displays chronological financial system events
 */

import React, { useState } from 'react';
import { TimelineEvent } from '../components';

const FinanceHistoryPanel = ({ snapshots, auditLog, loading }) => {
  const [activeTab, setActiveTab] = useState('all');

  if (loading) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial History</h2>
        <div className="animate-pulse">
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Combine snapshots and audit log into timeline events
  const timelineEvents = React.useMemo(() => {
    const events = [];

    // Add snapshots as events
    if (snapshots && snapshots.length > 0) {
      snapshots.forEach((snapshot) => {
        events.push({
          timestamp: snapshot.timestamp,
          event_type: 'snapshot_created',
          description: `Financial snapshot: Net Worth ${formatCurrency(snapshot.net_worth)}`,
          event_reference: `snapshot-${snapshot.snapshot_id}`,
          profile_id: snapshot.profile_id,
        });
      });
    }

    // Add audit log events
    if (auditLog && auditLog.length > 0) {
      auditLog.forEach((event) => {
        events.push({
          timestamp: event.timestamp,
          event_type: event.event_type,
          description: event.description,
          event_reference: event.event_reference,
          profile_id: event.profile_id,
        });
      });
    }

    // Sort by timestamp descending
    events.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    return events;
  }, [snapshots, auditLog]);

  const formatCurrency = (v) => new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v || 0);

  const filterOptions = [
    { value: 'all', label: 'All Events' },
    { value: 'snapshot', label: 'Snapshots' },
    { value: 'recommendation', label: 'Recommendations' },
    { value: 'simulation', label: 'Simulations' },
    { value: 'decision', label: 'Decisions' },
    { value: 'board', label: 'Board Briefs' },
  ];

  const filteredEvents = React.useMemo(() => {
    if (activeTab === 'all') return timelineEvents;
    
    const filters = {
      snapshot: ['snapshot_created'],
      recommendation: ['recommendation_generated'],
      simulation: ['simulation_run'],
      decision: ['decision_requested', 'decision_resolved'],
      board: ['board_brief_generated'],
    };

    return timelineEvents.filter((event) => 
      filters[activeTab]?.includes(event.event_type)
    );
  }, [timelineEvents, activeTab]);

  if (timelineEvents.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial History</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">No history available.</p>
          <p className="text-sm text-gray-400 mt-1">Financial events will appear here as they occur.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Financial History ({filteredEvents.length})
        </h2>
        <div className="flex gap-2">
          {filterOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setActiveTab(option.value)}
              className={`px-3 py-1 text-sm rounded ${
                activeTab === option.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      <div className="divide-y">
        {filteredEvents.map((event, index) => (
          <TimelineEvent key={index} event={event} />
        ))}
      </div>
    </div>
  );
};

export default FinanceHistoryPanel;

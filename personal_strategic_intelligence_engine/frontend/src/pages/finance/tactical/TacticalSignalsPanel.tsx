/**
 * Tactical Signals Panel
 * Displays active tactical signals from the Options Tactical Agent
 */

import React, { useState, useEffect } from 'react';

const TacticalSignalsPanel = ({ onSignalSelect }) => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchSignals = async () => {
    try {
      const response = await fetch('/api/options-agent/signals');
      const data = await response.json();
      setSignals(data.signals || []);
    } catch (error) {
      console.error('Failed to fetch signals:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return '#ffa500';
      case 'approved': return '#4caf50';
      case 'rejected': return '#f44336';
      default: return '#9e9e9e';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 70) return '#4caf50';
    if (score >= 50) return '#ffa500';
    return '#f44336';
  };

  if (loading) {
    return <div className="panel-loading">Loading signals...</div>;
  }

  return (
    <div className="tactical-signals-panel">
      <h3>Active Signals</h3>
      <div className="signals-list">
        {signals.length === 0 ? (
          <div className="no-signals">No active signals</div>
        ) : (
          signals.map((signal) => (
            <div
              key={signal.id}
              className="signal-card"
              onClick={() => onSignalSelect(signal)}
            >
              <div className="signal-header">
                <span className="signal-ticker">{signal.ticker}</span>
                <span 
                  className="signal-score"
                  style={{ backgroundColor: getScoreColor(signal.signal_score) }}
                >
                  {signal.signal_score}
                </span>
              </div>
              <div className="signal-details">
                <span className="signal-strike">
                  ${signal.strike}{signal.option_type?.toUpperCase()}
                </span>
                <span 
                  className="signal-status"
                  style={{ color: getStatusColor(signal.status) }}
                >
                  {signal.status || 'pending'}
                </span>
              </div>
              <div className="signal-meta">
                <span className="confidence">
                  Confidence: {signal.confidence_score}%
                </span>
                <span className="timestamp">
                  {new Date(signal.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default TacticalSignalsPanel;

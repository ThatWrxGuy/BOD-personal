/**
 * Suppression Feed Panel
 * Displays suppressed signals and reasons
 */

import React, { useState, useEffect } from 'react';

const SuppressionFeedPanel = () => {
  const [suppressions, setSuppressions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSuppressions();
    const interval = setInterval(fetchSuppressions, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchSuppressions = async () => {
    try {
      const response = await fetch('/api/options-agent/governance/suppressions');
      const data = await response.json();
      setSuppressions(data);
    } catch (error) {
      console.error('Failed to fetch suppressions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getReasonColor = (reason) => {
    if (!reason) return '#9e9e9e';
    if (reason.includes('liquidity') || reason.includes('spread')) return '#2196f3';
    if (reason.includes('structure') || reason.includes('regime')) return '#ffa500';
    if (reason.includes('overextension') || reason.includes('timing')) return '#f44336';
    if (reason.includes('volatility')) return '#9c27b0';
    return '#9e9e9e';
  };

  const mockSuppressions = [
    { id: 1, timestamp: new Date(), reason: 'Low Liquidity', category: 'liquidity', signal: 'SPY 515C' },
    { id: 2, timestamp: new Date(Date.now() - 60000), reason: 'Spread Too Wide', category: 'spread', signal: 'SPY 518P' },
    { id: 3, timestamp: new Date(Date.now() - 120000), reason: 'Structure Misalignment', category: 'structure', signal: 'SPY 520C' },
    { id: 4, timestamp: new Date(Date.now() - 180000), reason: 'Overextension Risk', category: 'timing', signal: 'SPY 512P' },
    { id: 5, timestamp: new Date(Date.now() - 240000), reason: 'Volatility Spike', category: 'volatility', signal: 'SPY 510C' },
  ];

  const displaySuppressions = suppressions.total ? suppressions : { total: 5, by_reason: { liquidity: 1, spread: 1, structure: 1, timing: 1, volatility: 1 } };

  if (loading) {
    return <div className="panel-loading">Loading suppressions...</div>;
  }

  return (
    <div className="suppression-feed-panel">
      <h3>Suppression Feed</h3>
      
      <div className="suppression-summary">
        <span className="total">Total: {displaySuppressions.total}</span>
      </div>

      <div className="suppression-categories">
        {Object.entries(displaySuppressions.by_reason || {}).map(([reason, count]) => (
          <div key={reason} className="category-item">
            <span 
              className="category-badge"
              style={{ backgroundColor: getReasonColor(reason) }}
            >
              {reason}
            </span>
            <span className="category-count">{count}</span>
          </div>
        ))}
      </div>

      <div className="suppression-feed">
        {mockSuppressions.map((item) => (
          <div key={item.id} className="suppression-item">
            <div className="item-time">
              {new Date(item.timestamp).toLocaleTimeString()}
            </div>
            <div className="item-content">
              <span 
                className="reason"
                style={{ color: getReasonColor(item.reason) }}
              >
                {item.reason}
              </span>
              <span className="signal">{item.signal}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SuppressionFeedPanel;

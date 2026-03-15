/**
 * Tactical Learning Panel
 * Displays learning insights and calibration data
 */

import React, { useState, useEffect } from 'react';

const TacticalLearningPanel = () => {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSnapshot();
    const interval = setInterval(fetchSnapshot, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchSnapshot = async () => {
    try {
      const response = await fetch('/api/options-agent/learning/snapshot');
      const data = await response.json();
      setSnapshot(data);
    } catch (error) {
      console.error('Failed to fetch learning snapshot:', error);
    } finally {
      setLoading(false);
    }
  };

  const getMetricColor = (value, type) => {
    if (type === 'win_rate') {
      return value >= 60 ? '#4caf50' : value >= 50 ? '#ffa500' : '#f44336';
    }
    if (type === 'expectancy') {
      return value > 0 ? '#4caf50' : '#f44336';
    }
    return '#2196f3';
  };

  if (loading) {
    return <div className="panel-loading">Loading learning data...</div>;
  }

  if (!snapshot) {
    return <div className="no-data">No learning data available</div>;
  }

  const calibration = snapshot.calibration_report || {};
  const features = snapshot.feature_report || {};

  return (
    <div className="tactical-learning-panel">
      <h3>Tactical Learning</h3>
      
      <div className="learning-summary">
        <div className="summary-metric">
          <label>Signals Analyzed</label>
          <span className="value">{snapshot.total_signals_analyzed}</span>
        </div>
        <div className="summary-metric">
          <label>Win Rate</label>
          <span 
            className="value"
            style={{ color: getMetricColor(snapshot.overall_win_rate, 'win_rate') }}
          >
            {snapshot.overall_win_rate?.toFixed(1)}%
          </span>
        </div>
        <div className="summary-metric">
          <label>Expectancy</label>
          <span 
            className="value"
            style={{ color: getMetricColor(snapshot.overall_expectancy, 'expectancy') }}
          >
            +{snapshot.overall_expectancy?.toFixed(2)}
          </span>
        </div>
      </div>

      {calibration.buckets && (
        <div className="calibration-section">
          <label>Confidence Calibration</label>
          <div className="calibration-buckets">
            {calibration.buckets.map((bucket) => (
              <div key={bucket.bucket} className="bucket-item">
                <span className="bucket-name">{bucket.bucket}</span>
                <span className="bucket-count">{bucket.signal_count}</span>
                <span 
                  className="bucket-winrate"
                  style={{ color: getMetricColor(bucket.win_rate, 'win_rate') }}
                >
                  {bucket.win_rate?.toFixed(0)}%
                </span>
                <span className="bucket-diff">
                  {bucket.predicted_vs_actual > 0 ? '+' : ''}{bucket.predicted_vs_actual?.toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
          {calibration.is_overconfident && (
            <div className="calibration-warning">
              ⚠️ System is overconfident - actual win rates lower than predicted
            </div>
          )}
        </div>
      )}

      {features.top_positive_predictors && (
        <div className="features-section">
          <label>Top Positive Predictors</label>
          <div className="feature-list">
            {features.top_positive_predictors.slice(0, 5).map((feature, idx) => (
              <div key={idx} className="feature-item">
                <span className="feature-name">{feature.feature_name}</span>
                <span className="feature-power">
                  {(feature.predictive_power * 100).toFixed(0)}%
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {snapshot.pending_proposals && snapshot.pending_proposals.length > 0 && (
        <div className="proposals-section">
          <label>Pending Proposals ({snapshot.pending_proposals.length})</label>
          <div className="proposals-list">
            {snapshot.pending_proposals.map((proposal) => (
              <div key={proposal.proposal_id} className="proposal-item">
                <span className="proposal-type">{proposal.proposal_type}</span>
                <span className="proposal-target">{proposal.target_feature}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TacticalLearningPanel;

/**
 * Intelligence Evolution Panel
 * Displays intelligence evolution insights
 */

import React, { useState, useEffect } from 'react';

const IntelligenceEvolutionPanel = () => {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSnapshot();
    const interval = setInterval(fetchSnapshot, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchSnapshot = async () => {
    try {
      const response = await fetch('/api/intelligence/evolution/snapshot');
      const data = await response.json();
      setSnapshot(data);
    } catch (error) {
      console.error('Failed to fetch evolution snapshot:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="panel-loading">Loading intelligence evolution...</div>;
  }

  if (!snapshot) {
    return <div className="no-data">No evolution data available</div>;
  }

  const patterns = snapshot.patterns || [];
  const features = snapshot.features || [];
  const optimizations = snapshot.optimizations || [];
  const summary = snapshot.learning_summary || {};

  return (
    <div className="intelligence-evolution-panel">
      <h3>Intelligence Evolution</h3>
      
      <div className="evolution-summary">
        <div className="summary-item">
          <label>Patterns</label>
          <span className="value">{summary.total_patterns_discovered || 0}</span>
        </div>
        <div className="summary-item">
          <label>Top Features</label>
          <span className="value">{summary.top_features || 0}</span>
        </div>
        <div className="summary-item">
          <label>Calibration</label>
          <span className="value">{summary.calibration_accuracy?.toFixed(1) || 0}%</span>
        </div>
      </div>

      {patterns.length > 0 && (
        <div className="patterns-section">
          <label>Discovered Patterns</label>
          <div className="patterns-list">
            {patterns.slice(0, 3).map((pattern) => (
              <div key={pattern.pattern_id} className="pattern-item">
                <span className="pattern-type">{pattern.pattern_type}</span>
                <span className="pattern-winrate">{pattern.win_rate?.toFixed(0)}%</span>
                <span className="pattern-confidence">{pattern.confidence?.toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {features.length > 0 && (
        <div className="features-section">
          <label>Top Features</label>
          <div className="features-list">
            {features.slice(0, 5).map((feature, idx) => (
              <div key={idx} className="feature-item">
                <span className="feature-name">{feature.feature_name}</span>
                <span className="feature-score">{(feature.importance_score * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {optimizations.length > 0 && (
        <div className="optimizations-section">
          <label>Optimization Proposals ({optimizations.length})</label>
          <div className="optimizations-list">
            {optimizations.map((opt) => (
              <div key={opt.proposal_id} className="optimization-item">
                <span className="opt-type">{opt.optimization_type}</span>
                <span className="opt-impact">+{opt.expected_improvement?.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default IntelligenceEvolutionPanel;

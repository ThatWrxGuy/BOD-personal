/**
 * Execution Timing Panel
 * Displays timing intelligence from the Execution Timing Agent
 */

import React, { useState, useEffect } from 'react';

const ExecutionTimingPanel = () => {
  const [timing, setTiming] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTiming();
    const interval = setInterval(fetchTiming, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchTiming = async () => {
    try {
      const response = await fetch('/api/options-agent/timing/decision');
      const data = await response.json();
      setTiming(data);
    } catch (error) {
      console.error('Failed to fetch timing:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDecisionColor = (decision) => {
    if (!decision) return '#9e9e9e';
    if (decision === 'enter_now') return '#4caf50';
    if (decision === 'wait_for_pullback' || decision === 'wait_for_confirmation') return '#ffa500';
    if (decision === 'avoid_entry' || decision === 'defer_signal') return '#f44336';
    return '#2196f3';
  };

  const getStateColor = (state) => {
    if (!state) return '#9e9e9e';
    if (state.includes('strong') || state.includes('healthy')) return '#4caf50';
    if (state.includes('weak') || state.includes('failed')) return '#f44336';
    return '#ffa500';
  };

  if (loading) {
    return <div className="panel-loading">Loading timing...</div>;
  }

  if (!timing) {
    return <div className="no-data">No timing data available</div>;
  }

  const momentum = timing.momentum || {};
  const pullback = timing.pullback || {};
  const breakout = timing.breakout || {};
  const overextension = timing.overextension || {};
  const recommendation = timing.entry_recommendation || {};

  return (
    <div className="execution-timing-panel">
      <h3>Execution Timing</h3>
      
      <div className="timing-decision">
        <label>Decision</label>
        <span 
          className="decision-badge"
          style={{ backgroundColor: getDecisionColor(timing.timing_decision) }}
        >
          {timing.timing_decision?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
        </span>
        <span className="timing-confidence">
          Confidence: {timing.timing_confidence?.toFixed(0) || 0}%
        </span>
      </div>

      <div className="timing-components">
        <div className="timing-item">
          <label>Momentum</label>
          <span style={{ color: getStateColor(momentum.state) }}>
            {momentum.state?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
          </span>
        </div>

        <div className="timing-item">
          <label>Pullback</label>
          <span style={{ color: getStateColor(pullback.state) }}>
            {pullback.state?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
          </span>
        </div>

        <div className="timing-item">
          <label>Breakout</label>
          <span style={{ color: getStateColor(breakout.state) }}>
            {breakout.state?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
          </span>
        </div>

        <div className="timing-item">
          <label>Extension</label>
          <span style={{ color: getStateColor(overextension.condition) }}>
            {overextension.condition?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
          </span>
        </div>
      </div>

      <div className="entry-zone">
        <label>Entry Zone</label>
        <span className="zone-values">
          ${recommendation.entry_zone_low?.toFixed(2) || '---'} - ${recommendation.entry_zone_high?.toFixed(2) || '---'}
        </span>
      </div>

      <div className="stop-level">
        <label>Stop Level</label>
        <span className="stop-value">
          ${recommendation.stop_level?.toFixed(2) || '---'}
        </span>
      </div>

      {timing.reasoning_summary && (
        <div className="timing-reasoning">
          <label>Reasoning</label>
          <p>{timing.reasoning_summary}</p>
        </div>
      )}

      {timing.suppression_flags?.length > 0 && (
        <div className="timing-warnings">
          <label>Warnings</label>
          {timing.suppression_flags.map((flag, idx) => (
            <span key={idx} className="warning-badge">{flag}</span>
          ))}
        </div>
      )}
    </div>
  );
};

export default ExecutionTimingPanel;

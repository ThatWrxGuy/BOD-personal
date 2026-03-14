/**
 * Strategy Simulation Panel
 * Displays strategy simulation and discovery insights
 */

import React, { useState, useEffect } from 'react';

const StrategySimulationPanel = () => {
  const [snapshot, setSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSnapshot();
    const interval = setInterval(fetchSnapshot, 60000);
    return () => clearInterval(interval);
  }, []);

  const fetchSnapshot = async () => {
    try {
      const response = await fetch('/api/strategy/snapshot');
      const data = await response.json();
      setSnapshot(data);
    } catch (error) {
      console.error('Failed to fetch simulation snapshot:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="panel-loading">Loading strategy simulations...</div>;
  }

  if (!snapshot) {
    return <div className="no-data">No simulation data available</div>;
  }

  const simulations = snapshot.simulations || [];
  const discoveries = snapshot.discoveries || [];
  const proposals = snapshot.proposals || [];
  const summary = snapshot.summary || {};

  return (
    <div className="strategy-simulation-panel">
      <h3>Strategy Simulation</h3>
      
      <div className="simulation-summary">
        <div className="summary-item">
          <label>Simulations</label>
          <span className="value">{summary.total_simulations || 0}</span>
        </div>
        <div className="summary-item">
          <label>Winners</label>
          <span className="value">{summary.winning_candidates || 0}</span>
        </div>
        <div className="summary-item">
          <label>Proposals</label>
          <span className="value">{summary.pending_proposals || 0}</span>
        </div>
      </div>

      {simulations.length > 0 && (
        <div className="simulations-section">
          <label>Strategy Performance</label>
          <div className="simulations-list">
            {simulations.slice(0, 4).map((sim) => (
              <div key={sim.simulation_id} className="simulation-item">
                <span className="sim-name">{sim.strategy_name}</span>
                <span className="sim-expectancy">Exp: {sim.metrics?.expectancy?.toFixed(2)}</span>
                <span className="sim-sharpe">Sharpe: {sim.metrics?.sharpe_ratio?.toFixed(1)}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {discoveries.length > 0 && (
        <div className="discoveries-section">
          <label>Pattern Discoveries</label>
          <div className="discoveries-list">
            {discoveries.slice(0, 3).map((disc) => (
              <div key={disc.discovery_id} className="discovery-item">
                <span className="disc-name">{disc.pattern_name}</span>
                <span className="disc-winrate">{disc.win_rate?.toFixed(0)}%</span>
                <span className="disc-confidence">{disc.confidence?.toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {proposals.length > 0 && (
        <div className="proposals-section">
          <label>Optimization Proposals</label>
          <div className="proposals-list">
            {proposals.map((prop) => (
              <div key={prop.proposal_id} className="proposal-item">
                <span className="prop-param">{prop.target_parameter}</span>
                <span className="prop-impact">+{prop.expected_improvement?.toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StrategySimulationPanel;

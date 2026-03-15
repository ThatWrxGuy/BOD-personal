/**
 * Market Structure Panel
 * Displays current market structure intelligence
 */

import React, { useState, useEffect } from 'react';

const MarketStructurePanel = () => {
  const [structure, setStructure] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStructure();
    const interval = setInterval(fetchStructure, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchStructure = async () => {
    try {
      const response = await fetch('/api/options-agent/structure/snapshot');
      const data = await response.json();
      setStructure(data);
    } catch (error) {
      console.error('Failed to fetch structure:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStateColor = (state) => {
    if (!state) return '#9e9e9e';
    if (state.includes('acceptance') || state.includes('trend')) return '#4caf50';
    if (state.includes('chop') || state.includes('range')) return '#ffa500';
    if (state.includes('reversal')) return '#f44336';
    return '#2196f3';
  };

  if (loading) {
    return <div className="panel-loading">Loading market structure...</div>;
  }

  if (!structure) {
    return <div className="no-data">No structure data available</div>;
  }

  const vwap = structure.vwap || {};
  const dayType = structure.day_type || {};
  const volatility = structure.volatility_state || {};

  return (
    <div className="market-structure-panel">
      <h3>Market Structure</h3>
      
      <div className="structure-grid">
        <div className="structure-item">
          <label>Day Type</label>
          <span 
            className="value"
            style={{ color: getStateColor(dayType.day_type) }}
          >
            {dayType.day_type?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
          </span>
          <span className="confidence">
            {dayType.confidence ? `${(dayType.confidence * 100).toFixed(0)}%` : ''}
          </span>
        </div>

        <div className="structure-item">
          <label>VWAP State</label>
          <span 
            className="value"
            style={{ color: getStateColor(vwap.state) }}
          >
            {vwap.state?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
          </span>
          <span className="distance">
            {vwap.distance_pct ? `${vwap.distance_pct.toFixed(2)}%` : ''}
          </span>
        </div>

        <div className="structure-item">
          <label>Volatility</label>
          <span 
            className="value"
            style={{ color: getStateColor(volatility.state) }}
          >
            {volatility.state?.replace(/_/g, ' ').toUpperCase() || 'N/A'}
          </span>
          <span className="realized">
            {volatility.realized_volatility ? `${volatility.realized_volatility.toFixed(1)}%` : ''}
          </span>
        </div>

        <div className="structure-item">
          <label>Direction</label>
          <span className="value bias">
            {structure.directional_bias?.toUpperCase() || 'NEUTRAL'}
          </span>
        </div>

        <div className="structure-item">
          <label>Structure Quality</label>
          <div className="score-bar">
            <div 
              className="score-fill"
              style={{ 
                width: `${structure.structure_quality_score || 0}%`,
                backgroundColor: getStateColor(structure.structure_quality_score > 60 ? 'good' : 'bad')
              }}
            />
          </div>
          <span className="score-value">
            {structure.structure_quality_score?.toFixed(0) || 0}
          </span>
        </div>

        <div className="structure-item">
          <label>Tactical Suitability</label>
          <div className="score-bar">
            <div 
              className="score-fill"
              style={{ 
                width: `${structure.tactical_suitability_score || 0}%`,
                backgroundColor: getStateColor(structure.tactical_suitability_score > 60 ? 'good' : 'bad')
              }}
            />
          </div>
          <span className="score-value">
            {structure.tactical_suitability_score?.toFixed(0) || 0}
          </span>
        </div>
      </div>

      {structure.suppression_flags?.length > 0 && (
        <div className="suppression-warnings">
          <label>Suppression Flags</label>
          {structure.suppression_flags.map((flag, idx) => (
            <span key={idx} className="warning-tag">{flag}</span>
          ))}
        </div>
      )}
    </div>
  );
};

export default MarketStructurePanel;

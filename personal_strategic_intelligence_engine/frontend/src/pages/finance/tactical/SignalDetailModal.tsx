/**
 * Signal Detail Modal
 * Detailed signal review interface
 */

import React, { useState, useEffect } from 'react';

const SignalDetailModal = ({ signal, isOpen, onClose }) => {
  const [structure, setStructure] = useState(null);
  const [timing, setTiming] = useState(null);
  const [brief, setBrief] = useState(null);

  useEffect(() => {
    if (signal && isOpen) {
      fetchDetailData();
    }
  }, [signal, isOpen]);

  const fetchDetailData = async () => {
    try {
      const [structureRes, timingRes] = await Promise.all([
        fetch('/api/options-agent/structure/snapshot'),
        fetch('/api/options-agent/timing/decision'),
      ]);
      
      const structureData = await structureRes.json();
      const timingData = await timingRes.json();
      
      setStructure(structureData);
      setTiming(timingData);
      
      setBrief({
        thesis: 'Bullish SPY 0DTE based on trend_up regime',
        rationale: 'Signal generated based on delta velocity, gamma exposure, and momentum alignment',
        portfolio_fit: 'FEASIBLE',
        capital_required: 500,
        risk_budget_impact: 15,
        requires_ceo_approval: false,
        requires_finance_approval: true,
      });
    } catch (error) {
      console.error('Failed to fetch detail data:', error);
    }
  };

  if (!isOpen || !signal) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content signal-detail-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Signal Detail: {signal.ticker} ${signal.strike}{signal.option_type?.toUpperCase()}</h2>
          <button className="close-btn" onClick={onClose}>&times;</button>
        </div>

        <div className="modal-body">
          <section className="detail-section">
            <h3>Signal Summary</h3>
            <div className="detail-grid">
              <div className="detail-item">
                <label>Instrument</label>
                <span>{signal.ticker}</span>
              </div>
              <div className="detail-item">
                <label>Strike</label>
                <span>${signal.strike}</span>
              </div>
              <div className="detail-item">
                <label>Expiration</label>
                <span>{signal.expiration_date}</span>
              </div>
              <div className="detail-item">
                <label>Signal Score</label>
                <span>{signal.signal_score}</span>
              </div>
              <div className="detail-item">
                <label>Confidence</label>
                <span>{signal.confidence_score}%</span>
              </div>
              <div className="detail-item">
                <label>Status</label>
                <span>{signal.status || 'pending'}</span>
              </div>
            </div>
          </section>

          <section className="detail-section">
            <h3>Market Structure Context</h3>
            {structure ? (
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Day Type</label>
                  <span>{structure.day_type?.day_type?.replace(/_/g, ' ').toUpperCase()}</span>
                </div>
                <div className="detail-item">
                  <label>VWAP State</label>
                  <span>{structure.vwap?.state?.replace(/_/g, ' ').toUpperCase()}</span>
                </div>
                <div className="detail-item">
                  <label>Volatility</label>
                  <span>{structure.volatility_state?.state?.replace(/_/g, ' ').toUpperCase()}</span>
                </div>
                <div className="detail-item">
                  <label>Structure Quality</label>
                  <span>{structure.structure_quality_score?.toFixed(0)}</span>
                </div>
                <div className="detail-item">
                  <label>Directional Bias</label>
                  <span>{structure.directional_bias?.toUpperCase()}</span>
                </div>
                <div className="detail-item">
                  <label>Tactical Suitability</label>
                  <span>{structure.tactical_suitability_score?.toFixed(0)}</span>
                </div>
              </div>
            ) : (
              <div className="loading">Loading...</div>
            )}
          </section>

          <section className="detail-section">
            <h3>Execution Timing Context</h3>
            {timing ? (
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Timing Decision</label>
                  <span>{timing.timing_decision?.replace(/_/g, ' ').toUpperCase()}</span>
                </div>
                <div className="detail-item">
                  <label>Momentum</label>
                  <span>{timing.momentum?.state?.replace(/_/g, ' ').toUpperCase()}</span>
                </div>
                <div className="detail-item">
                  <label>Pullback</label>
                  <span>{timing.pullback?.state?.replace(/_/g, ' ').toUpperCase()}</span>
                </div>
                <div className="detail-item">
                  <label>Entry Zone</label>
                  <span>${timing.entry_recommendation?.entry_zone_low?.toFixed(2)} - ${timing.entry_recommendation?.entry_zone_high?.toFixed(2)}</span>
                </div>
                <div className="detail-item">
                  <label>Stop Level</label>
                  <span>${timing.entry_recommendation?.stop_level?.toFixed(2)}</span>
                </div>
                <div className="detail-item">
                  <label>Timing Confidence</label>
                  <span>{timing.timing_confidence?.toFixed(0)}%</span>
                </div>
              </div>
            ) : (
              <div className="loading">Loading...</div>
            )}
          </section>

          <section className="detail-section">
            <h3>Portfolio Context</h3>
            {brief ? (
              <div className="detail-grid">
                <div className="detail-item">
                  <label>Portfolio Fit</label>
                  <span className={brief.portfolio_fit === 'FEASIBLE' ? 'feasible' : 'infeasible'}>
                    {brief.portfolio_fit}
                  </span>
                </div>
                <div className="detail-item">
                  <label>Capital Required</label>
                  <span>${brief.capital_required}</span>
                </div>
                <div className="detail-item">
                  <label>Risk Budget Impact</label>
                  <span>{brief.risk_budget_impact}%</span>
                </div>
                <div className="detail-item">
                  <label>CEO Approval Required</label>
                  <span>{brief.requires_ceo_approval ? 'Yes' : 'No'}</span>
                </div>
                <div className="detail-item">
                  <label>Finance Approval Required</label>
                  <span>{brief.requires_finance_approval ? 'Yes' : 'No'}</span>
                </div>
              </div>
            ) : (
              <div className="loading">Loading...</div>
            )}
          </section>

          <section className="detail-section">
            <h3>Thesis & Rationale</h3>
            {brief && (
              <>
                <div className="thesis">
                  <label>Thesis</label>
                  <p>{brief.thesis}</p>
                </div>
                <div className="rationale">
                  <label>Rationale</label>
                  <p>{brief.rationale}</p>
                </div>
              </>
            )}
          </section>
        </div>

        <div className="modal-footer">
          <button className="btn-approve">Approve</button>
          <button className="btn-reject">Reject</button>
          <button className="btn-defer">Defer</button>
          <button className="btn-close" onClick={onClose}>Close</button>
        </div>
      </div>
    </div>
  );
};

export default SignalDetailModal;

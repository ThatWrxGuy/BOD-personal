/**
 * Governance Queue Panel
 * Displays signals requiring review or approval
 */

import React, { useState, useEffect } from 'react';

const GovernanceQueuePanel = () => {
  const [pendingBriefs, setPendingBriefs] = useState([]);
  const [ceoBriefs, setCeoBriefs] = useState([]);
  const [financeBriefs, setFinanceBriefs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('pending');

  useEffect(() => {
    fetchBriefs();
    const interval = setInterval(fetchBriefs, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchBriefs = async () => {
    try {
      const [pendingRes, ceoRes, financeRes] = await Promise.all([
        fetch('/api/options-agent/briefs/pending'),
        fetch('/api/options-agent/briefs/ceo'),
        fetch('/api/options-agent/briefs/finance'),
      ]);
      
      const pendingData = await pendingRes.json();
      const ceoData = await ceoRes.json();
      const financeData = await financeRes.json();
      
      setPendingBriefs(pendingData.briefs || []);
      setCeoBriefs(ceoData.briefs || []);
      setFinanceBriefs(financeData.briefs || []);
    } catch (error) {
      console.error('Failed to fetch briefs:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (briefId) => {
    console.log('Approving:', briefId);
  };

  const handleReject = async (briefId) => {
    console.log('Rejecting:', briefId);
  };

  const handleDefer = async (briefId) => {
    console.log('Deferring:', briefId);
  };

  const getBriefs = () => {
    switch (activeTab) {
      case 'ceo': return ceoBriefs;
      case 'finance': return financeBriefs;
      default: return pendingBriefs;
    }
  };

  if (loading) {
    return <div className="panel-loading">Loading governance queue...</div>;
  }

  const briefs = getBriefs();

  return (
    <div className="governance-queue-panel">
      <h3>Governance Queue</h3>
      
      <div className="queue-tabs">
        <button 
          className={activeTab === 'pending' ? 'active' : ''}
          onClick={() => setActiveTab('pending')}
        >
          Pending ({pendingBriefs.length})
        </button>
        <button 
          className={activeTab === 'finance' ? 'active' : ''}
          onClick={() => setActiveTab('finance')}
        >
          Finance Review ({financeBriefs.length})
        </button>
        <button 
          className={activeTab === 'ceo' ? 'active' : ''}
          onClick={() => setActiveTab('ceo')}
        >
          CEO Approval ({ceoBriefs.length})
        </button>
      </div>

      <div className="queue-list">
        {briefs.length === 0 ? (
          <div className="no-items">No items in queue</div>
        ) : (
          briefs.map((brief) => (
            <div key={brief.brief_id} className="queue-item">
              <div className="item-header">
                <span className="brief-id">{brief.brief_id}</span>
                <span className="signal-id">{brief.signal_id}</span>
              </div>
              <div className="item-details">
                <span className="ticker">
                  {brief.ticker} ${brief.strike}{brief.option_type?.toUpperCase()}
                </span>
                <span className="direction">{brief.direction?.toUpperCase()}</span>
              </div>
              <div className="item-meta">
                <span className="confidence">
                  Confidence: {brief.confidence_score?.toFixed(0)}%
                </span>
                <span className="score">
                  Score: {brief.signal_score?.toFixed(0)}
                </span>
              </div>
              <div className="item-actions">
                <button 
                  className="btn-approve"
                  onClick={() => handleApprove(brief.brief_id)}
                >
                  Approve
                </button>
                <button 
                  className="btn-reject"
                  onClick={() => handleReject(brief.brief_id)}
                >
                  Reject
                </button>
                <button 
                  className="btn-defer"
                  onClick={() => handleDefer(brief.brief_id)}
                >
                  Defer
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default GovernanceQueuePanel;

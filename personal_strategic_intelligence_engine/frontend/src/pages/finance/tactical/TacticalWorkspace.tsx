/**
 * Tactical Workspace
 * Main command center for tactical finance intelligence
 */

import React, { useState, useEffect } from 'react';
import TacticalSignalsPanel from './TacticalSignalsPanel';
import MarketStructurePanel from './MarketStructurePanel';
import ExecutionTimingPanel from './ExecutionTimingPanel';
import GovernanceQueuePanel from './GovernanceQueuePanel';
import PortfolioImpactPanel from './PortfolioImpactPanel';
import SuppressionFeedPanel from './SuppressionFeedPanel';
import TacticalPerformancePanel from './TacticalPerformancePanel';
import TacticalLearningPanel from './TacticalLearningPanel';
import SignalDetailModal from './SignalDetailModal';

const TacticalWorkspace = () => {
  const [selectedSignal, setSelectedSignal] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 15000);
    
    return () => clearInterval(interval);
  }, []);

  const handleSignalSelect = (signal) => {
    setSelectedSignal(signal);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedSignal(null);
  };

  return (
    <div className="tactical-workspace">
      <div className="workspace-header">
        <div className="header-title">
          <h1>Tactical Command Center</h1>
          <span className="subtitle">SPY 0DTE Intelligence</span>
        </div>
        <div className="header-status">
          <span className="status-indicator online"></span>
          <span className="last-update">
            Last update: {lastUpdate.toLocaleTimeString()}
          </span>
        </div>
      </div>

      <div className="workspace-grid">
        <div className="grid-main">
          <TacticalSignalsPanel onSignalSelect={handleSignalSelect} />
        </div>
        
        <div className="grid-structure">
          <MarketStructurePanel />
        </div>
        
        <div className="grid-timing">
          <ExecutionTimingPanel />
        </div>
        
        <div className="grid-governance">
          <GovernanceQueuePanel />
        </div>
        
        <div className="grid-portfolio">
          <PortfolioImpactPanel />
        </div>
        
        <div className="grid-suppressions">
          <SuppressionFeedPanel />
        </div>
        
        <div className="grid-performance">
          <TacticalPerformancePanel />
        </div>
        
        <div className="grid-learning">
          <TacticalLearningPanel />
        </div>
      </div>

      <SignalDetailModal 
        signal={selectedSignal}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
};

export default TacticalWorkspace;

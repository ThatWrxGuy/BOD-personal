/**
 * FinanceCommandCenter - Primary financial command interface
 * 
 * Orchestrates all finance panels and integrates with the finance backend APIs.
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  DollarSign, 
  TrendingUp, 
  AlertTriangle, 
  Lightbulb, 
  Play, 
  Briefcase, 
  History,
  RefreshCw,
  Loader
} from 'lucide-react';

import {
  FinanceOverviewPanel,
  FinanceTrendPanel,
  FinanceSignalsPanel,
  FinanceRecommendationsPanel,
  FinanceSimulationPanel,
  FinanceBoardBriefPanel,
  FinanceHistoryPanel,
} from './panels';

const API_BASE = '/api/finance';

const FinanceCommandCenter = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Financial State Data
  const [financialState, setFinancialState] = useState(null);
  const [snapshots, setSnapshots] = useState([]);
  const [signals, setSignals] = useState({ risks: [], opportunities: [] });
  const [recommendations, setRecommendations] = useState([]);
  const [boardBrief, setBoardBrief] = useState(null);
  const [auditLog, setAuditLog] = useState([]);
  
  // Simulation
  const [simulationResults, setSimulationResults] = useState(null);
  const [simulationLoading, setSimulationLoading] = useState(false);

  // Fetch all financial data
  const fetchFinancialData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch financial state
      const stateRes = await fetch(`${API_BASE}/state?profile_id=1`);
      if (stateRes.ok) {
        const stateData = await stateRes.json();
        setFinancialState(stateData);
      }

      // Fetch snapshots
      const snapshotsRes = await fetch(`${API_BASE}/snapshots?profile_id=1`);
      if (snapshotsRes.ok) {
        const snapshotsData = await snapshotsRes.json();
        setSnapshots(snapshotsData.snapshots || []);
      }

      // Fetch signals
      const signalsRes = await fetch(`${API_BASE}/intelligence/signals?profile_id=1`);
      if (signalsRes.ok) {
        const signalsData = await signalsRes.json();
        setSignals({
          risks: signalsData.risks || [],
          opportunities: signalsData.opportunities || [],
        });
      }

      // Fetch recommendations
      const recsRes = await fetch(`${API_BASE}/intelligence/recommendations?profile_id=1`);
      if (recsRes.ok) {
        const recsData = await recsRes.json();
        setRecommendations(recsData.recommendations || []);
      }

      // Fetch board brief
      const briefRes = await fetch(`${API_BASE}/governance/board-brief?profile_id=1`);
      if (briefRes.ok) {
        const briefData = await briefRes.json();
        setBoardBrief(briefData);
      }

      // Fetch audit log
      const auditRes = await fetch(`${API_BASE}/governance/audit-log?profile_id=1`);
      if (auditRes.ok) {
        const auditData = await auditRes.json();
        setAuditLog(auditData.events || []);
      }

    } catch (err) {
      console.error('Error fetching financial data:', err);
      setError('Failed to load financial data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchFinancialData();
  }, [fetchFinancialData]);

  // Handle simulation run
  const handleRunSimulation = async (params) => {
    setSimulationLoading(true);
    try {
      const res = await fetch(`${API_BASE}/simulation/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile_id: 1, ...params }),
      });
      
      if (res.ok) {
        const result = await res.json();
        setSimulationResults(result);
      }
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setSimulationLoading(false);
    }
  };

  // Handle recommendation actions
  const handleViewDetails = (recommendation) => {
    console.log('View details:', recommendation);
    // Could open a modal or navigate to details
  };

  const handleRunSimulationFromRec = (recommendation) => {
    console.log('Run simulation for:', recommendation);
    // Pre-populate simulation panel
  };

  const handleSubmitDecision = async (recommendation) => {
    try {
      const res = await fetch(`${API_BASE}/governance/decisions/submit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          profile_id: 1, 
          recommendation_id: recommendation.recommendation_id,
          title: recommendation.title,
        }),
      });
      
      if (res.ok) {
        alert('Decision submitted for approval');
        fetchFinancialData(); // Refresh
      }
    } catch (err) {
      console.error('Submit decision error:', err);
    }
  };

  // Handle compare scenarios
  const handleCompareScenarios = async () => {
    console.log('Compare scenarios');
    // Implement scenario comparison
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-600 rounded-lg">
                <DollarSign className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Finance Command Center</h1>
                <p className="text-sm text-gray-500">Strategic Financial Operations</p>
              </div>
            </div>
            <button
              onClick={fetchFinancialData}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Row 1: Financial Vitals */}
        <section>
          <FinanceOverviewPanel 
            financialState={financialState} 
            loading={loading} 
          />
        </section>

        {/* Row 2: Trend Visualization */}
        <section>
          <FinanceTrendPanel 
            snapshots={snapshots} 
            loading={loading} 
          />
        </section>

        {/* Row 3: Signals */}
        <section>
          <FinanceSignalsPanel 
            risks={signals.risks}
            opportunities={signals.opportunities}
            loading={loading}
          />
        </section>

        {/* Row 4: Recommendations */}
        <section>
          <FinanceRecommendationsPanel 
            recommendations={recommendations}
            loading={loading}
            onViewDetails={handleViewDetails}
            onRunSimulation={handleRunSimulationFromRec}
            onSubmitDecision={handleSubmitDecision}
          />
        </section>

        {/* Row 5: Simulation Workspace */}
        <section>
          <FinanceSimulationPanel
            onRunSimulation={handleRunSimulation}
            onCompareScenarios={handleCompareScenarios}
            loading={simulationLoading}
            results={simulationResults}
          />
        </section>

        {/* Row 6: Board Brief */}
        <section>
          <FinanceBoardBriefPanel 
            boardBrief={boardBrief} 
            loading={loading} 
          />
        </section>

        {/* Row 7: Financial History */}
        <section>
          <FinanceHistoryPanel 
            snapshots={snapshots}
            auditLog={auditLog}
            loading={loading}
          />
        </section>

      </div>
    </div>
  );
};

export default FinanceCommandCenter;

/**
 * FinanceSignalsPanel - displays risks and opportunities
 */

import React from 'react';
import { RiskIndicator, OpportunityIndicator } from '../components';

const FinanceSignalsPanel = ({ signals, risks, opportunities, loading }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Signals</h2>
        <div className="animate-pulse">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
            <div className="space-y-3">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Use signals prop or derive from risks/opportunities
  const displayRisks = risks || signals?.risks || [];
  const displayOpportunities = opportunities || signals?.opportunities || [];

  const hasRisks = displayRisks.length > 0;
  const hasOpportunities = displayOpportunities.length > 0;

  if (!hasRisks && !hasOpportunities) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Signals</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">No financial signals detected.</p>
          <p className="text-sm text-gray-400 mt-1">Your financial state appears stable.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Signals</h2>
      <div className="grid grid-cols-2 gap-6">
        {/* Left Column: Risks */}
        <div>
          <h3 className="text-sm font-medium text-red-600 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 bg-red-500 rounded-full"></span>
            Top Risks ({displayRisks.length})
          </h3>
          {hasRisks ? (
            <div className="space-y-2">
              {displayRisks.slice(0, 5).map((risk, index) => (
                <RiskIndicator key={risk.risk_id || index} risk={risk} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">No risks detected</p>
          )}
        </div>

        {/* Right Column: Opportunities */}
        <div>
          <h3 className="text-sm font-medium text-green-600 mb-3 flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full"></span>
            Opportunities ({displayOpportunities.length})
          </h3>
          {hasOpportunities ? (
            <div className="space-y-2">
              {displayOpportunities.slice(0, 5).map((opp, index) => (
                <OpportunityIndicator key={opp.opportunity_id || index} opportunity={opp} />
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-400">No opportunities detected</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default FinanceSignalsPanel;

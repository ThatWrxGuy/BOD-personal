/**
 * FinanceOverviewPanel - displays financial vital signs
 */

import React from 'react';
import { MetricCard } from '../components';

const FinanceOverviewPanel = ({ financialState, loading }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Overview</h2>
        <div className="animate-pulse">
          <div className="grid grid-cols-5 gap-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!financialState) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Overview</h2>
        <p className="text-gray-500">No financial data available. Please configure your financial profile.</p>
      </div>
    );
  }

  const getHealthStatusColor = (score) => {
    if (score >= 70) return 'healthy';
    if (score >= 40) return 'watch';
    return 'risk';
  };

  const getNetWorthStatusColor = (nw) => {
    if (nw > 0) return 'healthy';
    if (nw > -50000) return 'watch';
    return 'risk';
  };

  const getCashFlowStatusColor = (cf) => {
    if (cf > 500) return 'healthy';
    if (cf > 0) return 'watch';
    return 'risk';
  };

  const getDebtStatusColor = (dti) => {
    if (dti < 0.15) return 'healthy';
    if (dti < 0.30) return 'watch';
    return 'risk';
  };

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Overview</h2>
      <div className="grid grid-cols-5 gap-4">
        <MetricCard
          label="Net Worth"
          value={financialState.net_worth || 0}
          trendDelta={financialState.net_worth_delta}
          trendDirection={financialState.net_worth > 0 ? 'up' : 'down'}
          statusColor={getNetWorthStatusColor(financialState.net_worth)}
          format="currency"
        />
        <MetricCard
          label="Free Cash Flow"
          value={financialState.free_cash_flow || 0}
          trendDelta={financialState.cash_flow_delta}
          trendDirection={financialState.free_cash_flow > 0 ? 'up' : 'down'}
          statusColor={getCashFlowStatusColor(financialState.free_cash_flow)}
          format="currency"
        />
        <MetricCard
          label="Liquid Reserves"
          value={financialState.liquid_assets || 0}
          trendDelta={financialState.liquid_assets_delta}
          trendDirection="neutral"
          statusColor="neutral"
          format="currency"
        />
        <MetricCard
          label="Total Debt"
          value={financialState.total_debt || 0}
          trendDelta={financialState.debt_delta}
          trendDirection={financialState.total_debt > 0 ? 'down' : 'up'}
          statusColor={getDebtStatusColor(financialState.debt_to_income_ratio)}
          format="currency"
        />
        <MetricCard
          label="Health Score"
          value={financialState.financial_health_score || 0}
          trendDirection={financialState.financial_health_score > 50 ? 'up' : 'down'}
          statusColor={getHealthStatusColor(financialState.financial_health_score)}
          format="number"
        />
      </div>
    </div>
  );
};

export default FinanceOverviewPanel;

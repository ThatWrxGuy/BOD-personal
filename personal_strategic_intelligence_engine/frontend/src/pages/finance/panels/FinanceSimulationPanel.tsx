/**
 * FinanceSimulationPanel - interactive scenario modeling workspace
 */

import React, { useState } from 'react';
import { Play, GitCompare, Loader } from 'lucide-react';

const FinanceSimulationPanel = ({ onRunSimulation, onCompareScenarios, loading, results }) => {
  const [scenarioType, setScenarioType] = useState('debt_payoff');
  const [parameters, setParameters] = useState({
    extra_payment_amount: 500,
    income_reduction_percent: 25,
    expense_increase_amount: 500,
    income_interruption_months: 3,
    simulation_horizon: 12,
  });

  const scenarioTypes = [
    { value: 'debt_payoff', label: 'Debt Payoff' },
    { value: 'income_shock', label: 'Income Shock' },
    { value: 'expense_shock', label: 'Expense Shock' },
    { value: 'liquidity_stress', label: 'Liquidity Stress' },
    { value: 'allocation_projection', label: 'Investment Allocation' },
  ];

  const handleRunSimulation = () => {
    if (onRunSimulation) {
      onRunSimulation({ scenario_type: scenarioType, ...parameters });
    }
  };

  const handleCompareScenarios = () => {
    if (onCompareScenarios) {
      onCompareScenarios();
    }
  };

  const formatCurrency = (v) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(v);

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Simulation Workspace</h2>

      {/* Scenario Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Scenario Type</label>
        <select
          value={scenarioType}
          onChange={(e) => setScenarioType(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {scenarioTypes.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </div>

      {/* Parameter Inputs */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {scenarioType === 'debt_payoff' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Extra Monthly Payment
            </label>
            <input
              type="number"
              value={parameters.extra_payment_amount}
              onChange={(e) => setParameters({ ...parameters, extra_payment_amount: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              min="0"
              step="50"
            />
          </div>
        )}

        {scenarioType === 'income_shock' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Income Reduction (%)
              </label>
              <input
                type="number"
                value={parameters.income_reduction_percent}
                onChange={(e) => setParameters({ ...parameters, income_reduction_percent: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="0"
                max="100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Duration (months)
              </label>
              <input
                type="number"
                value={parameters.income_interruption_months}
                onChange={(e) => setParameters({ ...parameters, income_interruption_months: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg"
                min="1"
                max="24"
              />
            </div>
          </>
        )}

        {scenarioType === 'expense_shock' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Expense Increase Amount
            </label>
            <input
              type="number"
              value={parameters.expense_increase_amount}
              onChange={(e) => setParameters({ ...parameters, expense_increase_amount: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              min="0"
              step="50"
            />
          </div>
        )}

        {scenarioType === 'liquidity_stress' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Income Interruption (months)
            </label>
            <input
              type="number"
              value={parameters.income_interruption_months}
              onChange={(e) => setParameters({ ...parameters, income_interruption_months: Number(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
              min="1"
              max="12"
            />
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Simulation Horizon (months)
          </label>
          <input
            type="number"
            value={parameters.simulation_horizon}
            onChange={(e) => setParameters({ ...parameters, simulation_horizon: Number(e.target.value) })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            min="1"
            max="60"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={handleRunSimulation}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? <Loader className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
          Run Simulation
        </button>
        <button
          onClick={handleCompareScenarios}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
        >
          <GitCompare className="w-4 h-4" />
          Compare Scenarios
        </button>
      </div>

      {/* Results Display */}
      {results && (
        <div className="border-t pt-4">
          <h3 className="font-medium text-gray-900 mb-3">Simulation Results</h3>
          <div className="grid grid-cols-3 gap-4">
            {results.projected_net_worth !== undefined && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Projected Net Worth</div>
                <div className="font-semibold text-lg">{formatCurrency(results.projected_net_worth)}</div>
              </div>
            )}
            {results.projected_liquidity !== undefined && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Projected Liquidity</div>
                <div className="font-semibold text-lg">{formatCurrency(results.projected_liquidity)}</div>
              </div>
            )}
            {results.projected_debt_balance !== undefined && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Projected Debt</div>
                <div className="font-semibold text-lg">{formatCurrency(results.projected_debt_balance)}</div>
              </div>
            )}
            {results.interest_paid_total !== undefined && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Total Interest</div>
                <div className="font-semibold text-lg">{formatCurrency(results.interest_paid_total)}</div>
              </div>
            )}
            {results.survival_months !== undefined && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Survival Months</div>
                <div className="font-semibold text-lg">{results.survival_months.toFixed(1)}</div>
              </div>
            )}
            {results.confidence_score !== undefined && (
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500 mb-1">Confidence</div>
                <div className="font-semibold text-lg">{(results.confidence_score * 100).toFixed(0)}%</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FinanceSimulationPanel;

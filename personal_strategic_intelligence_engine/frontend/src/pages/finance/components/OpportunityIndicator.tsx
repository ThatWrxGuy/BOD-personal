/**
 * OpportunityIndicator - displays financial opportunity signals
 */

import React from 'react';
import { TrendingUp, Lightbulb } from 'lucide-react';

const OpportunityIndicator = ({ opportunity }) => {
  const { title, description, opportunity_type, trigger_metric, trigger_value, expected_benefit } = opportunity;

  const getTypeColor = () => {
    switch (opportunity_type) {
      case 'accelerated_debt_payoff': return 'border-green-500 bg-green-50 text-green-900';
      case 'excess_cash_flow_investment': return 'border-emerald-500 bg-emerald-50 text-emerald-900';
      case 'reserve_optimization': return 'border-teal-500 bg-teal-50 text-teal-900';
      case 'allocation_rebalance': return 'border-cyan-500 bg-cyan-50 text-cyan-900';
      case 'tax_efficient_investing': return 'border-blue-500 bg-blue-50 text-blue-900';
      case 'debt_consolidation': return 'border-indigo-500 bg-indigo-50 text-indigo-900';
      case 'high_yield_savings': return 'border-violet-500 bg-violet-50 text-violet-900';
      default: return 'border-gray-500 bg-gray-50 text-gray-900';
    }
  };

  const getTypeBadge = () => {
    switch (opportunity_type) {
      case 'accelerated_debt_payoff': return 'bg-green-600 text-white';
      case 'excess_cash_flow_investment': return 'bg-emerald-600 text-white';
      case 'reserve_optimization': return 'bg-teal-600 text-white';
      case 'allocation_rebalance': return 'bg-cyan-600 text-white';
      case 'tax_efficient_investing': return 'bg-blue-600 text-white';
      case 'debt_consolidation': return 'bg-indigo-600 text-white';
      case 'high_yield_savings': return 'bg-violet-600 text-white';
      default: return 'bg-gray-600 text-white';
    }
  };

  const formatType = (type) => {
    return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <div className={`rounded-lg border-l-4 p-4 ${getTypeColor()} mb-3`}>
      <div className="flex items-start gap-3">
        <TrendingUp className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <h4 className="font-semibold">{title}</h4>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${getTypeBadge()}`}>
              {formatType(opportunity_type)}
            </span>
          </div>
          <p className="text-sm opacity-90 mb-2">{description}</p>
          <div className="text-xs opacity-75 space-y-1">
            <div>
              <span className="font-medium">Metric:</span> {trigger_metric} = {trigger_value}
            </div>
            {expected_benefit && (
              <div>
                <span className="font-medium">Benefit:</span> {expected_benefit}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OpportunityIndicator;

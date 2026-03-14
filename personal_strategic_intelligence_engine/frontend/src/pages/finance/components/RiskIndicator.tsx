/**
 * RiskIndicator - displays financial risk signals
 */

import React from 'react';
import { AlertTriangle, TrendingDown } from 'lucide-react';

const RiskIndicator = ({ risk }) => {
  const { title, description, severity, trigger_metric, trigger_value } = risk;

  const getSeverityColor = () => {
    switch (severity) {
      case 'critical': return 'border-red-500 bg-red-50 text-red-900';
      case 'high': return 'border-orange-500 bg-orange-50 text-orange-900';
      case 'medium': return 'border-yellow-500 bg-yellow-50 text-yellow-900';
      case 'low': return 'border-blue-500 bg-blue-50 text-blue-900';
      default: return 'border-gray-500 bg-gray-50 text-gray-900';
    }
  };

  const getSeverityBadge = () => {
    switch (severity) {
      case 'critical': return 'bg-red-600 text-white';
      case 'high': return 'bg-orange-500 text-white';
      case 'medium': return 'bg-yellow-500 text-white';
      case 'low': return 'bg-blue-500 text-white';
      default: return 'bg-gray-500 text-white';
    }
  };

  return (
    <div className={`rounded-lg border-l-4 p-4 ${getSeverityColor()} mb-3`}>
      <div className="flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <h4 className="font-semibold">{title}</h4>
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${getSeverityBadge()}`}>
              {severity.toUpperCase()}
            </span>
          </div>
          <p className="text-sm opacity-90 mb-2">{description}</p>
          <div className="text-xs opacity-75">
            <span className="font-medium">Metric:</span> {trigger_metric} = {trigger_value}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskIndicator;

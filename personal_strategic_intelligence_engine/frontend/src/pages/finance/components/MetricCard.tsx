/**
 * MetricCard - displays financial metrics with trend indicators
 */

import React from 'react';
import { ArrowUp, ArrowDown, Minus } from 'lucide-react';

const MetricCard = ({ 
  label, 
  value, 
  trendDelta, 
  trendDirection = 'neutral', 
  statusColor = 'neutral',
  format = 'currency'
}) => {
  const getStatusColor = () => {
    switch (statusColor) {
      case 'healthy': return 'text-green-600 bg-green-50';
      case 'watch': return 'text-yellow-600 bg-yellow-50';
      case 'risk': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getTrendIcon = () => {
    switch (trendDirection) {
      case 'up': return <ArrowUp className="w-4 h-4" />;
      case 'down': return <ArrowDown className="w-4 h-4" />;
      default: return <Minus className="w-4 h-4" />;
    }
  };

  const getTrendColor = () => {
    switch (trendDirection) {
      case 'up': return 'text-green-600';
      case 'down': return 'text-red-600';
      default: return 'text-gray-500';
    }
  };

  const formatValue = (val) => {
    if (format === 'currency') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0,
      }).format(val);
    }
    if (format === 'percent') {
      return `${(val * 100).toFixed(1)}%`;
    }
    if (format === 'number') {
      return val.toFixed(1);
    }
    return val;
  };

  return (
    <div className={`rounded-lg p-4 ${getStatusColor()} transition-all hover:shadow-md`}>
      <div className="text-sm font-medium text-gray-600 mb-1">{label}</div>
      <div className="text-2xl font-bold">{formatValue(value)}</div>
      {trendDelta !== undefined && (
        <div className={`flex items-center mt-2 text-sm ${getTrendColor()}`}>
          {getTrendIcon()}
          <span className="ml-1">{formatValue(Math.abs(trendDelta))}</span>
        </div>
      )}
    </div>
  );
};

export default MetricCard;

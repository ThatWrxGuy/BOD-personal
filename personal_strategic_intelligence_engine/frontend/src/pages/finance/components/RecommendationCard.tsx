/**
 * RecommendationCard - displays financial recommendations with priority indicators
 */

import React from 'react';
import { AlertTriangle, TrendingUp, CheckCircle, FileText } from 'lucide-react';

const RecommendationCard = ({ 
  recommendation, 
  onViewDetails, 
  onRunSimulation, 
  onSubmitDecision 
}) => {
  const { title, summary, priority, confidence_score, expected_benefit, downside_risk, action_class } = recommendation;

  const getPriorityColor = () => {
    switch (priority) {
      case 'critical': return 'border-l-red-500 bg-red-50';
      case 'high': return 'border-l-orange-500 bg-orange-50';
      case 'medium': return 'border-l-yellow-500 bg-yellow-50';
      case 'low': return 'border-l-blue-500 bg-blue-50';
      default: return 'border-l-gray-500 bg-gray-50';
    }
  };

  const getPriorityBadge = () => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getActionIcon = () => {
    switch (action_class) {
      case 'automated': return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'approval_required': return <AlertTriangle className="w-4 h-4 text-orange-600" />;
      default: return <FileText className="w-4 h-4 text-blue-600" />;
    }
  };

  return (
    <div className={`rounded-lg border border-gray-200 border-l-4 p-4 ${getPriorityColor()} mb-3`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex-1">
          <h4 className="font-semibold text-gray-900">{title}</h4>
          <p className="text-sm text-gray-600 mt-1">{summary}</p>
        </div>
        <span className={`px-2 py-1 rounded text-xs font-medium ${getPriorityBadge()}`}>
          {priority.toUpperCase()}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-3 text-sm">
        <div>
          <span className="text-gray-500">Confidence: </span>
          <span className="font-medium">{(confidence_score * 100).toFixed(0)}%</span>
        </div>
        <div className="flex items-center">
          {getActionIcon()}
          <span className="ml-1 text-gray-600">{action_class.replace('_', ' ')}</span>
        </div>
      </div>

      {expected_benefit && (
        <div className="mt-2 text-sm">
          <span className="text-green-700 font-medium">+ </span>
          <span className="text-gray-600">{expected_benefit}</span>
        </div>
      )}

      {downside_risk && (
        <div className="mt-1 text-sm">
          <span className="text-red-700 font-medium">- </span>
          <span className="text-gray-600">{downside_risk}</span>
        </div>
      )}

      <div className="flex gap-2 mt-4">
        {onViewDetails && (
          <button
            onClick={() => onViewDetails(recommendation)}
            className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded hover:bg-gray-50"
          >
            View Details
          </button>
        )}
        {onRunSimulation && (
          <button
            onClick={() => onRunSimulation(recommendation)}
            className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Run Simulation
          </button>
        )}
        {onSubmitDecision && (
          <button
            onClick={() => onSubmitDecision(recommendation)}
            className="px-3 py-1.5 text-sm bg-green-600 text-white rounded hover:bg-green-700"
          >
            Submit for Decision
          </button>
        )}
      </div>
    </div>
  );
};

export default RecommendationCard;

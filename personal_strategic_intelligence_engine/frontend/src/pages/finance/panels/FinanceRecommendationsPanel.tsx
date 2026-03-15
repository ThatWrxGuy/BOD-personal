/**
 * FinanceRecommendationsPanel - displays actionable financial recommendations
 */

import React, { useState } from 'react';
import { RecommendationCard } from '../components';

const FinanceRecommendationsPanel = ({ recommendations, loading, onViewDetails, onRunSimulation, onSubmitDecision }) => {
  const [filter, setFilter] = useState('all');

  if (loading) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h2>
        <div className="animate-pulse space-y-3">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
          ))}
        </div>
      </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h2>
        <div className="text-center py-8">
          <p className="text-gray-500">No recommendations available.</p>
          <p className="text-sm text-gray-400 mt-1">Complete your financial profile to receive personalized recommendations.</p>
        </div>
      </div>
    );
  }

  // Filter recommendations
  const filteredRecommendations = React.useMemo(() => {
    if (filter === 'all') return recommendations;
    return recommendations.filter(rec => rec.priority === filter);
  }, [recommendations, filter]);

  const filterOptions = [
    { value: 'all', label: 'All' },
    { value: 'critical', label: 'Critical' },
    { value: 'high', label: 'High' },
    { value: 'medium', label: 'Medium' },
    { value: 'low', label: 'Low' },
  ];

  const priorityCounts = {
    critical: recommendations.filter(r => r.priority === 'critical').length,
    high: recommendations.filter(r => r.priority === 'high').length,
    medium: recommendations.filter(r => r.priority === 'medium').length,
    low: recommendations.filter(r => r.priority === 'low').length,
  };

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Recommendations ({filteredRecommendations.length})
        </h2>
        <div className="flex gap-2">
          {filterOptions.map((option) => (
            <button
              key={option.value}
              onClick={() => setFilter(option.value)}
              className={`px-3 py-1 text-sm rounded ${
                filter === option.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {option.label}
              {option.value !== 'all' && priorityCounts[option.value] > 0 && (
                <span className="ml-1 text-xs opacity-75">({priorityCounts[option.value]})</span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-3">
        {filteredRecommendations.map((recommendation) => (
          <RecommendationCard
            key={recommendation.recommendation_id}
            recommendation={recommendation}
            onViewDetails={onViewDetails}
            onRunSimulation={onRunSimulation}
            onSubmitDecision={onSubmitDecision}
          />
        ))}
      </div>
    </div>
  );
};

export default FinanceRecommendationsPanel;

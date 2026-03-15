/**
 * FinanceBoardBriefPanel - displays executive-level financial intelligence report
 */

import React from 'react';
import { format } from 'date-fns';
import { 
  AlertTriangle, 
  TrendingUp, 
  CheckCircle, 
  DollarSign, 
  Target, 
  Eye,
  FileText
} from 'lucide-react';

const FinanceBoardBriefPanel = ({ boardBrief, loading }) => {
  if (loading) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Board Financial Brief</h2>
        <div className="animate-pulse">
          <div className="h-96 bg-gray-200 rounded-lg"></div>
        </div>
      </div>
    );
  }

  if (!boardBrief) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Board Financial Brief</h2>
        <div className="text-center py-8">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No board brief available.</p>
          <p className="text-sm text-gray-400 mt-1">Generate a board brief to view executive financial intelligence.</p>
        </div>
      </div>
    );
  }

  const formatCurrency = (v) => new Intl.NumberFormat('en-US', { 
    style: 'currency', 
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(v);

  const getStatusColor = (status) => {
    switch (status) {
      case 'stable': return 'bg-green-100 text-green-800';
      case 'growing': return 'bg-blue-100 text-blue-800';
      case 'at_risk': return 'bg-yellow-100 text-yellow-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRiskBadge = (risk) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'moderate': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-orange-100 text-orange-800';
      case 'critical': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      {/* Header */}
      <div className="bg-gray-900 text-white px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold">Financial Intelligence Brief</h2>
            <p className="text-sm text-gray-300">Executive Financial Summary</p>
          </div>
          <div className="text-right">
            <span className={`px-3 py-1 rounded text-sm font-medium ${getStatusColor(boardBrief.financial_status)}`}>
              {boardBrief.financial_status?.toUpperCase() || 'UNKNOWN'}
            </span>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Status Indicators */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${getRiskBadge(boardBrief.risk_level)}`}>
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-gray-500">Risk Level</div>
              <div className="font-semibold">{boardBrief.risk_level?.toUpperCase() || 'N/A'}</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-100 text-blue-800">
              <Eye className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-gray-500">Confidence</div>
              <div className="font-semibold">{boardBrief.confidence_level?.toUpperCase() || 'N/A'}</div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-100 text-purple-800">
              <Target className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs text-gray-500">Health Score</div>
              <div className="font-semibold">{boardBrief.financial_health_score || 'N/A'}</div>
            </div>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-xs text-gray-500 mb-1">Net Worth</div>
            <div className="text-xl font-bold text-gray-900">{formatCurrency(boardBrief.net_worth || 0)}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-xs text-gray-500 mb-1">Free Cash Flow</div>
            <div className="text-xl font-bold text-gray-900">{formatCurrency(boardBrief.free_cash_flow || 0)}/mo</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-xs text-gray-500 mb-1">Liquid Reserves</div>
            <div className="text-xl font-bold text-gray-900">{formatCurrency(boardBrief.liquid_reserves || 0)}</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-xs text-gray-500 mb-1">Debt Exposure</div>
            <div className="text-xl font-bold text-gray-900">{formatCurrency(boardBrief.debt_exposure || 0)}</div>
          </div>
        </div>

        {/* Top Risks */}
        {boardBrief.top_risks && boardBrief.top_risks.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-red-500" />
              Top Risks
            </h3>
            <ul className="space-y-2">
              {boardBrief.top_risks.map((risk, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                  <span className="text-red-500 mt-0.5">•</span>
                  {risk}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Top Opportunities */}
        {boardBrief.top_opportunities && boardBrief.top_opportunities.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-green-500" />
              Top Opportunities
            </h3>
            <ul className="space-y-2">
              {boardBrief.top_opportunities.map((opp, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                  <span className="text-green-500 mt-0.5">•</span>
                  {opp}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Recommended Actions */}
        {boardBrief.recommended_actions && boardBrief.recommended_actions.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-blue-500" />
              Recommended Actions
            </h3>
            <ul className="space-y-2">
              {boardBrief.recommended_actions.map((action, index) => (
                <li key={index} className="flex items-start gap-2 text-sm text-gray-600">
                  <span className="text-blue-500 mt-0.5">{index + 1}.</span>
                  {action}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Generated Timestamp */}
        {boardBrief.generated_at && (
          <div className="border-t pt-4 text-xs text-gray-400">
            Generated: {format(new Date(boardBrief.generated_at), 'MMMM dd, yyyy HH:mm')}
          </div>
        )}
      </div>
    </div>
  );
};

export default FinanceBoardBriefPanel;

import { useEffect } from 'react';
import { Brain, TrendingUp, AlertTriangle, Target, FlaskConical, RefreshCw } from 'lucide-react';
import { useAppStore } from '../services/store';

export default function Intelligence() {
  const { trends, risks, forecasts, fetchIntelligence, intelligenceLoading } = useAppStore();

  useEffect(() => {
    fetchIntelligence();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Forecast Intelligence</h1>
          <p className="text-gray-400">Predictive insights and risk analysis</p>
        </div>
        <button 
          onClick={fetchIntelligence}
          disabled={intelligenceLoading}
          className="btn btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${intelligenceLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Trends */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
          <TrendingUp className="w-5 h-5 text-success" />
          Trend Analysis
        </h2>
        {trends?.signal_trends?.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {trends.signal_trends.map((trend, idx) => (
              <div key={idx} className="p-4 bg-dark-bg rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white">{trend.category}</span>
                  <span className={`badge ${
                    trend.direction === 'up' ? 'badge-danger' :
                    trend.direction === 'down' ? 'badge-success' : 'badge-info'
                  }`}>
                    {trend.direction}
                  </span>
                </div>
                <div className="text-sm text-gray-400">
                  Strength: {trend.strength.toFixed(1)}/10
                </div>
                <div className="text-sm text-gray-500">
                  Confidence: {(trend.confidence * 100).toFixed(0)}%
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No trend data available</p>
        )}
      </div>

      {/* Risk Projections */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-warning" />
          Risk Projections
        </h2>
        {risks.length > 0 ? (
          <div className="space-y-3">
            {risks.map(risk => (
              <div key={risk.id} className="p-4 bg-dark-bg rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className={`w-5 h-5 ${
                      risk.risk_probability >= 0.7 ? 'text-danger' : 'text-warning'
                    }`} />
                    <span className="font-medium text-white">{risk.risk_category}</span>
                  </div>
                  <span className="text-lg font-bold text-warning">
                    {Math.round(risk.risk_probability * 100)}%
                  </span>
                </div>
                <p className="text-gray-400 text-sm mb-2">{risk.risk_description}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  <span>Impact: {Math.round(risk.impact_estimate * 100)}%</span>
                  <span>Horizon: {risk.time_horizon}</span>
                </div>
                {risk.mitigation_suggestions && risk.mitigation_suggestions.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-dark-border">
                    <p className="text-xs text-gray-500 mb-1">Suggested Actions:</p>
                    <ul className="text-xs text-gray-400 space-y-1">
                      {risk.mitigation_suggestions.slice(0, 2).map((s, i) => (
                        <li key={i}>• {s}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No risks projected</p>
        )}
      </div>

      {/* Forecasts */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2 mb-4">
          <Brain className="w-5 h-5 text-primary-400" />
          Forecasts
        </h2>
        {forecasts.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {forecasts.map(forecast => (
              <div key={forecast.id} className="p-4 bg-dark-bg rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-white">{forecast.forecast_type}</span>
                  <span className="badge badge-info">{forecast.prediction_horizon}</span>
                </div>
                <p className="text-2xl font-bold text-white mb-1">
                  {forecast.forecast_value?.toFixed(1) || 'N/A'}
                </p>
                <div className="text-sm text-gray-500">
                  Target: {forecast.forecast_target}
                </div>
                <div className="mt-2 text-xs text-gray-500">
                  Method: {forecast.methodology}
                </div>
                <div className="mt-2">
                  <div className="text-xs text-gray-500 mb-1">Confidence</div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill bg-success"
                      style={{ width: `${forecast.confidence * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No forecasts generated</p>
        )}
      </div>
    </div>
  );
}

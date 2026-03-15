import { useState, useEffect } from 'react';
import { Radio, Filter, Search, RefreshCw } from 'lucide-react';
import { useAppStore } from '../services/store';
import { formatDistanceToNow, format } from 'date-fns';

const categories = ['ALL', 'MARKET', 'PERSONAL_FINANCE', 'HEALTH', 'CALENDAR', 'MACRO', 'RESEARCH'];
const urgencyLevels = ['ALL', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

export default function Signals() {
  const { signals, signalsLoading, fetchSignals } = useAppStore();
  const [filter, setFilter] = useState({ category: 'ALL', urgency: 'ALL', search: '' });
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchSignals();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchSignals();
    setRefreshing(false);
  };

  const filteredSignals = signals.filter(signal => {
    if (filter.category !== 'ALL' && signal.category !== filter.category) return false;
    if (filter.urgency !== 'ALL') {
      const level = signal.urgency >= 8 ? 'CRITICAL' : signal.urgency >= 6 ? 'HIGH' : signal.urgency >= 4 ? 'MEDIUM' : 'LOW';
      if (filter.urgency !== level) return false;
    }
    if (filter.search && !signal.title.toLowerCase().includes(filter.search.toLowerCase())) return false;
    return true;
  });

  const getUrgencyBadge = (urgency) => {
    if (urgency >= 8) return 'badge-danger';
    if (urgency >= 6) return 'badge-warning';
    return 'badge-info';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Signal Monitor</h1>
          <p className="text-gray-400">Monitor all strategic signals affecting your life</p>
        </div>
        <button 
          onClick={handleRefresh}
          disabled={refreshing}
          className="btn btn-secondary flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <span className="text-gray-400">Filters:</span>
          </div>
          
          <div className="flex gap-2">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setFilter({ ...filter, category: cat })}
                className={`px-3 py-1 rounded-full text-sm transition-colors ${
                  filter.category === cat 
                    ? 'bg-primary-600 text-white' 
                    : 'bg-dark-border text-gray-400 hover:text-white'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>

          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search signals..."
              value={filter.search}
              onChange={(e) => setFilter({ ...filter, search: e.target.value })}
              className="input pl-10"
            />
          </div>
        </div>
      </div>

      {/* Signals List */}
      <div className="space-y-3">
        {signalsLoading ? (
          <div className="card flex items-center justify-center py-12">
            <RefreshCw className="w-6 h-6 text-primary-400 animate-spin" />
          </div>
        ) : filteredSignals.length === 0 ? (
          <div className="card flex flex-col items-center justify-center py-12 text-gray-500">
            <Radio className="w-12 h-12 mb-4" />
            <p>No signals found</p>
          </div>
        ) : (
          filteredSignals.map((signal) => (
            <div key={signal.id} className="card card-hover">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-white">{signal.title}</h3>
                    <span className={`badge ${getUrgencyBadge(signal.urgency)}`}>
                      Urgency: {signal.urgency}
                    </span>
                    <span className="badge badge-info">{signal.category}</span>
                  </div>
                  <p className="text-gray-400 text-sm mb-2">{signal.description}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>Source: {signal.source}</span>
                    <span>Strength: {signal.signal_strength}/10</span>
                    <span>{formatDistanceToNow(new Date(signal.timestamp), { addSuffix: true })}</span>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-white">{signal.urgency}</div>
                  <div className="text-xs text-gray-500">Urgency</div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Signal Stats */}
      <div className="grid grid-cols-4 gap-4">
        {categories.slice(1).map(cat => {
          const count = signals.filter(s => s.category === cat).length;
          return (
            <div key={cat} className="stat-card">
              <div className="stat-label">{cat}</div>
              <div className="stat-value">{count}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

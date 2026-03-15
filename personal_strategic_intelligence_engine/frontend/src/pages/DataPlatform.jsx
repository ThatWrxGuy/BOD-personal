import { useState } from 'react';
import { useAppStore } from '../services/store';
import { 
  Database, 
  Search, 
  FileText, 
  BarChart3,
  Shield,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  ExternalLink,
  Filter,
  RefreshCw
} from 'lucide-react';

export default function DataPlatform() {
  const { dataPlatform, fetchDataPlatform } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDomain, setSelectedDomain] = useState('all');

  const domains = ['all', 'finance', 'health', 'fitness', 'operations', 'strategy', 'risk'];

  // Mock data for demonstration
  const sources = [
    { id: 'finance_macro_us', name: 'US Macroeconomic Data', domain: 'finance', trust: 'HIGH', status: 'active' },
    { id: 'finance_market_quotes', name: 'Market Quote Data', domain: 'finance', trust: 'HIGH', status: 'active' },
    { id: 'health_nutrition_usda', name: 'USDA FoodData Central', domain: 'health', trust: 'HIGH', status: 'active' },
    { id: 'health_literature_pubmed', name: 'PubMed Health Literature', domain: 'health', trust: 'HIGH', status: 'active' },
    { id: 'fitness_exercise_lib', name: 'Exercise Library', domain: 'fitness', trust: 'HIGH', status: 'active' },
    { id: 'ops_sops', name: 'Standard Operating Procedures', domain: 'operations', trust: 'HIGH', status: 'active' },
    { id: 'ops_metrics', name: 'Operational Metrics', domain: 'operations', trust: 'HIGH', status: 'active' },
    { id: 'strategy_doctrine', name: 'Strategic Doctrine Library', domain: 'strategy', trust: 'HIGH', status: 'active' },
    { id: 'risk_register', name: 'Risk Register', domain: 'risk', trust: 'HIGH', status: 'active' },
  ];

  const retrievalLogs = [
    { id: 1, agent: 'Finance Agent', query: 'revenue forecast Q4', sources: 3, results: 12, latency: 145 },
    { id: 2, agent: 'Health Agent', query: 'vitamin D research', sources: 2, results: 8, latency: 89 },
    { id: 3, agent: 'Strategy Agent', query: 'market opportunity analysis', sources: 5, results: 24, latency: 234 },
    { id: 4, agent: 'Operations Agent', query: 'SOP for vendor management', sources: 1, results: 5, latency: 67 },
  ];

  const metrics = {
    totalRequests: 1247,
    avgLatency: 142,
    successRate: 94.3,
    staleDataRate: 2.1,
  };

  const filteredSources = sources.filter(source => {
    const matchesDomain = selectedDomain === 'all' || source.domain === selectedDomain;
    const matchesSearch = source.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesDomain && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Database className="text-primary-400" />
            Data Platform
          </h1>
          <p className="text-gray-400 mt-1">
            Unified data access for all agents with governance and monitoring
          </p>
        </div>
        <button 
          onClick={fetchDataPlatform}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-lg text-white"
        >
          <RefreshCw size={18} />
          Refresh
        </button>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Requests</p>
              <p className="text-2xl font-bold text-white">{metrics.totalRequests.toLocaleString()}</p>
            </div>
            <Database className="text-primary-400" size={24} />
          </div>
        </div>
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Avg Latency</p>
              <p className="text-2xl font-bold text-white">{metrics.avgLatency}ms</p>
            </div>
            <Clock className="text-blue-400" size={24} />
          </div>
        </div>
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Success Rate</p>
              <p className="text-2xl font-bold text-success">{metrics.successRate}%</p>
            </div>
            <CheckCircle className="text-success" size={24} />
          </div>
        </div>
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Stale Data Rate</p>
              <p className="text-2xl font-bold text-warning">{metrics.staleDataRate}%</p>
            </div>
            <AlertTriangle className="text-warning" size={24} />
          </div>
        </div>
      </div>

      {/* Source Registry */}
      <div className="bg-dark-card rounded-lg border border-dark-border">
        <div className="p-4 border-b border-dark-border">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Shield className="text-primary-400" />
            Source Registry
          </h2>
        </div>
        
        {/* Filters */}
        <div className="p-4 flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input
              type="text"
              placeholder="Search sources..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-dark-bg border border-dark-border rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="text-gray-400" size={18} />
            <select
              value={selectedDomain}
              onChange={(e) => setSelectedDomain(e.target.value)}
              className="bg-dark-bg border border-dark-border rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500"
            >
              {domains.map(domain => (
                <option key={domain} value={domain}>
                  {domain === 'all' ? 'All Domains' : domain.charAt(0).toUpperCase() + domain.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Sources Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-dark-bg">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Source</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Domain</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Trust Tier</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {filteredSources.map(source => (
                <tr key={source.id} className="hover:bg-dark-border/50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <FileText className="text-gray-400" size={16} />
                      <span className="text-white">{source.name}</span>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-1 bg-primary-600/20 text-primary-400 rounded text-sm">
                      {source.domain}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-sm ${
                      source.trust === 'HIGH' ? 'bg-success/20 text-success' :
                      source.trust === 'MEDIUM' ? 'bg-warning/20 text-warning' :
                      'bg-danger/20 text-danger'
                    }`}>
                      {source.trust}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="flex items-center gap-1 text-success">
                      <CheckCircle size={14} />
                      {source.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button className="text-primary-400 hover:text-primary-300">
                      <ExternalLink size={16} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Retrieval Logs */}
      <div className="bg-dark-card rounded-lg border border-dark-border">
        <div className="p-4 border-b border-dark-border">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <BarChart3 className="text-primary-400" />
            Recent Retrieval Activity
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-dark-bg">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Agent</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Query</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Sources</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Results</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase">Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {retrievalLogs.map(log => (
                <tr key={log.id} className="hover:bg-dark-border/50">
                  <td className="px-4 py-3 text-white">{log.agent}</td>
                  <td className="px-4 py-3 text-gray-300">{log.query}</td>
                  <td className="px-4 py-3 text-gray-300">{log.sources}</td>
                  <td className="px-4 py-3 text-gray-300">{log.results}</td>
                  <td className="px-4 py-3">
                    <span className={log.latency < 100 ? 'text-success' : log.latency < 200 ? 'text-warning' : 'text-danger'}>
                      {log.latency}ms
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

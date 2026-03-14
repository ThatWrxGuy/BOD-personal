import { useState } from 'react';
import { 
  Bot, 
  Brain, 
  Shield, 
  Activity, 
  Search,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Settings,
  ChevronDown,
  ChevronRight,
  Zap,
  Target,
  TrendingUp,
  DollarSign,
  Heart,
  Dumbbell,
  Briefcase
} from 'lucide-react';

export default function Agents() {
  const [expandedAgent, setExpandedAgent] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');

  // Agent profiles matching the backend AgentProfile model
  const agents = [
    {
      id: 'agent_strategy',
      name: 'Strategy Agent',
      role: 'strategy',
      status: 'active',
      domain: 'strategy',
      capabilities: ['retrieve_federated', 'analyze_trends', 'analyze_opportunities'],
      trustTier: 'MEDIUM',
      description: 'Orchestrates strategic planning and cross-domain analysis',
      lastActivity: '2 minutes ago',
    },
    {
      id: 'agent_finance',
      name: 'Finance Agent',
      role: 'finance',
      status: 'active',
      domain: 'finance',
      capabilities: ['retrieve_structured', 'retrieve_documents', 'analyze_trends'],
      trustTier: 'MEDIUM',
      description: 'Financial analysis, market data, and investment recommendations',
      lastActivity: '5 minutes ago',
    },
    {
      id: 'agent_health',
      name: 'Health Agent',
      role: 'health',
      status: 'active',
      domain: 'health',
      capabilities: ['retrieve_structured', 'retrieve_documents', 'retrieve_latest'],
      trustTier: 'MEDIUM',
      description: 'Health metrics, nutrition data, and wellness guidance',
      lastActivity: '12 minutes ago',
    },
    {
      id: 'agent_fitness',
      name: 'Fitness Agent',
      role: 'fitness',
      status: 'active',
      domain: 'fitness',
      capabilities: ['retrieve_structured', 'retrieve_documents'],
      trustTier: 'MEDIUM',
      description: 'Exercise library, workout templates, and training plans',
      lastActivity: '1 hour ago',
    },
    {
      id: 'agent_operations',
      name: 'Operations Agent',
      role: 'operations',
      status: 'active',
      domain: 'operations',
      capabilities: ['retrieve_structured', 'retrieve_documents', 'analyze_trends'],
      trustTier: 'MEDIUM',
      description: 'Operational workflows, task management, and process optimization',
      lastActivity: '8 minutes ago',
    },
    {
      id: 'agent_risk',
      name: 'Risk Agent',
      role: 'risk',
      status: 'active',
      domain: 'risk',
      capabilities: ['retrieve_federated', 'analyze_risk', 'retrieve_summarize'],
      trustTier: 'HIGH',
      description: 'Risk assessment, threat analysis, and mitigation planning',
      lastActivity: '15 minutes ago',
    },
    {
      id: 'agent_executive',
      name: 'Executive Agent',
      role: 'executive',
      status: 'active',
      domain: 'strategy',
      capabilities: ['retrieve_federated', 'approve_action', 'retrieve_summarize'],
      trustTier: 'MEDIUM',
      description: 'Executive decision support, approval authority, and strategy oversight',
      lastActivity: '3 minutes ago',
    },
  ];

  // Toolkits available in the system
  const toolkits = [
    { id: 'finance_toolkit', domain: 'finance', name: 'Finance Toolkit', capabilities: ['structured', 'documents', 'latest', 'summarize'] },
    { id: 'health_toolkit', domain: 'health', name: 'Health Toolkit', capabilities: ['structured', 'documents', 'latest'] },
    { id: 'fitness_toolkit', domain: 'fitness', name: 'Fitness Toolkit', capabilities: ['structured', 'documents', 'latest'] },
    { id: 'operations_toolkit', domain: 'operations', name: 'Operations Toolkit', capabilities: ['structured', 'documents', 'latest'] },
    { id: 'federated_toolkit', domain: 'federated', name: 'Federated Retrieval', capabilities: ['cross_domain', 'brief_builder'] },
  ];

  const getDomainIcon = (domain) => {
    const icons = {
      strategy: Brain,
      finance: DollarSign,
      health: Heart,
      fitness: Dumbbell,
      operations: Briefcase,
      risk: Shield,
    };
    const Icon = icons[domain] || Bot;
    return <Icon size={20} />;
  };

  const getCapabilityIcon = (capability) => {
    if (capability.includes('retrieve')) return <Search size={14} className="text-blue-400" />;
    if (capability.includes('analyze')) return <Activity size={14} className="text-purple-400" />;
    if (capability.includes('approve')) return <Shield size={14} className="text-green-400" />;
    return <Zap size={14} className="text-yellow-400" />;
  };

  const filteredAgents = agents.filter(agent => 
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.role.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <Bot className="text-primary-400" />
            Agent Management
          </h1>
          <p className="text-gray-400 mt-1">
            Monitor and manage agent profiles, toolkits, and capabilities
          </p>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Search agents..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full bg-dark-card border border-dark-border rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-primary-500"
        />
      </div>

      {/* Agent Profiles */}
      <div className="bg-dark-card rounded-lg border border-dark-border">
        <div className="p-4 border-b border-dark-border">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Brain className="text-primary-400" />
            Agent Profiles
          </h2>
        </div>
        <div className="divide-y divide-dark-border">
          {filteredAgents.map(agent => (
            <div key={agent.id}>
              <div 
                className="p-4 hover:bg-dark-border/50 cursor-pointer"
                onClick={() => setExpandedAgent(expandedAgent === agent.id ? null : agent.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-primary-600/20 flex items-center justify-center text-primary-400">
                      {getDomainIcon(agent.domain)}
                    </div>
                    <div>
                      <h3 className="text-white font-medium">{agent.name}</h3>
                      <p className="text-sm text-gray-400">{agent.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="flex items-center gap-2">
                        <span className={`w-2 h-2 rounded-full ${agent.status === 'active' ? 'bg-success' : 'bg-danger'}`} />
                        <span className="text-white capitalize">{agent.status}</span>
                      </div>
                      <p className="text-xs text-gray-500">{agent.lastActivity}</p>
                    </div>
                    {expandedAgent === agent.id ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                  </div>
                </div>
              </div>
              
              {/* Expanded Details */}
              {expandedAgent === agent.id && (
                <div className="px-4 pb-4 bg-dark-bg/50">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-2">
                    <div>
                      <p className="text-xs text-gray-500 uppercase">Role</p>
                      <p className="text-white">{agent.role}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase">Domain</p>
                      <p className="text-white capitalize">{agent.domain}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase">Trust Tier</p>
                      <span className={`px-2 py-0.5 rounded text-xs ${
                        agent.trustTier === 'HIGH' ? 'bg-success/20 text-success' :
                        agent.trustTier === 'MEDIUM' ? 'bg-warning/20 text-warning' :
                        'bg-danger/20 text-danger'
                      }`}>
                        {agent.trustTier}
                      </span>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500 uppercase">Toolkit</p>
                      <p className="text-white">{toolkits.find(t => t.domain === agent.domain)?.name || 'N/A'}</p>
                    </div>
                  </div>
                  <div className="mt-4">
                    <p className="text-xs text-gray-500 uppercase mb-2">Capabilities</p>
                    <div className="flex flex-wrap gap-2">
                      {agent.capabilities.map(cap => (
                        <span key={cap} className="flex items-center gap-1 px-2 py-1 bg-dark-border rounded text-sm text-gray-300">
                          {getCapabilityIcon(cap)}
                          {cap.replace(/_/g, ' ')}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Toolkit Registry */}
      <div className="bg-dark-card rounded-lg border border-dark-border">
        <div className="p-4 border-b border-dark-border">
          <h2 className="text-lg font-semibold text-white flex items-center gap-2">
            <Zap className="text-primary-400" />
            Toolkit Registry
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-4">
          {toolkits.map(toolkit => (
            <div key={toolkit.id} className="p-4 bg-dark-bg rounded-lg border border-dark-border hover:border-primary-500/50">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-white font-medium">{toolkit.name}</h3>
                <CheckCircle className="text-success" size={18} />
              </div>
              <p className="text-sm text-gray-400 mb-3">Domain: <span className="text-primary-400 capitalize">{toolkit.domain}</span></p>
              <div className="flex flex-wrap gap-1">
                {toolkit.capabilities.map(cap => (
                  <span key={cap} className="px-2 py-0.5 bg-dark-border rounded text-xs text-gray-400">
                    {cap}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Agent Activity Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Active Agents</p>
              <p className="text-2xl font-bold text-white">{agents.filter(a => a.status === 'active').length}</p>
            </div>
            <Bot className="text-primary-400" size={24} />
          </div>
        </div>
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Registered Toolkits</p>
              <p className="text-2xl font-bold text-white">{toolkits.length}</p>
            </div>
            <Zap className="text-yellow-400" size={24} />
          </div>
        </div>
        <div className="bg-dark-card rounded-lg p-4 border border-dark-border">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Capabilities</p>
              <p className="text-2xl font-bold text-white">{agents.reduce((sum, a) => sum + a.capabilities.length, 0)}</p>
            </div>
            <Activity className="text-purple-400" size={24} />
          </div>
        </div>
      </div>
    </div>
  );
}

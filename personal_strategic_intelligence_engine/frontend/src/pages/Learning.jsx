import { useEffect, useState } from 'react';
import { Brain, BookOpen, Users, TrendingUp, AlertTriangle, CheckCircle, XCircle, MinusCircle, Lightbulb } from 'lucide-react';

const outcomeColors = {
  SUCCESS: 'text-success',
  PARTIAL_SUCCESS: 'text-primary-400',
  NEUTRAL: 'text-gray-400',
  UNDERPERFORMED: 'text-warning',
  FAILED: 'text-danger',
};

const outcomeIcons = {
  SUCCESS: CheckCircle,
  PARTIAL_SUCCESS: TrendingUp,
  NEUTRAL: MinusCircle,
  UNDERPERFORMED: AlertTriangle,
  FAILED: XCircle,
};

const lessonTypeColors = {
  SUCCESS_PATTERN: 'bg-success/20 text-success',
  FAILURE_PATTERN: 'bg-danger/20 text-danger',
  RISK_PATTERN: 'bg-warning/20 text-warning',
  PROCESS_PATTERN: 'bg-info/20 text-info',
  STRATEGIC_PATTERN: 'bg-purple-500/20 text-purple-400',
};

export default function Learning() {
  const [memories, setMemories] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [patterns, setPatterns] = useState([]);
  const [scorecards, setScorecards] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('memories');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [memRes, lessonsRes, patternsRes, scoresRes] = await Promise.all([
        fetch('/api/v1/learning/memories?limit=20'),
        fetch('/api/v1/learning/lessons?limit=20'),
        fetch('/api/v1/learning/patterns?limit=20'),
        fetch('/api/v1/learning/agents/scorecards'),
      ]);
      
      const memData = await memRes.json();
      const lessonsData = await lessonsRes.json();
      const patternsData = await patternsRes.json();
      const scoresData = await scoresRes.json();
      
      setMemories(memData.memories || []);
      setLessons(lessonsData.lessons || []);
      setPatterns(patternsData.patterns || []);
      setScorecards(scoresData.scorecards || []);
    } catch (error) {
      console.error('Failed to fetch learning data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const stats = [
    { 
      label: 'Decisions in Memory', 
      value: memories.length, 
      icon: Brain,
      color: 'text-primary-400' 
    },
    { 
      label: 'Lessons Learned', 
      value: lessons.length, 
      icon: Lightbulb,
      color: 'text-warning' 
    },
    { 
      label: 'Patterns Detected', 
      value: patterns.length, 
      icon: TrendingUp,
      color: 'text-success' 
    },
    { 
      label: 'Agents Tracked', 
      value: scorecards.length, 
      icon: Users,
      color: 'text-purple-400' 
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Learning & Memory</h1>
          <p className="text-gray-400">Strategic decision history and insights</p>
        </div>
        <button onClick={fetchData} disabled={loading} className="btn btn-secondary flex items-center gap-2">
          <Brain className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        {stats.map(stat => (
          <div key={stat.label} className="stat-card">
            <div className="flex items-center justify-between mb-2">
              <stat.icon className={`w-5 h-5 ${stat.color}`} />
            </div>
            <div className="stat-value" style={{ color: stat.color }}>{stat.value}</div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border">
        {['memories', 'lessons', 'patterns', 'agents'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === tab
                ? 'border-primary-500 text-white'
                : 'border-transparent text-gray-400 hover:text-white'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'memories' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Decision Memory</h2>
          
          {memories.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No decisions in memory yet</p>
          ) : (
            <div className="space-y-3">
              {memories.map(memory => {
                const OutcomeIcon = outcomeIcons[memory.outcome_category] || MinusCircle;
                
                return (
                  <div key={memory.id} className="p-4 bg-dark-bg rounded-lg">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <span className="font-medium text-white">{memory.decision_summary || memory.decision_type}</span>
                        <span className="ml-2 badge badge-info">{memory.decision_type}</span>
                      </div>
                      {memory.outcome_category && (
                        <div className={`flex items-center gap-1 ${outcomeColors[memory.outcome_category]}`}>
                          <OutcomeIcon className="w-4 h-4" />
                          <span className="text-sm">{memory.outcome_category}</span>
                        </div>
                      )}
                    </div>
                    
                    {memory.consensus_score && (
                      <div className="text-sm text-gray-400 mb-2">
                        Consensus: {Math.round(memory.consensus_score * 100)}%
                      </div>
                    )}
                    
                    {memory.outcome_delta !== null && memory.outcome_delta !== undefined && (
                      <div className="text-sm">
                        Outcome Delta: 
                        <span className={memory.outcome_delta > 0 ? 'text-success ml-1' : memory.outcome_delta < 0 ? 'text-danger ml-1' : 'text-gray-400 ml-1'}>
                          {memory.outcome_delta > 0 ? '+' : ''}{memory.outcome_delta.toFixed(2)}
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {activeTab === 'lessons' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Lessons Learned</h2>
          
          {lessons.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No lessons extracted yet</p>
          ) : (
            <div className="space-y-3">
              {lessons.map(lesson => (
                <div key={lesson.id} className="p-4 bg-dark-bg rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Lightbulb className="w-5 h-5 text-warning" />
                      <span className="font-medium text-white">{lesson.title}</span>
                    </div>
                    <span className={`badge ${lessonTypeColors[lesson.lesson_type] || 'badge-info'}`}>
                      {lesson.lesson_type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">{lesson.description}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    {lesson.domain && <span>Domain: {lesson.domain}</span>}
                    <span>Confidence: {Math.round(lesson.confidence * 100)}%</span>
                    {lesson.is_provisional && <span className="text-warning">Provisional</span>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'patterns' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Strategic Patterns</h2>
          
          {patterns.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No patterns detected yet</p>
          ) : (
            <div className="space-y-3">
              {patterns.map(pattern => (
                <div key={pattern.id} className="p-4 bg-dark-bg rounded-lg">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <span className="font-medium text-white">{pattern.title}</span>
                      {pattern.domain && <span className="ml-2 badge badge-info">{pattern.domain}</span>}
                    </div>
                    <span className="text-sm text-gray-400">
                      {pattern.historical_frequency}x observed
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">{pattern.description}</p>
                  {pattern.average_outcome_score && (
                    <div className="text-xs text-gray-500">
                      Avg Outcome: {Math.round(pattern.average_outcome_score * 100)}%
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {activeTab === 'agents' && (
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Agent Performance</h2>
          
          {scorecards.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No agent performance data yet</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {scorecards.map(agent => (
                <div key={agent.id} className="p-4 bg-dark-bg rounded-lg">
                  <div className="flex items-center gap-2 mb-3">
                    <Users className="w-5 h-5 text-purple-400" />
                    <span className="font-medium text-white">{agent.agent_name || agent.agent_id}</span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Decisions</span>
                      <span className="text-white">{agent.total_decisions}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Accuracy</span>
                      <span className={agent.accuracy_score >= 0.7 ? 'text-success' : agent.accuracy_score >= 0.5 ? 'text-warning' : 'text-danger'}>
                        {Math.round(agent.accuracy_score * 100)}%
                      </span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Avg Confidence</span>
                      <span className="text-white">{Math.round(agent.avg_confidence * 100)}%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Weight</span>
                      <span className="text-white">{agent.current_weight.toFixed(2)}x</span>
                    </div>
                  </div>
                  
                  <div className="mt-3 pt-3 border-t border-dark-border">
                    <div className="w-full bg-dark-card rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          agent.accuracy_score >= 0.7 ? 'bg-success' : 
                          agent.accuracy_score >= 0.5 ? 'bg-warning' : 'bg-danger'
                        }`}
                        style={{ width: `${agent.accuracy_score * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from 'react';
import { MessageSquare, Users, ThumbsUp, ThumbsDown, Hand, Play, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

const statusColors = {
  INITIALIZED: 'badge-info',
  IN_PROGRESS: 'badge-warning',
  COMPLETED: 'badge-success',
  FAILED: 'badge-danger',
};

const voteIcons = {
  APPROVE: ThumbsUp,
  REJECT: ThumbsDown,
  ABSTAIN: Hand,
};

const positionColors = {
  SUPPORT: 'text-success',
  OPPOSE: 'text-danger',
  NEUTRAL: 'text-warning',
};

export default function Debates() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [debateArgs, setDebateArgs] = useState([]);
  const [votes, setVotes] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [newDebate, setNewDebate] = useState({
    title: '',
    description: '',
    topic: '',
    context: { risk_level: 0.5, expected_return: 0.1 },
  });

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/v1/debate/sessions');
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to fetch debates:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleSessionClick = async (sessionId) => {
    try {
      const [argsRes, votesRes] = await Promise.all([
        fetch(`/api/v1/debate/sessions/${sessionId}/arguments`),
        fetch(`/api/v1/debate/sessions/${sessionId}/votes`),
      ]);
      
      const argsData = await argsRes.json();
      const votesData = await votesRes.json();
      
      setSelectedSession(sessionId);
      setDebateArgs(argsData.arguments || []);
      setVotes(votesData);
    } catch (error) {
      console.error('Failed to fetch session details:', error);
    }
  };

  const handleCreate = async () => {
    try {
      await fetch('/api/v1/debate/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: newDebate.title,
          description: newDebate.description,
          topic: newDebate.topic,
          context: newDebate.context,
        }),
      });
      setShowCreate(false);
      setNewDebate({
        title: '',
        description: '',
        topic: '',
        context: { risk_level: 0.5, expected_return: 0.1 },
      });
      fetchSessions();
    } catch (error) {
      console.error('Failed to start debate:', error);
    }
  };

  const stats = [
    { label: 'Total', value: sessions.length, color: 'text-white' },
    { label: 'Active', value: sessions.filter(s => s.status === 'IN_PROGRESS').length, color: 'text-warning' },
    { label: 'Completed', value: sessions.filter(s => s.status === 'COMPLETED').length, color: 'text-success' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Strategic Debates</h1>
          <p className="text-gray-400">Multi-agent strategic deliberation</p>
        </div>
        <div className="flex gap-2">
          <button onClick={fetchSessions} disabled={loading} className="btn btn-secondary flex items-center gap-2">
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button onClick={() => setShowCreate(true)} className="btn btn-primary flex items-center gap-2">
            <Play className="w-4 h-4" />
            New Debate
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        {stats.map(stat => (
          <div key={stat.label} className="stat-card">
            <div className="stat-value" style={{ color: stat.color }}>{stat.value}</div>
            <div className="stat-label">{stat.label} Debates</div>
          </div>
        ))}
      </div>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-dark-card border border-dark-border rounded-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-white mb-4">Start New Debate</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Title</label>
                <input
                  type="text"
                  value={newDebate.title}
                  onChange={(e) => setNewDebate({ ...newDebate, title: e.target.value })}
                  className="input"
                  placeholder="Investment Strategy Review"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Topic</label>
                <input
                  type="text"
                  value={newDebate.topic}
                  onChange={(e) => setNewDebate({ ...newDebate, topic: e.target.value })}
                  className="input"
                  placeholder="portfolio_allocation"
                />
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Description</label>
                <textarea
                  value={newDebate.description}
                  onChange={(e) => setNewDebate({ ...newDebate, description: e.target.value })}
                  className="input h-20"
                  placeholder="Discuss the proposed portfolio changes"
                />
              </div>
            </div>
            
            <div className="flex gap-2 mt-6">
              <button onClick={handleCreate} className="btn btn-primary flex-1">
                Start Debate
              </button>
              <button onClick={() => setShowCreate(false)} className="btn btn-secondary flex-1">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sessions List */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Debate Sessions
          </h2>
          
          {sessions.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No debates yet</p>
          ) : (
            <div className="space-y-3">
              {sessions.map(sess => (
                <div
                  key={sess.id}
                  onClick={() => handleSessionClick(sess.id)}
                  className={`p-3 bg-dark-bg rounded-lg cursor-pointer border border-transparent hover:border-primary-500 transition-colors ${
                    selectedSession === sess.id ? 'border-primary-500' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-white">{sess.title}</span>
                    <span className={`badge ${statusColors[sess.status]}`}>{sess.status}</span>
                  </div>
                  <div className="text-xs text-gray-500">{sess.topic}</div>
                  {sess.consensus_score && (
                    <div className="mt-2 text-sm">
                      <span className="text-gray-400">Consensus: </span>
                      <span className={sess.consensus_score >= 0.75 ? 'text-success' : sess.consensus_score >= 0.5 ? 'text-warning' : 'text-danger'}>
                        {Math.round(sess.consensus_score * 100)}%
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Debate Details */}
        <div className="lg:col-span-2 space-y-4">
          {!selectedSession ? (
            <div className="card flex flex-col items-center justify-center py-12 text-gray-500">
              <Users className="w-12 h-12 mb-4" />
              <p>Select a debate to view details</p>
            </div>
          ) : (
            <>
              {/* Arguments */}
              <div className="card">
                <h2 className="text-lg font-semibold text-white mb-4">Agent Arguments</h2>
                
                <div className="space-y-4">
                  {[1, 2, 3, 4].map(round => {
                    const roundArgs = debateArgs.filter(a => a.round_number === round);
                    if (roundArgs.length === 0) return null;
                    
                    return (
                      <div key={round}>
                        <h3 className="text-sm font-medium text-gray-400 mb-2">
                          Round {round}: {round === 4 ? 'Voting' : round === 3 ? 'Risk Analysis' : round === 2 ? 'Counter-Arguments' : 'Initial Arguments'}
                        </h3>
                        <div className="space-y-2">
                          {roundArgs.map(arg => (
                            <div key={arg.id} className="p-3 bg-dark-bg rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <span className="font-medium text-white">{arg.agent_id.replace('_', ' ').title()}</span>
                                <span className={`badge ${arg.position === 'SUPPORT' ? 'badge-success' : arg.position === 'OPPOSE' ? 'badge-danger' : 'badge-warning'}`}>
                                  {arg.position}
                                </span>
                              </div>
                              <p className="text-sm text-gray-300">{arg.argument_text}</p>
                              {round === 4 && votes?.votes?.filter(v => v.agent_id === arg.agent_id).map(v => {
                                const VoteIcon = voteIcons[v.vote] || Hand;
                                return (
                                  <div key={v.vote} className="flex items-center gap-2 mt-2">
                                    <VoteIcon className={`w-4 h-4 ${v.vote === 'APPROVE' ? 'text-success' : v.vote === 'REJECT' ? 'text-danger' : 'text-gray-400'}`} />
                                    <span className="text-sm">{v.vote}</span>
                                  </div>
                                );
                              })}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Consensus */}
              {votes?.consensus_details && (
                <div className="card">
                  <h2 className="text-lg font-semibold text-white mb-4">Consensus Results</h2>
                  
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-success">
                        {votes.consensus_details.vote_counts?.APPROVE || 0}
                      </div>
                      <div className="text-sm text-gray-400">Approve</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-warning">
                        {votes.consensus_details.vote_counts?.ABSTAIN || 0}
                      </div>
                      <div className="text-sm text-gray-400">Abstain</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-danger">
                        {votes.consensus_details.vote_counts?.REJECT || 0}
                      </div>
                      <div className="text-sm text-gray-400">Reject</div>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-dark-bg rounded-lg">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Final Consensus Score</span>
                      <span className={`text-2xl font-bold ${
                        votes.consensus_details.consensus_score >= 0.75 ? 'text-success' :
                        votes.consensus_details.consensus_score >= 0.5 ? 'text-warning' : 'text-danger'
                      }`}>
                        {Math.round((votes.consensus_details.consensus_score || 0) * 100)}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

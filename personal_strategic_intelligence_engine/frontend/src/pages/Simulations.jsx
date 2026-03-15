import { useEffect, useState } from 'react';
import { FlaskConical, Play, FileText, Clock, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import { useAppStore } from '../services/store';
import { formatDistanceToNow, format } from 'date-fns';

export default function Simulations() {
  const { simulations, fetchSimulations, simulationLoading } = useAppStore();
  const [selectedSim, setSelectedSim] = useState(null);
  const [report, setReport] = useState(null);
  const [events, setEvents] = useState([]);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    fetchSimulations();
  }, []);

  const handleRunSimulation = async () => {
    setRunning(true);
    try {
      const { simulationApi } = await import('../services/api');
      await simulationApi.run({ scenario_type: 'mixed_life_pressure', simulated_days: 14 });
      await fetchSimulations();
    } catch (error) {
      console.error('Failed to run simulation:', error);
    } finally {
      setRunning(false);
    }
  };

  const handleViewReport = async (simId) => {
    try {
      const { simulationApi } = await import('../services/api');
      const reportRes = await simulationApi.report(simId);
      setReport(reportRes.data);
      const eventsRes = await simulationApi.events(simId);
      setEvents(eventsRes.data.events || []);
    } catch (error) {
      console.error('Failed to fetch report:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'COMPLETED': return <CheckCircle className="w-5 h-5 text-success" />;
      case 'FAILED': return <XCircle className="w-5 h-5 text-danger" />;
      case 'RUNNING': return <RefreshCw className="w-5 h-5 text-primary-400 animate-spin" />;
      default: return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Simulation Viewer</h1>
          <p className="text-gray-400">View system simulation results and audit reports</p>
        </div>
        <button 
          onClick={handleRunSimulation}
          disabled={running}
          className="btn btn-primary flex items-center gap-2"
        >
          <Play className={`w-4 h-4 ${running ? 'animate-pulse' : ''}`} />
          {running ? 'Running...' : 'Run Simulation'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulation List */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Simulation Runs</h2>
          
          {simulationLoading ? (
            <div className="flex justify-center py-8">
              <RefreshCw className="w-6 h-6 text-primary-400 animate-spin" />
            </div>
          ) : simulations.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FlaskConical className="w-12 h-12 mx-auto mb-4" />
              <p>No simulations run yet</p>
              <p className="text-sm mt-2">Run a simulation to see results</p>
            </div>
          ) : (
            <div className="space-y-3">
              {simulations.map(sim => (
                <div 
                  key={sim.id}
                  onClick={() => handleViewReport(sim.id)}
                  className={`p-4 bg-dark-bg rounded-lg cursor-pointer hover:border-primary-500 transition-colors border border-transparent ${
                    selectedSim === sim.id ? 'border-primary-500' : ''
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(sim.status)}
                      <span className="font-medium text-white">{sim.name}</span>
                    </div>
                    <span className={`badge ${
                      sim.status === 'COMPLETED' ? 'badge-success' :
                      sim.status === 'FAILED' ? 'badge-danger' : 'badge-warning'
                    }`}>
                      {sim.status}
                    </span>
                  </div>
                  <div className="text-sm text-gray-400">
                    {sim.scenario_type} • {sim.simulated_days} days
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    {formatDistanceToNow(new Date(sim.start_time), { addSuffix: true })}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Report Viewer */}
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Audit Report
          </h2>
          
          {!report ? (
            <div className="text-center py-12 text-gray-500">
              <FileText className="w-12 h-12 mx-auto mb-4" />
              <p>Select a simulation to view its report</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Score */}
              <div className="flex items-center justify-between p-4 bg-dark-bg rounded-lg">
                <span className="text-white font-medium">Overall Readiness Score</span>
                <span className={`text-2xl font-bold ${
                  report.system_readiness_score >= 70 ? 'text-success' :
                  report.system_readiness_score >= 40 ? 'text-warning' : 'text-danger'
                }`}>
                  {report.system_readiness_score}/100
                </span>
              </div>

              {/* Component Scores */}
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-2">Component Scores</h3>
                <div className="space-y-2">
                  {Object.entries(report.component_scores || {}).map(([component, score]) => (
                    <div key={component} className="flex items-center justify-between text-sm">
                      <span className="text-gray-400 capitalize">{component.replace('_', ' ')}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-24 h-2 bg-dark-border rounded-full">
                          <div 
                            className={`h-full rounded-full ${
                              score >= 70 ? 'bg-success' : score >= 40 ? 'bg-warning' : 'bg-danger'
                            }`}
                            style={{ width: `${score}%` }}
                          />
                        </div>
                        <span className="text-white w-8">{score}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Executive Summary */}
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-2">Executive Summary</h3>
                <p className="text-sm text-gray-300 bg-dark-bg p-3 rounded-lg">
                  {report.executive_summary}
                </p>
              </div>

              {/* Recommendations */}
              {report.recommendations?.length > 0 && (
                <div>
                  <h3 className="text-sm font-medium text-gray-400 mb-2">Recommendations</h3>
                  <div className="space-y-2">
                    {report.recommendations.map((rec, idx) => (
                      <div key={idx} className="p-3 bg-dark-bg rounded-lg">
                        <div className="flex items-center gap-2">
                          <span className={`badge badge-${
                            rec.priority === 1 ? 'danger' : rec.priority === 2 ? 'warning' : 'info'
                          }`}>
                            Priority {rec.priority}
                          </span>
                          <span className="text-white text-sm">{rec.component}</span>
                        </div>
                        <p className="text-sm text-gray-400 mt-1">{rec.recommendation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

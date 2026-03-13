import { create } from 'zustand';

export const useAppStore = create((set, get) => ({
  // Dashboard data
  dashboard: null,
  setDashboard: (data) => set({ dashboard: data }),
  
  // Signals
  signals: [],
  signalsLoading: false,
  signalsError: null,
  setSignals: (signals) => set({ signals }),
  setSignalsLoading: (loading) => set({ signalsLoading: loading }),
  setSignalsError: (error) => set({ signalsError: error }),
  
  // Governance
  goals: [],
  plans: [],
  triggers: [],
  governanceLoading: false,
  setGoals: (goals) => set({ goals }),
  setPlans: (plans) => set({ plans }),
  setTriggers: (triggers) => set({ triggers }),
  setGovernanceLoading: (loading) => set({ governanceLoading: loading }),
  
  // Intelligence
  trends: null,
  risks: [],
  forecasts: [],
  intelligenceLoading: false,
  setTrends: (trends) => set({ trends }),
  setRisks: (risks) => set({ risks }),
  setForecasts: (forecasts) => set({ forecasts }),
  setIntelligenceLoading: (loading) => set({ intelligenceLoading: loading }),
  
  // Simulations
  simulations: [],
  currentSimulation: null,
  simulationLoading: false,
  setSimulations: (simulations) => set({ simulations }),
  setCurrentSimulation: (sim) => set({ currentSimulation: sim }),
  setSimulationLoading: (loading) => set({ simulationLoading: loading }),
  
  // Decisions
  decisions: [],
  decisionsLoading: false,
  setDecisions: (decisions) => set({ decisions }),
  setDecisionsLoading: (loading) => set({ decisionsLoading: loading }),
  
  // System health
  systemHealth: null,
  healthLoading: false,
  setSystemHealth: (health) => set({ systemHealth: health }),
  setHealthLoading: (loading) => set({ healthLoading: loading }),
  
  // UI state
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  activeModule: 'dashboard',
  setActiveModule: (module) => set({ activeModule: module }),
  
  // Notifications
  notifications: [],
  addNotification: (notification) => set((state) => ({
    notifications: [...state.notifications, { ...notification, id: Date.now() }]
  })),
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id)
  })),
  
  // Refresh all data
  refreshAll: async () => {
    const { fetchDashboard, fetchSignals, fetchGovernance, fetchIntelligence } = get();
    await Promise.all([
      fetchDashboard(),
      fetchSignals(),
      fetchGovernance(),
      fetchIntelligence(),
    ]);
  },
  
  // Fetch functions
  fetchDashboard: async () => {
    try {
      const { governanceApi } = await import('./api');
      const response = await governanceApi.dashboard();
      set({ dashboard: response.data });
    } catch (error) {
      console.error('Failed to fetch dashboard:', error);
    }
  },
  
  fetchSignals: async () => {
    set({ signalsLoading: true });
    try {
      const { signalsApi } = await import('./api');
      const response = await signalsApi.list({ limit: 50 });
      set({ signals: response.data.signals || [], signalsError: null });
    } catch (error) {
      set({ signalsError: error.message });
    } finally {
      set({ signalsLoading: false });
    }
  },
  
  fetchGovernance: async () => {
    set({ governanceLoading: true });
    try {
      const { governanceApi } = await import('./api');
      const [goalsRes, plansRes, triggersRes] = await Promise.all([
        governanceApi.goals.list(),
        governanceApi.plans.list(),
        governanceApi.triggers.list({ resolved: false }),
      ]);
      set({
        goals: goalsRes.data || [],
        plans: plansRes.data || [],
        triggers: triggersRes.data || [],
      });
    } catch (error) {
      console.error('Failed to fetch governance:', error);
    } finally {
      set({ governanceLoading: false });
    }
  },
  
  fetchIntelligence: async () => {
    set({ intelligenceLoading: true });
    try {
      const { intelligenceApi } = await import('./api');
      const [trendsRes, risksRes, forecastsRes] = await Promise.all([
        intelligenceApi.trends({ days: 30 }),
        intelligenceApi.risks.list({ min_probability: 0.5 }),
        intelligenceApi.forecasts.list(),
      ]);
      set({
        trends: trendsRes.data,
        risks: risksRes.data || [],
        forecasts: forecastsRes.data || [],
      });
    } catch (error) {
      console.error('Failed to fetch intelligence:', error);
    } finally {
      set({ intelligenceLoading: false });
    }
  },
  
  fetchSimulations: async () => {
    set({ simulationLoading: true });
    try {
      const { simulationApi } = await import('./api');
      const response = await simulationApi.list();
      set({ simulations: response.data.runs || [] });
    } catch (error) {
      console.error('Failed to fetch simulations:', error);
    } finally {
      set({ simulationLoading: false });
    }
  },
  
  fetchDecisions: async () => {
    set({ decisionsLoading: true });
    try {
      const { decisionsApi } = await import('./api');
      const response = await decisionsApi.list({ limit: 20 });
      set({ decisions: response.data.decisions || [] });
    } catch (error) {
      console.error('Failed to fetch decisions:', error);
    } finally {
      set({ decisionsLoading: false });
    }
  },
  
  fetchHealth: async () => {
    set({ healthLoading: true });
    try {
      const { healthApi } = await import('./api');
      const response = await healthApi.check();
      set({ systemHealth: response.data });
    } catch (error) {
      console.error('Failed to fetch health:', error);
    } finally {
      set({ healthLoading: false });
    }
  },
}));

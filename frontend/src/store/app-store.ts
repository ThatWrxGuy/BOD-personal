import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type TimeHorizon = 'today' | 'week' | 'month' | 'quarter';
export type SystemStatus = 'healthy' | 'degraded' | 'critical';
export type StrategicPosture = 'offensive' | 'defensive' | 'neutral';

interface User {
  id: string;
  email: string;
  username: string;
  status: string;
}

interface AppState {
  // Auth
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  
  // UI State
  sidebarOpen: boolean;
  currentHorizon: TimeHorizon;
  theme: 'light' | 'dark' | 'system';
  
  // System State
  systemStatus: SystemStatus;
  strategicPosture: StrategicPosture;
  
  // Actions
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
  
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  setCurrentHorizon: (horizon: TimeHorizon) => void;
  setTheme: (theme: 'light' | 'dark' | 'system') => void;
  
  setSystemStatus: (status: SystemStatus) => void;
  setStrategicPosture: (posture: StrategicPosture) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      token: null,
      isAuthenticated: false,
      
      sidebarOpen: true,
      currentHorizon: 'week',
      theme: 'system',
      
      systemStatus: 'healthy',
      strategicPosture: 'neutral',
      
      // Actions
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setToken: (token) => set({ token }),
      
      logout: () => set({
        user: null,
        token: null,
        isAuthenticated: false,
      }),
      
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),
      setCurrentHorizon: (horizon) => set({ currentHorizon: horizon }),
      setTheme: (theme) => set({ theme }),
      
      setSystemStatus: (status) => set({ systemStatus: status }),
      setStrategicPosture: (posture) => set({ strategicPosture: posture }),
    }),
    {
      name: 'busy-bee-storage',
      partialize: (state) => ({
        theme: state.theme,
        currentHorizon: state.currentHorizon,
        sidebarOpen: state.sidebarOpen,
      }),
    }
  )
);

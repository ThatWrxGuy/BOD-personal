import { Outlet, NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Radio, 
  Shield, 
  Target, 
  Brain, 
  FlaskConical, 
  CheckSquare, 
  Activity,
  Menu,
  X,
  Bell,
  Settings
} from 'lucide-react';
import { useState } from 'react';
import { useAppStore } from '../services/store';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/signals', label: 'Signals', icon: Radio },
  { path: '/governance', label: 'Governance', icon: Shield },
  { path: '/goals', label: 'Goals & Plans', icon: Target },
  { path: '/intelligence', label: 'Intelligence', icon: Brain },
  { path: '/simulations', label: 'Simulations', icon: FlaskConical },
  { path: '/decisions', label: 'Decisions', icon: CheckSquare },
  { path: '/system', label: 'System Health', icon: Activity },
];

export default function Layout() {
  const { sidebarOpen, toggleSidebar, notifications, removeNotification } = useAppStore();
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <div className="flex h-screen bg-dark-bg">
      {/* Sidebar */}
      <aside 
        className={`${sidebarOpen ? 'w-64' : 'w-16'} 
          bg-dark-card border-r border-dark-border 
          transition-all duration-300 flex flex-col
          fixed md:relative z-20 h-full`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-dark-border">
          {sidebarOpen && (
            <span className="font-bold text-lg text-white">PSIE</span>
          )}
          <button 
            onClick={toggleSidebar}
            className="p-2 hover:bg-dark-border rounded-lg text-gray-400 hover:text-white"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive 
                    ? 'bg-primary-600/20 text-primary-400' 
                    : 'text-gray-400 hover:bg-dark-border hover:text-white'
                }`
              }
            >
              <item.icon size={20} />
              {sidebarOpen && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Settings */}
        <div className="p-2 border-t border-dark-border">
          <button className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-gray-400 hover:bg-dark-border hover:text-white">
            <Settings size={20} />
            {sidebarOpen && <span>Settings</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-16 bg-dark-card border-b border-dark-border flex items-center justify-between px-6">
          <h1 className="text-xl font-semibold text-white">
            Personal Strategic Command Center
          </h1>
          
          <div className="flex items-center gap-4">
            {/* Notifications */}
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 hover:bg-dark-border rounded-lg text-gray-400 hover:text-white relative"
              >
                <Bell size={20} />
                {notifications.length > 0 && (
                  <span className="absolute top-1 right-1 w-2 h-2 bg-danger rounded-full" />
                )}
              </button>
              
              {showNotifications && notifications.length > 0 && (
                <div className="absolute right-0 top-full mt-2 w-80 bg-dark-card border border-dark-border rounded-lg shadow-xl z-50">
                  <div className="p-3 border-b border-dark-border">
                    <h3 className="font-semibold text-white">Notifications</h3>
                  </div>
                  <div className="max-h-64 overflow-y-auto">
                    {notifications.map((notification) => (
                      <div 
                        key={notification.id}
                        className="p-3 border-b border-dark-border last:border-0 hover:bg-dark-border"
                      >
                        <p className="text-sm text-white">{notification.message}</p>
                        <button
                          onClick={() => removeNotification(notification.id)}
                          className="text-xs text-gray-500 hover:text-white mt-1"
                        >
                          Dismiss
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            {/* Status indicator */}
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 bg-success rounded-full animate-pulse" />
              <span className="text-sm text-gray-400">System Online</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

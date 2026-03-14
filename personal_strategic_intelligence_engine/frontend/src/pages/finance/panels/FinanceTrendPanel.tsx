/**
 * FinanceTrendPanel - displays financial metric trends
 */

import React, { useState } from 'react';
import { 
  NetWorthTrendChart, 
  CashFlowTrendChart, 
  DebtTrendChart, 
  LiquidityTrendChart 
} from '../components/charts';

const FinanceTrendPanel = ({ snapshots, loading }) => {
  const [timeRange, setTimeRange] = useState('12m');

  const timeRanges = [
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '12m', label: '12 Months' },
    { value: 'all', label: 'All Time' },
  ];

  if (loading) {
    return (
      <div className="bg-white rounded-lg p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Financial Trends</h2>
        <div className="animate-pulse">
          <div className="grid grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-64 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Transform snapshots to chart data format
  const chartData = React.useMemo(() => {
    if (!snapshots || snapshots.length === 0) {
      // Generate demo data if no snapshots
      const demoData = [];
      const now = new Date();
      for (let i = 11; i >= 0; i--) {
        const date = new Date(now);
        date.setMonth(date.getMonth() - i);
        demoData.push({
          date: date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
          netWorth: 50000 + Math.random() * 20000 - 10000,
          cashFlow: 1500 + Math.random() * 1000,
          debt: 100000 + Math.random() * 10000,
          liquidity: 30000 + Math.random() * 10000,
        });
      }
      return demoData;
    }

    return snapshots.map(s => ({
      date: new Date(s.timestamp).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
      netWorth: s.net_worth,
      cashFlow: s.free_cash_flow,
      debt: s.total_liabilities,
      liquidity: s.available_liquidity,
    }));
  }, [snapshots]);

  return (
    <div className="bg-white rounded-lg p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Financial Trends</h2>
        <div className="flex gap-2">
          {timeRanges.map((range) => (
            <button
              key={range.value}
              onClick={() => setTimeRange(range.value)}
              className={`px-3 py-1 text-sm rounded ${
                timeRange === range.value
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <NetWorthTrendChart data={chartData} timeRange={timeRange} />
        <CashFlowTrendChart data={chartData} timeRange={timeRange} />
        <DebtTrendChart data={chartData} timeRange={timeRange} />
        <LiquidityTrendChart data={chartData} timeRange={timeRange} />
      </div>
    </div>
  );
};

export default FinanceTrendPanel;

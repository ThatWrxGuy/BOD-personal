/**
 * NetWorthTrendChart - displays net worth over time
 */

import React from 'react';
import FinancialLineChart from './FinancialLineChart';

const NetWorthTrendChart = ({ data, timeRange = '12m' }) => {
  const formatCurrency = (v) => {
    if (v >= 1000) return `$${(v / 1000).toFixed(0)}k`;
    return `$${v}`;
  };

  return (
    <FinancialLineChart
      data={data}
      dataKey="netWorth"
      title="Net Worth"
      color="#3b82f6"
      formatValue={formatCurrency}
    />
  );
};

export default NetWorthTrendChart;

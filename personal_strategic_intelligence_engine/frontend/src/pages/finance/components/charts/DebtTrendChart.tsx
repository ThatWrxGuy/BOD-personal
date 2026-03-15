/**
 * DebtTrendChart - displays debt balance over time
 */

import React from 'react';
import FinancialLineChart from './FinancialLineChart';

const DebtTrendChart = ({ data, timeRange = '12m' }) => {
  const formatCurrency = (v) => {
    if (v >= 1000) return `$${(v / 1000).toFixed(0)}k`;
    return `$${v}`;
  };

  return (
    <FinancialLineChart
      data={data}
      dataKey="debt"
      title="Total Debt"
      color="#ef4444"
      formatValue={formatCurrency}
    />
  );
};

export default DebtTrendChart;

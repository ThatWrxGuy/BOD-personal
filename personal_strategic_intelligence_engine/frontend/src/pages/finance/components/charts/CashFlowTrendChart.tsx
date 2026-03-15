/**
 * CashFlowTrendChart - displays cash flow over time
 */

import React from 'react';
import FinancialLineChart from './FinancialLineChart';

const CashFlowTrendChart = ({ data, timeRange = '12m' }) => {
  const formatCurrency = (v) => `$${v}`;

  return (
    <FinancialLineChart
      data={data}
      dataKey="cashFlow"
      title="Monthly Cash Flow"
      color="#10b981"
      formatValue={formatCurrency}
    />
  );
};

export default CashFlowTrendChart;

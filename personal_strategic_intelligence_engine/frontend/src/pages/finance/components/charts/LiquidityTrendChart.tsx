/**
 * LiquidityTrendChart - displays liquid assets over time
 */

import React from 'react';
import FinancialLineChart from './FinancialLineChart';

const LiquidityTrendChart = ({ data, timeRange = '12m' }) => {
  const formatCurrency = (v) => {
    if (v >= 1000) return `$${(v / 1000).toFixed(0)}k`;
    return `$${v}`;
  };

  return (
    <FinancialLineChart
      data={data}
      dataKey="liquidity"
      title="Liquid Assets"
      color="#8b5cf6"
      formatValue={formatCurrency}
    />
  );
};

export default LiquidityTrendChart;

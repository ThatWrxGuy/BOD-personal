/**
 * Portfolio Impact Panel
 * Displays portfolio risk and allocation information
 */

import React, { useState, useEffect } from 'react';

const PortfolioImpactPanel = () => {
  const [portfolio, setPortfolio] = useState({
    available_cash: 0,
    daily_loss_limit: 0,
    weekly_loss_limit: 0,
    speculative_budget: 0,
    current_exposure: 0,
  });
  const [allocation, setAllocation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 15000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const response = await fetch('/api/options-agent/allocation/policy');
      const data = await response.json();
      setAllocation(data.policy);
      
      setPortfolio({
        available_cash: 2000,
        daily_loss_limit: 500,
        weekly_loss_limit: 1500,
        speculative_budget: 300,
        current_exposure: 120,
      });
    } catch (error) {
      console.error('Failed to fetch portfolio:', error);
    } finally {
      setLoading(false);
    }
  };

  const budgetUsed = (portfolio.current_exposure / portfolio.speculative_budget * 100) || 0;
  const budgetRemaining = portfolio.speculative_budget - portfolio.current_exposure;

  if (loading) {
    return <div className="panel-loading">Loading portfolio...</div>;
  }

  return (
    <div className="portfolio-impact-panel">
      <h3>Portfolio Impact</h3>
      
      <div className="portfolio-metrics">
        <div className="metric">
          <label>Available Cash</label>
          <span className="value">${portfolio.available_cash.toLocaleString()}</span>
        </div>

        <div className="metric">
          <label>Risk Budget</label>
          <span className="value">${portfolio.speculative_budget}</span>
        </div>

        <div className="metric">
          <label>Current Exposure</label>
          <span className="value">${portfolio.current_exposure}</span>
        </div>

        <div className="metric">
          <label>Budget Remaining</label>
          <span className="value">${budgetRemaining}</span>
        </div>
      </div>

      <div className="budget-utilization">
        <label>Budget Utilization</label>
        <div className="utilization-bar">
          <div 
            className="utilization-fill"
            style={{ 
              width: `${Math.min(budgetUsed, 100)}%`,
              backgroundColor: budgetUsed > 80 ? '#f44336' : budgetUsed > 50 ? '#ffa500' : '#4caf50'
            }}
          />
        </div>
        <span className="utilization-value">{budgetUsed.toFixed(0)}%</span>
      </div>

      {allocation && (
        <div className="allocation-limits">
          <label>Allocation Limits</label>
          <div className="limit-item">
            <span>Paper Trade Max</span>
            <span>${allocation.max_paper_trade_notional?.toLocaleString()}</span>
          </div>
          <div className="limit-item">
            <span>Board Review Max</span>
            <span>${allocation.max_board_review_notional?.toLocaleString()}</span>
          </div>
          <div className="limit-item">
            <span>Qualified Max</span>
            <span>${allocation.max_qualified_notional?.toLocaleString()}</span>
          </div>
        </div>
      )}

      <div className="feasibility-status">
        <label>Capital Feasibility</label>
        <span className="status-badge feasible">
          {budgetRemaining > 100 ? 'FEASIBLE' : 'LIMITED'}
        </span>
      </div>
    </div>
  );
};

export default PortfolioImpactPanel;

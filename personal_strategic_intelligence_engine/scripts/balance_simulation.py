#!/usr/bin/env python
"""Simulation script with balance tracking."""
import random
import hashlib
from datetime import date, timedelta
from typing import Dict, List


class SeedManager:
    def __init__(self, seed: str):
        self.original_seed = seed.upper().strip().replace(" ", "-")
        self._random_generator = self._create_deterministic_generator(self.original_seed)
    
    def _create_deterministic_generator(self, seed: str) -> random.Random:
        seed_hash = hashlib.sha256(seed.encode()).hexdigest()
        seed_int = int(seed_hash[:16], 16) % (2**31)
        return random.Random(seed_int)
    
    @property
    def random(self) -> random.Random:
        return self._random_generator
    
    def get_seed_hash(self) -> str:
        return hashlib.sha256(self.original_seed.encode()).hexdigest()


class FinancialState:
    def __init__(self):
        self.monthly_income = 0
        self.fixed_expenses = 0
        self.debt_balances = 0
        self.investment_balances = 0
        self.liquidity = 0
        self.cash_flow_pressure = 0


class MockDataGenerator:
    def __init__(self, seed_manager: SeedManager):
        self.seed = seed_manager
        self._rng = seed_manager.random
    
    def generate_financial_state(self) -> FinancialState:
        rng = self._rng
        fin = FinancialState()
        fin.monthly_income = rng.randint(3000, 15000) + rng.random() * 1000
        fin.fixed_expenses = rng.randint(2000, 6000) + rng.random() * 500
        fin.debt_balances = rng.randint(0, 20000)
        fin.investment_balances = rng.randint(0, 100000)
        fin.liquidity = rng.randint(1000, 20000)
        fin.cash_flow_pressure = (fin.fixed_expenses / fin.monthly_income) if fin.monthly_income > 0 else 0.5
        return fin


def run_simulation(seed: str, days: int):
    seed_manager = SeedManager(seed)
    mock = MockDataGenerator(seed_manager)
    
    # Generate initial financial state
    initial_fin = mock.generate_financial_state()
    
    print("=" * 70)
    print("FINANCIAL BALANCE TRACKING")
    print("=" * 70)
    print(f"\nSeed: {seed}")
    print(f"Duration: {days} days")
    print(f"\n{'='*70}")
    print("STARTING FINANCIAL STATE")
    print("=" * 70)
    print(f"Monthly Income:     ${initial_fin.monthly_income:,.0f}")
    print(f"Fixed Expenses:     ${initial_fin.fixed_expenses:,.0f}")
    print(f"Debt Balances:      ${initial_fin.debt_balances:,.0f}")
    print(f"Investment Balance: ${initial_fin.investment_balances:,.0f}")
    print(f"Liquidity (Cash):  ${initial_fin.liquidity:,.0f}")
    print(f"Net Monthly Cash:   ${initial_fin.monthly_income - initial_fin.fixed_expenses:,.0f}")
    
    # Calculate starting net worth
    starting_net_worth = (
        initial_fin.investment_balances + 
        initial_fin.liquidity - 
        initial_fin.debt_balances
    )
    print(f"\n>>> STARTING NET WORTH: ${starting_net_worth:,.0f} <<<")
    
    # Simulate month by month
    current_fin = initial_fin
    monthly_savings = current_fin.monthly_income - current_fin.fixed_expenses
    
    # Track monthly changes
    months = days // 30
    for month in range(1, months + 1):
        # Random events that affect finances
        event_roll = mock._rng.random()
        
        if event_roll < 0.1:  # 10% chance of unexpected expense
            expense = mock._rng.uniform(500, 3000)
            current_fin.liquidity -= expense
            print(f"\nMonth {month}: Unexpected expense ${expense:,.0f}")
        
        elif event_roll < 0.15:  # 5% chance of bonus
            bonus = mock._rng.uniform(500, 3000)
            current_fin.monthly_income += bonus
            print(f"\nMonth {month}: Bonus income +${bonus:,.0f}")
        
        elif event_roll < 0.2:  # 5% chance of debt payment
            payment = min(current_fin.liquidity * 0.3, current_fin.debt_balances * 0.1)
            if payment > 0 and current_fin.liquidity > 2000:
                current_fin.debt_balances -= payment
                current_fin.liquidity -= payment
                print(f"\nMonth {month}: Debt payment -${payment:,.0f}")
        
        # Investment returns (average 6% annual = 0.5% monthly)
        investment_return = current_fin.investment_balances * 0.005
        current_fin.investment_balances += investment_return
        
        # Add savings to liquidity
        monthly_savings = current_fin.monthly_income - current_fin.fixed_expenses
        current_fin.liquidity += monthly_savings
        
        # Move excess liquidity to investments
        if current_fin.liquidity > 10000:
            investment_contribution = (current_fin.liquidity - 5000) * 0.5
            current_fin.investment_balances += investment_contribution
            current_fin.liquidity -= investment_contribution
    
    # Final calculations
    ending_net_worth = (
        current_fin.investment_balances + 
        current_fin.liquidity - 
        current_fin.debt_balances
    )
    
    print(f"\n{'='*70}")
    print("ENDING FINANCIAL STATE")
    print("=" * 70)
    print(f"Monthly Income:     ${current_fin.monthly_income:,.0f}")
    print(f"Fixed Expenses:     ${current_fin.fixed_expenses:,.0f}")
    print(f"Debt Balances:      ${current_fin.debt_balances:,.0f}")
    print(f"Investment Balance: ${current_fin.investment_balances:,.0f}")
    print(f"Liquidity (Cash):  ${current_fin.liquidity:,.0f}")
    print(f"Net Monthly Cash:   ${current_fin.monthly_income - current_fin.fixed_expenses:,.0f}")
    
    print(f"\n>>> ENDING NET WORTH: ${ending_net_worth:,.0f} <<<")
    
    print(f"\n{'='*70}")
    print("CHANGE IN NET WORTH")
    print("=" * 70)
    change = ending_net_worth - starting_net_worth
    pct_change = (change / starting_net_worth * 100) if starting_net_worth != 0 else 0
    
    print(f"Starting Net Worth: ${starting_net_worth:,.0f}")
    print(f"Ending Net Worth:   ${ending_net_worth:,.0f}")
    print(f"Change:            ${change:+,.0f} ({pct_change:+.1f}%)")
    
    return {
        "starting_net_worth": starting_net_worth,
        "ending_net_worth": ending_net_worth,
        "change": change,
        "pct_change": pct_change
    }


if __name__ == "__main__":
    result = run_simulation("BOD-V4-SIM-BASELINE-001", 256)

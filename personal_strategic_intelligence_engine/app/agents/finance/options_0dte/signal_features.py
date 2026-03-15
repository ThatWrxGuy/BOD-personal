"""Signal Feature Calculations for SPY 0DTE Options.

This module provides functions to compute various features used in evaluating
0DTE options contracts for short-duration trading opportunities.
"""

from typing import Optional

from app.agents.finance.options_0dte.options_signal_models import (
    OptionContract,
    OptionsChain,
    MarketDataSnapshot,
)


def calculate_delta_velocity(
    contract: OptionContract,
    historical_delta: Optional[float] = None,
    time_window_minutes: int = 5,
) -> float:
    """
    Calculate delta velocity - rate of change of delta over time.
    
    Delta velocity measures how quickly the option's delta changes,
    which is crucial for 0DTE options where gamma exposure is high.
    
    Args:
        contract: Current option contract
        historical_delta: Delta value from previous observation
        time_window_minutes: Time window in minutes for velocity calculation
    
    Returns:
        Delta velocity (absolute value, higher = more acceleration potential)
    """
    if historical_delta is None:
        # Estimate velocity based on gamma and typical price movement
        # For 0DTE, gamma is very high, so estimate velocity
        gamma_factor = abs(contract.gamma) * 100  # Scale gamma
        estimated_velocity = min(gamma_factor * 0.1, 1.0)  # Cap at 1.0
        return estimated_velocity
    
    delta_change = abs(contract.delta - historical_delta)
    # Normalize by time window (assume 1 minute bars)
    velocity = delta_change / max(time_window_minutes, 1)
    return min(velocity, 1.0)  # Cap at 1.0


def calculate_gamma_exposure(contract: OptionContract, underlying_price: float) -> float:
    """
    Calculate gamma exposure (GEX) for the option contract.
    
    GEX measures the change in delta for a $1 move in the underlying.
    High gamma exposure means more delta acceleration potential.
    
    Args:
        contract: Option contract
        underlying_price: Current underlying price
    
    Returns:
        Gamma exposure score (0-100)
    """
    # Gamma exposure = gamma * underlying * contract multiplier (100)
    gamma_raw = abs(contract.gamma) * underlying_price * 100
    
    # Normalize to 0-100 scale based on typical 0DTE gamma values
    # Typical 0DTE gamma ranges from 0.01 to 0.5+
    if gamma_raw < 1:
        return gamma_raw * 50  # 0-50 range
    elif gamma_raw < 5:
        return 50 + (gamma_raw - 1) * 10  # 50-90 range
    else:
        return min(90 + (gamma_raw - 5), 100)  # 90-100 range


def calculate_premium_sensitivity(
    contract: OptionContract,
    market_data: MarketDataSnapshot,
) -> float:
    """
    Calculate premium sensitivity to price movements.
    
    Measures how sensitive the option premium is to underlying price changes.
    Higher sensitivity means more potential for quick profits in short duration.
    
    Args:
        contract: Option contract
        market_data: Current market snapshot
    
    Returns:
        Premium sensitivity score (0-100)
    """
    # Components:
    # 1. Delta (directional sensitivity)
    delta_score = abs(contract.delta) * 50
    
    # 2. Gamma (acceleration sensitivity)
    gamma_score = abs(contract.gamma) * 30
    
    # 3. Vega (vol sensitivity)
    vega_score = min(contract.vega * 10, 20)
    
    # Combine scores
    total_score = delta_score + gamma_score + vega_score
    
    # Adjust for option premium level (cheaper options = more leverage)
    if contract.mid_price > 0:
        leverage_factor = min(5.0 / contract.mid_price, 2.0)  # Cheaper = more leverage
        total_score *= leverage_factor
    
    return min(total_score, 100)


def calculate_liquidity_score(contract: OptionContract) -> float:
    """
    Calculate liquidity score based on volume, open interest, and spread.
    
    Higher liquidity means easier entry/exit with minimal slippage.
    
    Args:
        contract: Option contract
    
    Returns:
        Liquidity score (0-100)
    """
    # Volume score (0-40 points)
    volume_score = 0
    if contract.volume > 10000:
        volume_score = 40
    elif contract.volume > 1000:
        volume_score = 30
    elif contract.volume > 100:
        volume_score = 20
    elif contract.volume > 10:
        volume_score = 10
    
    # Open interest score (0-30 points)
    oi_score = 0
    if contract.open_interest > 50000:
        oi_score = 30
    elif contract.open_interest > 10000:
        oi_score = 25
    elif contract.open_interest > 1000:
        oi_score = 20
    elif contract.open_interest > 100:
        oi_score = 10
    
    # Spread score (0-30 points) - tighter is better
    spread_score = 0
    if contract.mid_price > 0:
        spread_percent = (contract.spread / contract.mid_price) * 100
        if spread_percent < 1:
            spread_score = 30
        elif spread_percent < 3:
            spread_score = 25
        elif spread_percent < 5:
            spread_score = 20
        elif spread_percent < 10:
            spread_score = 10
        else:
            spread_score = 0
    
    return min(volume_score + oi_score + spread_score, 100)


def calculate_spread_quality(contract: OptionContract) -> float:
    """
    Calculate spread quality score.
    
    Evaluates the bid-ask spread quality for the option contract.
    
    Args:
        contract: Option contract
    
    Returns:
        Spread quality score (0-100, higher = tighter spread)
    """
    if contract.mid_price <= 0:
        return 0
    
    spread_percent = (contract.spread / contract.mid_price) * 100
    
    # Convert percentage to score (inverse relationship)
    if spread_percent < 0.5:
        return 100
    elif spread_percent < 1:
        return 90
    elif spread_percent < 2:
        return 80
    elif spread_percent < 3:
        return 70
    elif spread_percent < 5:
        return 60
    elif spread_percent < 10:
        return 40
    elif spread_percent < 20:
        return 20
    else:
        return 0


def calculate_time_decay_risk(contract: OptionContract, minutes_remaining: int) -> float:
    """
    Calculate time decay (theta) risk.
    
    Measures how much value the option loses per minute due to theta decay.
    Important for 0DTE where theta accelerates exponentially.
    
    Args:
        contract: Option contract
        minutes_remaining: Minutes until expiration
    
    Returns:
        Time decay risk (0-100, higher = more risk)
    """
    # Daily theta to minute theta
    minute_theta = abs(contract.theta) / 390  # Approximate trading minutes per day
    
    # Scale by time remaining (theta accelerates as expiration approaches)
    # At 1 minute remaining, theta is extremely high
    time_multiplier = 1.0
    if minutes_remaining <= 5:
        time_multiplier = 10.0
    elif minutes_remaining <= 15:
        time_multiplier = 5.0
    elif minutes_remaining <= 30:
        time_multiplier = 3.0
    elif minutes_remaining <= 60:
        time_multiplier = 2.0
    
    theta_risk = minute_theta * time_multiplier * 1000  # Scale up
    
    # Normalize to 0-100
    return min(theta_risk, 100)


def calculate_momentum_alignment(
    contract: OptionContract,
    market_data: MarketDataSnapshot,
) -> float:
    """
    Calculate alignment between option direction and market momentum.
    
    Args:
        contract: Option contract
        market_data: Current market snapshot
    
    Returns:
        Momentum alignment score (0-100)
    """
    score = 50  # Start neutral
    
    # Direction alignment
    is_call = contract.option_type.value == "call"
    
    # Price momentum
    if market_data.change_percent > 0.5:  # Strong uptrend
        if is_call:
            score += 30
        else:
            score -= 20
    elif market_data.change_percent < -0.5:  # Strong downtrend
        if not is_call:
            score += 30
        else:
            score -= 20
    elif abs(market_data.change_percent) < 0.1:
        # Sideways - prefer ATM options
        atm_distance = abs(contract.strike - market_data.current_price)
        if atm_distance < 1:  # ATM
            score += 10
    
    # Delta alignment - higher delta = more directional exposure
    delta_alignment = abs(contract.delta) * 20
    score += delta_alignment
    
    return max(0, min(100, score))


def calculate_volatility_regime(
    contract: OptionContract,
    market_data: MarketDataSnapshot,
) -> float:
    """
    Calculate volatility regime score.
    
    Evaluates whether current IV conditions favor options trading.
    
    Args:
        contract: Option contract
        market_data: Current market snapshot
    
    Returns:
        Volatility regime score (0-100)
    """
    # IV percentile would ideally be fetched, using IV directly as proxy
    iv = contract.implied_volatility
    
    if iv < 0.10:
        # Very low IV - poor for buying options
        return 20
    elif iv < 0.15:
        # Low IV - moderate
        return 40
    elif iv < 0.25:
        # Normal IV - good for options
        return 80
    elif iv < 0.35:
        # Elevated IV - good for selling (premium capture)
        return 90
    else:
        # High IV - very elevated, potential mean reversion
        return 70


def calculate_all_features(
    contract: OptionContract,
    market_data: MarketDataSnapshot,
    options_chain: Optional[OptionsChain] = None,
    historical_delta: Optional[float] = None,
    minutes_remaining: int = 390,
) -> dict[str, float]:
    """
    Calculate all feature scores for a contract.
    
    Args:
        contract: Option contract
        market_data: Current market snapshot
        options_chain: Full options chain (optional)
        historical_delta: Previous delta for velocity calculation
        minutes_remaining: Minutes until expiration
    
    Returns:
        Dictionary of feature scores
    """
    underlying_price = market_data.current_price
    
    features = {
        "delta_velocity": calculate_delta_velocity(contract, historical_delta),
        "gamma_exposure": calculate_gamma_exposure(contract, underlying_price),
        "premium_sensitivity": calculate_premium_sensitivity(contract, market_data),
        "liquidity_score": calculate_liquidity_score(contract),
        "spread_quality": calculate_spread_quality(contract),
        "time_decay_risk": calculate_time_decay_risk(contract, minutes_remaining),
        "momentum_alignment": calculate_momentum_alignment(contract, market_data),
        "volatility_regime": calculate_volatility_regime(contract, market_data),
    }
    
    return features

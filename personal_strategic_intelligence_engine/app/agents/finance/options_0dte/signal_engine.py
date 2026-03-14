"""Signal Scoring Engine for SPY 0DTE Options.

Combines feature signals into a unified signal score for option contract ranking.
"""

from typing import Optional

from app.agents.finance.options_0dte.options_signal_models import (
    OptionContract,
    OptionsChain,
    MarketDataSnapshot,
)
from app.agents.finance.options_0dte.signal_features import calculate_all_features


# Feature weights for signal score calculation
FEATURE_WEIGHTS = {
    "delta_velocity": 0.20,        # High delta acceleration potential
    "gamma_exposure": 0.15,        # Gamma exposure for momentum plays
    "premium_sensitivity": 0.15,   # Premium sensitivity to price moves
    "liquidity_score": 0.15,      # Must have good liquidity
    "spread_quality": 0.10,        # Tight spreads matter for quick entries
    "time_decay_risk": -0.10,      # Negative - high theta is risky for buyers
    "momentum_alignment": 0.20,    # Direction alignment with market
    "volatility_regime": 0.05,     # IV conditions
}

# Minimum thresholds for signal generation
MIN_LIQUIDITY_THRESHOLD = 30
MAX_SPREAD_PERCENT_THRESHOLD = 15.0
MIN_CONFIDENCE_THRESHOLD = 40


def generate_signal_score(
    contract: OptionContract,
    market_data: MarketDataSnapshot,
    options_chain: Optional[OptionsChain] = None,
    historical_delta: Optional[float] = None,
    minutes_remaining: int = 390,
) -> tuple[float, float, dict]:
    """
    Generate combined signal score for an option contract.
    
    Args:
        contract: Option contract to score
        market_data: Current market snapshot
        options_chain: Full options chain (optional)
        historical_delta: Previous delta for velocity calculation
        minutes_remaining: Minutes until expiration
    
    Returns:
        Tuple of (signal_score, confidence_score, feature_scores)
    """
    # Calculate all features
    features = calculate_all_features(
        contract=contract,
        market_data=market_data,
        options_chain=options_chain,
        historical_delta=historical_delta,
        minutes_remaining=minutes_remaining,
    )
    
    # Calculate weighted signal score
    signal_score = 0.0
    for feature_name, weight in FEATURE_WEIGHTS.items():
        feature_value = features.get(feature_name, 0)
        
        # Apply weight (negative weight for risk factors)
        if weight < 0:
            # For risk factors, invert the score
            signal_score += weight * (100 - feature_value)
        else:
            signal_score += weight * feature_value
    
    # Ensure score is in 0-100 range
    signal_score = max(0.0, min(100.0, signal_score))
    
    # Calculate confidence score based on feature quality
    confidence_score = calculate_confidence(features, contract)
    
    return signal_score, confidence_score, features


def calculate_confidence(features: dict[str, float], contract: OptionContract) -> float:
    """
    Calculate confidence score based on feature quality.
    
    Args:
        features: Calculated feature scores
        contract: Option contract
    
    Returns:
        Confidence score (0-100)
    """
    confidence = 50.0  # Start neutral
    
    # Liquidity confidence
    liquidity = features.get("liquidity_score", 0)
    if liquidity >= 60:
        confidence += 15
    elif liquidity >= 40:
        confidence += 10
    elif liquidity >= 20:
        confidence += 5
    
    # Spread confidence
    spread = features.get("spread_quality", 0)
    if spread >= 70:
        confidence += 10
    elif spread >= 50:
        confidence += 5
    
    # Delta confidence (higher delta = more certainty in direction)
    if abs(contract.delta) >= 0.5:
        confidence += 15
    elif abs(contract.delta) >= 0.3:
        confidence += 10
    elif abs(contract.delta) >= 0.1:
        confidence += 5
    
    # Volume confidence
    if contract.volume >= 1000:
        confidence += 10
    elif contract.volume >= 100:
        confidence += 5
    
    return max(0.0, min(100.0, confidence))


def calculate_momentum_alignment_score(
    contract: OptionContract,
    market_data: MarketDataSnapshot,
) -> float:
    """
    Calculate momentum alignment score for the contract.
    
    Measures how well the option direction aligns with market momentum.
    
    Args:
        contract: Option contract
        market_data: Current market snapshot
    
    Returns:
        Momentum alignment score (0-100)
    """
    score = 50.0  # Neutral baseline
    
    is_call = contract.option_type.value == "call"
    price_change = market_data.change_percent
    
    # Strong directional alignment
    if price_change > 1.0:  # Strong uptrend
        if is_call:
            score += 35
        else:
            score -= 25
    elif price_change > 0.3:  # Moderate uptrend
        if is_call:
            score += 20
        else:
            score -= 10
    elif price_change < -1.0:  # Strong downtrend
        if not is_call:
            score += 35
        else:
            score -= 25
    elif price_change < -0.3:  # Moderate downtrend
        if not is_call:
            score += 20
        else:
            score -= 10
    
    # Delta contribution
    delta_contribution = abs(contract.delta) * 20
    score += delta_contribution
    
    return max(0.0, min(100.0, score))


def calculate_liquidity_penalty(features: dict[str, float]) -> float:
    """
    Calculate liquidity penalty for poor liquidity conditions.
    
    Args:
        features: Calculated feature scores
    
    Returns:
        Liquidity penalty (0-30)
    """
    liquidity = features.get("liquidity_score", 0)
    spread = features.get("spread_quality", 0)
    
    penalty = 0.0
    
    # Liquidity-based penalty
    if liquidity < 20:
        penalty += 15
    elif liquidity < 40:
        penalty += 10
    elif liquidity < 60:
        penalty += 5
    
    # Spread penalty
    if spread < 30:
        penalty += 15
    elif spread < 50:
        penalty += 10
    elif spread < 70:
        penalty += 5
    
    return min(penalty, 30)


def calculate_time_decay_risk_score(
    contract: OptionContract,
    minutes_remaining: int,
) -> float:
    """
    Calculate time decay risk score.
    
    Higher score means higher risk from theta decay.
    
    Args:
        contract: Option contract
        minutes_remaining: Minutes until expiration
    
    Returns:
        Time decay risk score (0-100)
    """
    # Daily theta (typically negative for long options)
    daily_theta = contract.theta
    
    # Convert to per-minute theta
    minute_theta = abs(daily_theta) / 390
    
    # Scale by time remaining (theta accelerates near expiration)
    if minutes_remaining <= 5:
        time_factor = 10.0
    elif minutes_remaining <= 15:
        time_factor = 5.0
    elif minutes_remaining <= 30:
        time_factor = 3.0
    elif minutes_remaining <= 60:
        time_factor = 2.0
    elif minutes_remaining <= 120:
        time_factor = 1.5
    else:
        time_factor = 1.0
    
    # Calculate risk score
    theta_risk = minute_theta * time_factor * 1000
    
    return min(theta_risk, 100.0)


def should_suppress_signal(
    contract: OptionContract,
    market_data: MarketDataSnapshot,
    features: dict[str, float],
) -> tuple[bool, str]:
    """
    Determine if signal should be suppressed due to risk conditions.
    
    Args:
        contract: Option contract
        market_data: Current market snapshot
        features: Calculated feature scores
    
    Returns:
        Tuple of (should_suppress, reason)
    """
    # Check liquidity threshold
    if features.get("liquidity_score", 0) < MIN_LIQUIDITY_THRESHOLD:
        return True, f"Insufficient liquidity (score: {features.get('liquidity_score', 0)})"
    
    # Check spread threshold
    if contract.mid_price > 0:
        spread_percent = (contract.spread / contract.mid_price) * 100
        if spread_percent > MAX_SPREAD_PERCENT_THRESHOLD:
            return True, f"Excessive spread ({spread_percent:.1f}%)"
    
    # Check for extreme volatility spike
    # This would require historical IV comparison - using IV as proxy
    if contract.implied_volatility > 0.5:  # 50% IV is very high
        return True, f"Extreme volatility (IV: {contract.implied_volatility:.1%})"
    
    # Check confidence threshold
    confidence = features.get("confidence_score", 0)
    if confidence < MIN_CONFIDENCE_THRESHOLD:
        return True, f"Low confidence (score: {confidence})"
    
    return False, ""


def rank_contracts(
    contracts: list[OptionContract],
    market_data: MarketDataSnapshot,
    options_chain: Optional[OptionsChain] = None,
    top_n: int = 10,
) -> list[tuple[OptionContract, float, float, dict]]:
    """
    Rank option contracts by signal score.
    
    Args:
        contracts: List of option contracts to rank
        market_data: Current market snapshot
        options_chain: Full options chain (optional)
        top_n: Number of top contracts to return
    
    Returns:
        List of tuples: (contract, signal_score, confidence, features)
    """
    scored_contracts = []
    
    for contract in contracts:
        # Skip suppressed contracts
        signal_score, confidence, features = generate_signal_score(
            contract=contract,
            market_data=market_data,
            options_chain=options_chain,
            minutes_remaining=390,  # Default to full trading day
        )
        
        # Add confidence to features
        features["confidence_score"] = confidence
        
        # Check suppression
        should_suppress, reason = should_suppress_signal(contract, market_data, features)
        if should_suppress:
            features["suppressed"] = True
            features["suppression_reason"] = reason
        
        scored_contracts.append((contract, signal_score, confidence, features))
    
    # Sort by signal score (descending)
    scored_contracts.sort(key=lambda x: x[1], reverse=True)
    
    return scored_contracts[:top_n]

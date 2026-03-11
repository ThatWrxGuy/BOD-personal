"""Intent classifier for natural language understanding."""
import re
from typing import Dict, Any, Optional, Tuple

from app.chat.chat_types import IntentType
from app.core.logging import get_logger

logger = get_logger(__name__)


class IntentClassifier:
    """Classify user intents from natural language."""
    
    def __init__(self):
        self.intent_patterns = {
            IntentType.QUERY_RISKS: [
                r"risk",
                r"danger",
                r"threat",
                r"concern",
                r"worried",
                r"what.*wrong",
            ],
            IntentType.QUERY_OPPORTUNITIES: [
                r"opportunit",
                r"potential",
                r"chance",
                r"what.*good",
                r"possibility",
            ],
            IntentType.RUN_SIMULATION: [
                r"simulat",
                r"model",
                r"what if",
                r"predict",
                r"forecast",
            ],
            IntentType.START_RESEARCH: [
                r"research",
                r"investigate",
                r"find out about",
                r"look up",
                r"analyze",
            ],
            IntentType.GENERATE_PLAN: [
                r"generat.*plan",
                r"creat.*plan",
                r"make.*strateg",
                r"plan for",
            ],
            IntentType.RUN_REVIEW: [
                r"review",
                r"check up",
                r"analyz.*status",
                r"how.*doing",
            ],
            IntentType.CHECK_FINANCES: [
                r"financ",
                r"budget",
                r"money",
                r"expense",
                r"spending",
                r"cash",
            ],
            IntentType.QUERY_GOALS: [
                r"goal",
                r"objectiv",
                r"target",
            ],
            IntentType.SYSTEM_STATUS: [
                r"status",
                r"how are you",
                r"system.*health",
            ],
            IntentType.LIST_BILLS: [
                r"bill",
                r"due",
                r"payment",
                r"upcoming",
            ],
            IntentType.CHECK_LIQUIDITY: [
                r"liquid",
                r"balance",
                r"cash flow",
                r"cash.*position",
            ],
        }
    
    def classify(self, message: str) -> Tuple[str, float]:
        """Classify the intent of a message."""
        
        message_lower = message.lower()
        
        # Score each intent
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    score += 1
            
            if score > 0:
                intent_scores[intent] = score
        
        # Get best intent
        if not intent_scores:
            return IntentType.GENERAL_QUERY.value, 0.0
        
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(0.9, intent_scores[best_intent] * 0.3)
        
        return best_intent.value, confidence
    
    def extract_parameters(self, message: str, intent: str) -> Dict[str, Any]:
        """Extract parameters from the message based on intent."""
        
        params = {}
        message_lower = message.lower()
        
        # Extract numbers for simulation
        if intent == IntentType.RUN_SIMULATION:
            numbers = re.findall(r'\d+', message)
            if numbers:
                params["amount"] = float(numbers[0])
            
            if "year" in message_lower:
                params["time_horizon_days"] = 365
            elif "month" in message_lower:
                params["time_horizon_days"] = 30
        
        # Extract time periods
        if "week" in message_lower:
            params["time_period"] = "week"
        elif "month" in message_lower:
            params["time_period"] = "month"
        elif "quarter" in message_lower:
            params["time_period"] = "quarter"
        elif "year" in message_lower:
            params["time_period"] = "year"
        
        # Extract domains
        domains = []
        if any(w in message_lower for w in ["financial", "money", "finance"]):
            domains.append("financial")
        if any(w in message_lower for w in ["health", "wellness"]):
            domains.append("health")
        if any(w in message_lower for w in ["productivity", "work"]):
            domains.append("productivity")
        
        if domains:
            params["domains"] = domains
        
        return params


async def get_intent_classifier() -> IntentClassifier:
    """Get intent classifier instance."""
    return IntentClassifier()

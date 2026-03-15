"""thinkScript Generation Engine.

Generates thinkScript code for ThinkorSwim platform.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


class ThinkScriptType(str, Enum):
    STUDY = "study"
    STRATEGY = "strategy"
    SCANNER = "scanner"
    WATCHLIST = "watchlist"


@dataclass
class ThinkScriptOutput:
    """Generated thinkScript code."""
    name: str
    script_type: ThinkScriptType
    code: str
    description: str
    parameters: List[Dict]
    timestamp: datetime


class ThinkScriptGenerator:
    """Generates thinkScript code."""
    
    def __init__(self):
        self.version = "1.0"
    
    def generate_study(
        self,
        name: str,
        plots: List[Dict],
        inputs: Optional[List[Dict]] = None,
    ) -> ThinkScriptOutput:
        """Generate a thinkScript study."""
        
        code = f"study(title=\"{name}\", overlay=false);\n\n"
        
        # Add inputs
        if inputs:
            for inp in inputs:
                code += f"input {inp['name']} = {inp['default']};\n"
            code += "\n"
        
        # Add plots
        for i, plot in enumerate(plots):
            if i > 0:
                code += "\n"
            code += f"# {plot.get('description', '')}\n"
            code += f"plot {plot['name']} = {plot['expression']};\n"
            
            if plot.get('color'):
                code += f"{plot['name']}.SetDefaultColor({plot['color']});\n"
            
            if plot.get('linewidth'):
                code += f"{plot['name']}.SetLineWidth({plot['linewidth']});\n"
        
        return ThinkScriptOutput(
            name=name,
            script_type=ThinkScriptType.STUDY,
            code=code,
            description=f"Generated study: {name}",
            parameters=inputs or [],
            timestamp=datetime.now(),
        )
    
    def generate_strategy(
        self,
        name: str,
        entry_conditions: List[Dict],
        exit_conditions: Optional[List[Dict]] = None,
    ) -> ThinkScriptOutput:
        """Generate a thinkScript strategy."""
        
        code = f"strategy(title=\"{name}\", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=10);\n\n"
        
        # Add inputs
        code += "input profitTarget = 1.0;\n"
        code += "input stopLoss = 0.5;\n\n"
        
        # Add entry conditions
        for i, entry in enumerate(entry_conditions):
            code += f"# Entry {i+1}: {entry.get('description', '')}\n"
            code += f"def {entry['name']} = {entry['condition']};\n"
            
            if entry.get('order_type') == 'BUY':
                code += f"AddOrder(OrderType.{entry['order_type']}, {entry['name']}, open[1]);\n"
            else:
                code += f"AddOrder(OrderType.{entry['order_type']}, {entry['name']}, open[1]);\n"
            code += "\n"
        
        return ThinkScriptOutput(
            name=name,
            script_type=ThinkScriptType.STRATEGY,
            code=code,
            description=f"Generated strategy: {name}",
            parameters=[],
            timestamp=datetime.now(),
        )


class GammaAccelerationStudy:
    """Generates gamma acceleration study."""
    
    def generate(self) -> ThinkScriptOutput:
        """Generate gamma acceleration study."""
        
        code = """# PSIE Gamma Acceleration Study
# Detects gamma spikes and delta momentum

input length = 20;
input gammaThreshold = 0.05;

# Simulated gamma calculation (requires options data)
def gammaVal = 0.03;  # Placeholder for actual gamma
def deltaVal = Delta();  # Requires ThinkorSwim

# Gamma spike detection
def gammaSpike = gammaVal > Average(gammaVal, length);
def gammaAcceleration = gammaVal - gammaVal[1];

# Delta momentum
def deltaMomentum = deltaVal - deltaVal[length];

# Plots
plot GammaSpike = gammaSpike;
plot GammaAcceleration = gammaAcceleration;
plot DeltaMomentum = deltaMomentum;

GammaSpike.SetDefaultColor(Color.CYAN);
GammaSpike.SetPaintingStrategy(PaintingStrategy.BOOLEAN_POINTS);

GammaAcceleration.SetDefaultColor(Color.MAGENTA);
DeltaMomentum.SetDefaultColor(Color.YELLOW);
"""
        
        return ThinkScriptOutput(
            name="PSIE_Gamma_Acceleration",
            script_type=ThinkScriptType.STUDY,
            code=code,
            description="Gamma acceleration and delta momentum detection",
            parameters=[
                {"name": "length", "type": "int", "default": 20},
                {"name": "gammaThreshold", "type": "float", "default": 0.05},
            ],
            timestamp=datetime.now(),
        )


class ThetaDecayStudy:
    """Generates theta decay study."""
    
    def generate(self) -> ThinkScriptOutput:
        """Generate theta decay study."""
        
        code = """# PSIE Theta Decay Study
# Tracks time decay and theta harvest opportunities

input length = 10;

# Theta calculation (simplified)
def theta = Theta();

# Moving average of theta
def thetaMA = Average(theta, length);

# Theta acceleration
def thetaChange = theta - theta[1];

# Plots
plot Theta = theta;
plot ThetaMA = thetaMA;
plot ThetaChange = thetaChange;

Theta.SetDefaultColor(Color.GREEN);
Theta.SetPaintingStrategy(PaintingStrategy.HISTOGRAM);

ThetaMA.SetDefaultColor(Color.RED);
ThetaChange.SetDefaultColor(Color.BLUE);
"""
        
        return ThinkScriptOutput(
            name="PSIE_Theta_Decay",
            script_type=ThinkScriptType.STUDY,
            code=code,
            description="Theta decay tracking study",
            parameters=[
                {"name": "length", "type": "int", "default": 10},
            ],
            timestamp=datetime.now(),
        )


class VolatilityBreakoutStrategy:
    """Generates volatility breakout strategy."""
    
    def generate(self) -> ThinkScriptOutput:
        """Generate volatility breakout strategy."""
        
        code = """# PSIE Volatility Breakout Strategy
# Entry on IV expansion with momentum

input atrLength = 14;
input volatilityThreshold = 1.5;

def atr = ATR(atrLength);
def avgATR = Average(atr, 20);
def volatilityRatio = atr / avgATR;

# Volatility expansion signal
def volatilityBreakout = volatilityRatio > volatilityThreshold;

# Momentum confirmation
def priceMomentum = close > close[5];

# Entry
def longSignal = volatilityBreakout and priceMomentum;

# Orders
AddOrder(OrderType.BUY_AUTO, longSignal, open);

# Exit
AddOrder(OrderType.SELL_AUTO, !longSignal, close);
"""
        
        return ThinkScriptOutput(
            name="PSIE_Volatility_Breakout",
            script_type=ThinkScriptType.STRATEGY,
            code=code,
            description="Volatility breakout trading strategy",
            parameters=[
                {"name": "atrLength", "type": "int", "default": 14},
                {"name": "volatilityThreshold", "type": "float", "default": 1.5},
            ],
            timestamp=datetime.now(),
        )


class OptionsScanner:
    """Generates options scanner code."""
    
    def generate_scanner(
        self,
        filters: List[Dict],
    ) -> ThinkScriptOutput:
        """Generate options scanner."""
        
        code = "# PSIE Options Scanner\n"
        code += "# Scanner for filtering options\n\n"
        
        for filter_def in filters:
            code += f"# {filter_def['description']}\n"
            code += f"def {filter_def['name']} = {filter_def['condition']};\n"
        
        code += "\n# Combined signal\n"
        code += "plot scan = "
        code += " and ".join([f["name"] for f in filters]) + ";\n"
        
        return ThinkScriptOutput(
            name="PSIE_Options_Scanner",
            script_type=ThinkScriptType.SCANNER,
            code=code,
            description="Custom options scanner",
            parameters=[],
            timestamp=datetime.now(),
        )


# Factory functions
def create_generator() -> ThinkScriptGenerator:
    """Create thinkScript generator."""
    return ThinkScriptGenerator()


def create_gamma_study() -> GammaAccelerationStudy:
    """Create gamma study."""
    return GammaAccelerationStudy()


def create_theta_study() -> ThetaDecayStudy:
    """Create theta study."""
    return ThetaDecayStudy()


def create_volatility_strategy() -> VolatilityBreakoutStrategy:
    """Create volatility strategy."""
    return VolatilityBreakoutStrategy()


def create_scanner() -> OptionsScanner:
    """Create options scanner."""
    return OptionsScanner()


# Add missing import
from enum import Enum

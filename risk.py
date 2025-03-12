from typing import Dict, Union
from dataclasses import dataclass

@dataclass
class RiskProfile:
    base_energy: int
    base_health: int
    base_happiness: int
    base_money: int = 0
    energy_variance: int = 0
    health_variance: int = 0
    happiness_variance: int = 0
    money_variance: int = 0

def calculate_risk_adjusted_values(action: Dict[str, Union[str, int, float]], risk_tolerance: float) -> Dict[str, int]:
    """
    Adjusts action values based on risk tolerance (-1 to 1).
    Returns dict with adjusted values.
    
    risk_tolerance: 
        -1 = extremely risk-averse (minimal variance)
        0 = neutral (baseline values)
        1 = extremely risk-seeking (maximum variance)
    """
    # Start with base values
    result = {
        'energy': action.get('energy', 0),
        'health': action.get('health', 0),
        'happiness': action.get('happiness', 0),
        'money': action.get('money', 0)
    }
    
    # Apply risk adjustments if the action has defined variances
    if 'risk_profile' in action:
        profile = action['risk_profile']
        risk_factor = (risk_tolerance + 1) / 2  # Convert from [-1,1] to [0,1]
        
        for stat in ['energy', 'health', 'happiness', 'money']:
            base = getattr(profile, f'base_{stat}')
            variance = getattr(profile, f'{stat}_variance')
            
            # More negative RT reduces variance, more positive RT increases it
            result[stat] = int(base + (variance * risk_factor))
    
    return result
from economy import compute_money_weight

def compute_weighted_sum(action, current_points):
    """Calculate the weighted sum for an action based on current points."""
    total = 0
    for key in ['energy', 'health', 'happiness']:
        factor = 1 - (current_points[key] / 50)
        total += factor * action[key]
    
    if 'money' in current_points:
        total += compute_money_weight(action, current_points['money'])
    
    return total
"""Transparent demonstration screening, NOT an agronomically validated crop model."""
from dataclasses import dataclass

# Pilot examples from TNAU's Vellore cropping-pattern pages.
# Ratings are heuristic prototype assumptions (1-5), not observed benefits.
ROTATIONS = [
    {'id':'rice_pulses','name':'Rice → Pulses','crops':['Rice','Pulses'], 'water':2, 'soil':4, 'diversity':3, 'economic':3,
     'note':'TNAU lists rice–pulses for tank-fed Vellore land. Legume benefits depend on management and soil conditions.', 'water_class':'high'},
    {'id':'rice_sesame','name':'Rice → Sesame','crops':['Rice','Sesame'], 'water':3, 'soil':2, 'diversity':3, 'economic':3,
     'note':'A locally documented alternative crop group; rice establishment still needs sufficient water.', 'water_class':'high'},
    {'id':'millet_pulses','name':'Pearl millet → Pulses','crops':['Pearl millet','Pulses'], 'water':5, 'soil':4, 'diversity':4, 'economic':2,
     'note':'A TNAU drought-year candidate, subject to soil, planting window, marketing and seed access.', 'water_class':'low'},
    {'id':'groundnut_pulses','name':'Groundnut → Pulses','crops':['Groundnut','Pulses'], 'water':4, 'soil':4, 'diversity':3, 'economic':3,
     'note':'Listed in Vellore dryland farming systems; avoid assuming two legumes guarantee nitrogen gains.', 'water_class':'medium'},
]
BY_ID = {r['id']:r for r in ROTATIONS}

@dataclass(frozen=True)
class Farm:
    current_rotation: str = 'rice_pulses'
    irrigation: str = 'limited'  # limited, reliable, rainfed
    soil: str = 'unknown'  # unknown, sandy, loamy, clay
    priority: str = 'water'  # water, soil, income
    waterlogging: bool = False
    market_for_millet: bool = True


def compare(farm: Farm, rainfall_change_pct=0, temperature_change_c=0):
    """Return baseline + at least two alternatives, with feasibility warnings.

    Climate adjustments are stress-screening heuristics rather than yield or
    water-demand estimates. Farmer constraints are displayed, not overridden.
    """
    if farm.current_rotation not in BY_ID:
        raise ValueError('Unknown existing rotation')
    if not -40 <= rainfall_change_pct <= 40 or not -2 <= temperature_change_c <= 4:
        raise ValueError('Scenario outside supported demonstration range')
    weights = {'water':(0.50,0.25,0.15,0.10),'soil':(0.20,0.50,0.20,0.10),
               'income':(0.20,0.20,0.15,0.45)}
    w = weights[farm.priority]
    results = []
    for r in ROTATIONS:
        warnings = []
        if farm.irrigation == 'rainfed' and r['water_class'] == 'high':
            warnings.append('High-water crop may be unsuitable without dependable irrigation.')
        elif farm.irrigation == 'limited' and r['water_class'] == 'high':
            warnings.append('Confirm rice-season irrigation availability.')
        if farm.waterlogging and ('Pulses' in r['crops'] or 'Groundnut' in r['crops']):
            warnings.append('Reported waterlogging: check drainage before planting sensitive crops.')
        if not farm.market_for_millet and 'Pearl millet' in r['crops']:
            warnings.append('Millet marketing constraint reported by farmer.')
        if farm.soil == 'unknown':
            warnings.append('Soil test and drainage characteristics have not been supplied.')
        if farm.soil == 'clay' and 'Groundnut' in r['crops']:
            warnings.append('Check drainage and soil suitability for groundnut.')
        # Only relative demonstrator preference: drier/hotter penalizes water-intensive sequences.
        stress = max(0,-rainfall_change_pct)/40 + max(0,temperature_change_c)/4
        stress_penalty = stress * (6-r['water']) * 5
        raw = (r['water']*w[0]+r['soil']*w[1]+r['diversity']*w[2]+r['economic']*w[3])*20
        score = max(0,round(raw - stress_penalty,1))
        results.append({**r, 'score':score, 'warnings':warnings,
                        'baseline':r['id']==farm.current_rotation,
                        'status':'Requires local review' if warnings else 'Preliminary candidate'})
    # Always show user's existing rotation, even if it ranks poorly.
    return sorted(results, key=lambda x: (not x['baseline'], -x['score']))

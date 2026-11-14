import pytest
from terrarotate.engine import Farm, compare

def test_contains_baseline_and_alternatives():
    r=compare(Farm())
    assert len(r)>=3
    assert r[0]['baseline']
    assert sum(x['baseline'] for x in r)==1

def test_drier_scenario_penalizes_high_water_more():
    a={r['id']:r['score'] for r in compare(Farm(),0,0)}
    b={r['id']:r['score'] for r in compare(Farm(),-40,0)}
    assert a['rice_pulses']-b['rice_pulses'] > a['millet_pulses']-b['millet_pulses']

def test_farmer_constraints_visible():
    r=compare(Farm(irrigation='rainfed',soil='unknown',waterlogging=True))
    rice=next(r for r in r if r['id']=='rice_pulses')
    assert any('irrigation' in w for w in rice['warnings'])
    assert any('waterlogging' in w for w in rice['warnings'])

def test_invalid_climate_scenario():
    with pytest.raises(ValueError): compare(Farm(),-99,0)

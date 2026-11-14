from terrarotate.engine import Farm, compare
from terrarotate.report import build_report

def test_report_has_baseline_alternatives_and_caveats():
    farm=Farm()
    html=build_report(farm,(12.9,79.1),compare(farm))
    assert 'Current rotation' in html
    assert 'Alternative' in html
    assert 'No NASA observations loaded' in html
    assert 'not validated yields' in html
    assert '12.9000' in html

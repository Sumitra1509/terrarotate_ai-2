import pandas as pd
from terrarotate.intelligence import build_evidence, evidence_flags, _dry_spells

def test_dry_spells_separated_and_missing_breaks():
    s=pd.Series([0]*8+[5]+[0]*6+[None]+[0]*7)
    assert _dry_spells(s)==2

def test_historical_evidence_no_invented_anomaly():
    dates=pd.date_range('2020-01-01','2020-12-31')
    df=pd.DataFrame({'PRECTOTCORR':[2.0]*len(dates),'T2M_MAX':[34.]*len(dates),'WS10M':[2.]*len(dates)},index=dates)
    e=build_evidence(df)
    assert e.valid_days==366
    assert e.mean_annual_rain_mm==732.
    assert e.rainfall_anomaly_last_pct is None
    assert e.annual_dry_spells==0
    assert evidence_flags(e)==[]

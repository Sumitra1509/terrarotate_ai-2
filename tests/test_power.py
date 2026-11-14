from datetime import date
from unittest.mock import patch
import pandas as pd
import pytest
from terrarotate.nasa_power import fetch_power, climate_summary

def test_coordinate_validation():
    with pytest.raises(ValueError): fetch_power(95,79,date(2019,1,1),date(2020,1,1))

def test_fetch_parsing_and_cache(tmp_path):
    days=pd.date_range('2020-01-01', periods=32)
    datekeys=[x.strftime('%Y%m%d') for x in days]
    payload={'properties':{'parameter':{p:{d:(2.0 if p=='PRECTOTCORR' else 30.0) for d in datekeys} for p in ['T2M_MAX','T2M_MIN','PRECTOTCORR','WS10M']}}}
    class Response:
        def raise_for_status(self): pass
        def json(self): return payload
    with patch('terrarotate.nasa_power.requests.get',return_value=Response()) as mock:
        frame,source=fetch_power(12.9,79.1,date(2020,1,1),date(2020,2,2),tmp_path)
        assert len(frame)==32
        assert mock.call_count==1
    with patch('terrarotate.nasa_power.requests.get',side_effect=AssertionError('Network should not be accessed')):
        _,source=fetch_power(12.9,79.1,date(2020,1,1),date(2020,2,2),tmp_path)
        assert 'cached' in source
    assert climate_summary(frame)['valid_days']==32

"""Download historical daily NASA POWER point data; no manufactured observations."""
from datetime import date
from pathlib import Path
import hashlib
import json
import pandas as pd
import requests

BASE_URL = 'https://power.larc.nasa.gov/api/temporal/daily/point'
PARAMS = ['T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'WS10M']


def fetch_power(lat: float, lon: float, start: date, end: date, cache_dir='data/cache'):
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('Invalid coordinates')
    if start >= end or end >= date.today():
        raise ValueError('Choose a completed historical date range')
    key = hashlib.sha256(f'{lat:.3f}:{lon:.3f}:{start}:{end}:{",".join(PARAMS)}'.encode()).hexdigest()[:20]
    cache = Path(cache_dir) / f'power_{key}.json'
    if cache.exists():
        payload = json.loads(cache.read_text())
        source = 'NASA POWER (local cached response)'
    else:
        query = dict(latitude=lat, longitude=lon, start=start.strftime('%Y%m%d'),
                     end=end.strftime('%Y%m%d'), parameters=','.join(PARAMS),
                     community='AG', format='JSON', **{'time-standard': 'UTC'})
        response = requests.get(BASE_URL, params=query, timeout=35)
        response.raise_for_status()
        payload = response.json()
        if 'properties' not in payload or 'parameter' not in payload['properties']:
            raise ValueError('Unexpected POWER response')
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(payload))
        source = 'NASA POWER (downloaded response)'
    variables = payload['properties']['parameter']
    missing = set(PARAMS) - variables.keys()
    if missing:
        raise ValueError(f'Missing parameters: {sorted(missing)}')
    df = pd.DataFrame({p: pd.Series(variables[p], dtype='float64') for p in PARAMS})
    df.index = pd.to_datetime(df.index, format='%Y%m%d', errors='coerce')
    df = df.sort_index()
    df.index.name = 'date'
    df = df.where(df > -900)  # POWER fill value often -999
    if df.empty or df['PRECTOTCORR'].notna().sum() < 30:
        raise ValueError('Too few valid observations for meaningful analysis')
    return df, source


def climate_summary(df: pd.DataFrame):
    rain = df['PRECTOTCORR'].clip(lower=0)
    valid_days = int(rain.notna().sum())
    annual_rain = rain.resample('YE').sum(min_count=300).dropna()
    return {
        'valid_days': valid_days,
        'date_start': df.index.min().date().isoformat(),
        'date_end': df.index.max().date().isoformat(),
        'total_rain_mm': round(float(rain.sum()), 1),
        'mean_annual_rain_mm': round(float(annual_rain.mean()), 1) if len(annual_rain) else None,
        'days_over_35c': int((df['T2M_MAX'] > 35).sum()),
        'dry_days_below_1mm': int((rain < 1).sum()),
        'mean_daily_wind_ms': round(float(df['WS10M'].mean()), 2),
        'rainfall_cv': round(float(annual_rain.std() / annual_rain.mean()), 2) if len(annual_rain)>2 and annual_rain.mean()>0 else None,
    }

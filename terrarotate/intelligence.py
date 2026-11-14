"""Evidence-oriented climate diagnostics. Descriptive statistics, not forecasts."""
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class ClimateEvidence:
    period: str
    valid_days: int
    mean_annual_rain_mm: float | None
    rainfall_cv: float | None
    annual_hot_days: float | None
    annual_dry_spells: float | None
    mean_wind_ms: float | None
    rainfall_anomaly_last_pct: float | None
    caveats: tuple[str, ...]


def _dry_spells(series: pd.Series, threshold=1., days=7):
    """Number of non-overlapping runs >= days, ignoring missing observations."""
    count, run = 0, 0
    for x in series:
        if pd.isna(x):
            if run >= days: count += 1
            run = 0
        elif x < threshold:
            run += 1
        else:
            if run >= days: count += 1
            run = 0
    return count + (run >= days)


def build_evidence(df: pd.DataFrame) -> ClimateEvidence:
    required = {'PRECTOTCORR', 'T2M_MAX', 'WS10M'}
    if not required.issubset(df.columns) or not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError('Expected dated NASA POWER observations')
    df = df.sort_index()
    rain = df.PRECTOTCORR.where(df.PRECTOTCORR >= 0)
    counts = rain.resample('YE').count()
    full = counts >= 300
    annual = rain.resample('YE').sum(min_count=300)[full].dropna()
    hot = (df.T2M_MAX > 35).where(df.T2M_MAX.notna()).resample('YE').sum(min_count=300)[full].dropna()
    dry_counts = []
    for yr, part in rain.groupby(rain.index.year):
        if part.notna().sum() >= 300:
            dry_counts.append(_dry_spells(part))
    anomaly = None
    if len(annual) >= 4 and annual.iloc[:-1].mean() > 0:
        anomaly = round((annual.iloc[-1] / annual.iloc[:-1].mean() - 1)*100, 1)
    cv = None
    if len(annual) >= 3 and annual.mean() > 0:
        cv = round(float(annual.std()/annual.mean()), 2)
    caveats = (
        'NASA POWER is gridded meteorology, not an on-farm rain gauge.',
        'Historical averages and last-year departures are not weather forecasts.',
        'Mean wind speed is not a gust or banana-lodging prediction.',
        'Crop water needs, yields and soil-carbon changes are not calculated.',
    )
    return ClimateEvidence(
        period=f'{df.index.min():%Y-%m-%d} to {df.index.max():%Y-%m-%d}',
        valid_days=int(rain.notna().sum()),
        mean_annual_rain_mm=round(float(annual.mean()),1) if len(annual) else None,
        rainfall_cv=cv,
        annual_hot_days=round(float(hot.mean()),1) if len(hot) else None,
        annual_dry_spells=round(float(sum(dry_counts)/len(dry_counts)),1) if dry_counts else None,
        mean_wind_ms=round(float(df.WS10M.mean()),2) if df.WS10M.notna().any() else None,
        rainfall_anomaly_last_pct=anomaly,
        caveats=caveats)


def evidence_flags(evidence: ClimateEvidence):
    """Descriptive flags based on declared demo thresholds, not locally calibrated warnings."""
    flags = []
    if evidence.rainfall_cv is not None and evidence.rainfall_cv >= 0.30:
        flags.append(('Rainfall variability', 'Historical rainfall variation is high under a *demo* coefficient-of-variation threshold (0.30).'))
    if evidence.annual_dry_spells is not None and evidence.annual_dry_spells >= 4:
        flags.append(('Dry-spell exposure','Historical record includes frequent 7+ day periods with under 1 mm of daily precipitation.'))
    if evidence.annual_hot_days is not None and evidence.annual_hot_days >= 40:
        flags.append(('Heat exposure','Historical record includes many days above the *demo* 35°C threshold.'))
    return flags

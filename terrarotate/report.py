"""Printable self-contained HTML decision report with traceable evidence and caveats."""
from html import escape
from datetime import datetime, timezone


def _v(value, unit=''):
    return 'Not available' if value is None else f'{escape(str(value))}{unit}'


def build_report(farm, location, results, evidence=None, source='not loaded', rain_pct=0, temp_c=0):
    lat, lon = location
    metrics = ''
    if evidence:
        metrics = f'''<section><h2>NASA evidence (historical)</h2>
        <p>Source: {escape(source)} · {escape(evidence.period)} · {evidence.valid_days} valid rainfall days</p>
        <div class="metrics">
        <div><b>{_v(evidence.mean_annual_rain_mm,' mm')}</b><span>Mean annual rainfall</span></div>
        <div><b>{_v(evidence.rainfall_cv)}</b><span>Annual rainfall variability (CV)</span></div>
        <div><b>{_v(evidence.annual_hot_days)}</b><span>Mean hot days/year (&gt;35°C)</span></div>
        <div><b>{_v(evidence.annual_dry_spells)}</b><span>Mean 7+ day dry spells/year</span></div>
        </div><p class="muted">The rainfall anomaly for the last complete year vs earlier available years: {_v(evidence.rainfall_anomaly_last_pct,'%')}.</p>
        </section>'''
    else:
        metrics = '<section><h2>NASA evidence</h2><p class="notice">No NASA observations loaded. This report contains demonstration crop screening only.</p></section>'
    rows = ''
    for r in results:
        warnings = ' '.join(f'<li>{escape(w)}</li>' for w in r['warnings']) or '<li>Local soil, planting calendar and economics must still be verified.</li>'
        rows += f'''<article><header><h3>{'Current rotation · ' if r['baseline'] else 'Alternative · '}{escape(r['name'])}</h3>
        <strong>{r['score']:.1f}/100</strong></header>
        <p>{escape(r['note'])}</p><p><b>Status:</b> {escape(r['status'])}</p><b>Review points</b><ul>{warnings}</ul></article>'''
    limitations = '''<li>Scores are illustrative heuristic preferences; not validated yields, irrigation savings or profits.</li>
    <li>No groundwater depth, subsurface flow, lightning strike or near-term wind gust is predicted.</li>
    <li>Local experts must review seasonality, crop-specific soil suitability, pest risks and markets.</li>
    <li>Rainfall and temperature sliders are hypothetical sensitivity tests, not El Niño forecasts.</li>'''
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>TerraRotate Farm Resilience Report</title>
    <style>body{{max-width:900px;margin:35px auto;padding:0 22px;color:#142923;font:15px/1.6 system-ui,Arial}}h1{{color:#176742;font-size:34px;margin:0}}h2{{margin-top:32px;border-bottom:1px solid #d5e5db;padding-bottom:6px}}.tag{{color:#176742;text-transform:uppercase;font-size:12px;font-weight:750;letter-spacing:2px}}.muted{{color:#567267}}.notice{{background:#fff4dc;padding:12px;border-radius:8px}}.metrics{{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}}.metrics div{{padding:12px;background:#eef6f0;border-radius:12px}}.metrics b{{font-size:25px;display:block}}.metrics span{{color:#567267}}article{{margin:12px 0;border:1px solid #cce0d4;padding:16px;border-radius:12px}}article header{{display:flex;justify-content:space-between;gap:12px}}h3{{margin:0}}@media print{{body{{margin:0}}article{{break-inside:avoid}}}}</style></head>
    <body><div class="tag">TerraRotate AI · Vellore pilot</div><h1>Farm Resilience Report</h1><p class="muted">Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M UTC} · Method: transparent prototype screening</p>
    <section><h2>Farm context</h2><p><b>Location:</b> {lat:.4f}, {lon:.4f} (user selected) · <b>Existing rotation:</b> {escape(farm.current_rotation)}<br>
    <b>Irrigation:</b> {escape(farm.irrigation)} · <b>Soil:</b> {escape(farm.soil)} · <b>Priority:</b> {escape(farm.priority)}<br>
    <b>Waterlogging observed:</b> {'Yes' if farm.waterlogging else 'No'} · <b>Millet market available:</b> {'Yes' if farm.market_for_millet else 'No'}</p>
    <p><b>Hypothetical scenario:</b> Rainfall {rain_pct:+d}% · Temperature {temp_c:+.1f}°C</p></section>
    {metrics}<section><h2>Current rotation and alternatives</h2>{rows}</section>
    <section><h2>What the evidence does not establish</h2><ul>{limitations}</ul></section>
    <section><h2>References and provenance</h2><p>NASA POWER Daily API: https://power.larc.nasa.gov/docs/services/api/temporal/daily/<br>
    TNAU cropping patterns: https://agritech.tnau.ac.in/<br>All numeric climate metrics are only reported when a NASA response was explicitly loaded.</p></section>
    <footer class="muted">Decision support only. The farmer and local agricultural experts remain responsible for planting decisions.</footer></body></html>'''

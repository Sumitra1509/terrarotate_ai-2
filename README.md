# TerraRotate AI · Vellore Pilot

**NASA Space Apps Challenge 2026 · Field Shift: Adapting Farms with NASA Data**

A runnable Streamlit decision-support prototype combining **real, on-demand NASA POWER historical meteorology** with a documented, **illustrative** comparison of existing and alternative crop rotations. Inspired by the *risk → mitigation → report* product journey of Astro Sweepers; all TerraRotate code and interface content is independently written.

## Features

1. Farm profile: coordinates, existing rotation, irrigation, soil, drainage, market constraints, priority.
2. Actual NASA POWER historical weather: precipitation, Tmax, wind; locally cached.
3. Historical climate indicators: annual rain, coefficient of variation, heat days, non-overlapping 7+ day dry spells, last complete year comparison.
4. Four illustrative crop sequences including the farmer's baseline. Constraint warnings are displayed clearly.
5. Rainfall and temperature *hypothetical* sliders for demonstration sensitivity.
6. Farm risk/water guidance with limitations on groundwater, gusts and lightning.
7. Downloadable, self-contained **Farm Resilience Report** in printable HTML.
8. Unit tests and an explicit methodology/limitations statement.

### Start

Requirements: Python 3.10+ and an internet connection for the first NASA fetch.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows, activate with `.venv\\Scripts\\activate`. Run tests:

```bash
python -m pytest -q
```

Open the app, configure a farm in the sidebar, fetch real NASA weather on the **Climate intelligence** tab, compare rotations, and download an evidence report.

### Data integrity

- There is **no fabricated NASA data**. A failed network fetch displays an error and keeps observations unavailable.
- NASA POWER is a **gridded estimate**, not an on-farm station. Only complete annual periods with at least 300 valid daily rainfall observations are summarized into annual precipitation statistics.
- High rain variability (CV >= 0.30), frequent dry spells (>= 4 per year), and heat exposure (>= 40 hot days/year) are **prototype thresholds**; NOT calibrated alerts.
- Crop suitability ratings in `terrarotate/engine.py` are **heuristic demo inputs, not validated scientific models**. Climate data is shown alongside—not fed into—the numeric rankings yet. Climate sliders change the demonstration ranking through declared assumptions; they are **not forecasts**.
- Candidate crop sequences require validation of crop calendars, prices, water demand, soils, drainage and local plant disease expertise.
- The app does **not** measure groundwater flow or depth, predict wind gusts, predict lightning strikes, recommend borewell drilling or give crop-yield projections.
- No soil probe, voice assistant, GPM, Landsat, GRACE, official real-time alert provider, or LLM is integrated in this version.

### Project structure

```
app.py                       Streamlit dashboard
terrarotate/nasa_power.py     NASA POWER API with disk caching
terrarotate/intelligence.py   Historical climate evidence and transparent flags
terrarotate/engine.py         Declared crop heuristics + farmer constraints
terrarotate/report.py         Standalone HTML resilience report
 tests/                       Automated unit tests
 docs/                        Scope, limitations, roadmap, pitch
```

### Data sources
- [NASA POWER daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)
- [TNAU agriculture and agrometeorology](https://www.agritech.tnau.ac.in/)
- [Official 2026 Field Shift challenge](https://www.spaceappschallenge.org/2026/challenges/field-shift-adapting-farms-with-nasa-data/)

### Next milestones
1. Incorporate checked local crop parameters, sowing calendar and soil/irrigation budgets into defensible crop feasibility rules.
2. Integrate GPM and Landsat with spatial/temporal provenance and clear resolution disclaimers.
3. Validate scenarios against real local agronomy; add farmer-readable evidence grading.
4. Optionally add calibrated soil probe and Tamil two-way voice UI in later versions.

**For research and planning only; do not interpret outputs as verified agronomic advice.**

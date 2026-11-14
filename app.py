"""TerraRotate AI: NASA Space Apps Field Shift competition prototype."""
from datetime import date
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from terrarotate.nasa_power import fetch_power
from terrarotate.engine import Farm, ROTATIONS, compare
from terrarotate.intelligence import build_evidence, evidence_flags
from terrarotate.report import build_report

st.set_page_config(page_title='TerraRotate AI | Vellore', page_icon='🌱', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{padding-top:2rem;max-width:1350px}
[data-testid="stMetric"]{background:#f0f7ef;padding:14px;border:1px solid #d7e5d8;border-radius:12px}
h1,h2,h3{letter-spacing:-.025em}
.hero{padding:30px;background:linear-gradient(110deg,#123f2c,#20754e);border-radius:20px;color:white;margin-bottom:20px}
.hero h1{color:white;margin:0;font-size:2.55rem}.hero p{color:#d6eee0;margin:8px 0 0}
.pill{display:inline-block;background:#c9edd8;color:#124e30;border-radius:30px;padding:4px 12px;font-size:12px;font-weight:bold}
</style>''',unsafe_allow_html=True)
st.markdown('''<div class="hero"><span class="pill">NASA SPACE APPS · FIELD SHIFT</span><h1>🌱 TerraRotate AI</h1>
<p>From space to soil. A Vellore pilot that turns Earth observations into transparent crop-rotation decisions.</p></div>''',unsafe_allow_html=True)
st.caption('Decision-support prototype · No claims of validated yield gains, groundwater depth, wind forecasts or lightning prediction')

with st.sidebar:
    st.header('📍 Your farm')
    lat=st.number_input('Latitude',-90.,90.,12.9165,format='%.4f')
    lon=st.number_input('Longitude',-180.,180.,79.1325,format='%.4f')
    rot_labels={r['name']:r['id'] for r in ROTATIONS}
    selected=st.selectbox('Existing crop rotation',list(rot_labels))
    irrigation=st.selectbox('Water access',['limited','rainfed','reliable'],help='A farmer-reported condition; not calculated from satellite data')
    soil=st.selectbox('Soil texture',['unknown','sandy','loamy','clay'])
    priority=st.selectbox('Main goal',['water','soil','income'],format_func=lambda x:{'water':'Conserve water','soil':'Improve soil health','income':'Protect income'}[x])
    waterlogging=st.checkbox('Field holds water after rain')
    market=st.checkbox('Local market for millet is available',value=True)
    st.divider()
    st.header('🌦️ Climate stress test')
    rain_change=st.slider('Rainfall change (%)',-40,40,0,5)
    temp_change=st.slider('Temperature change (°C)',-2.,4.,0.,0.5)
    st.caption('Hypothetical scenarios only, not a forecast or El Niño prediction.')

farm=Farm(rot_labels[selected],irrigation,soil,priority,waterlogging,market)
results=compare(farm,rain_change,temp_change)
state=st.session_state
# Prevent data from one location being presented as another location's observation.
key=(round(lat,4),round(lon,4))
df=state.get('nasa_data') if state.get('nasa_location')==key else None
source=state.get('nasa_source','Not loaded') if df is not None else 'Not loaded'
evidence=build_evidence(df) if df is not None else None

tab1,tab2,tab3,tab4=st.tabs(['🛰️ Climate intelligence','🌾 Rotation decisions','🛡️ Farm risk & water','📄 Resilience report'])
with tab1:
    st.subheader('NASA POWER · Historical environmental observations')
    st.write('Choose a completed range of years and fetch actual NASA POWER gridded meteorology. This requires internet access on first use; results are cached locally.')
    c1,c2,c3=st.columns([1,1,2])
    with c1: start_year=st.number_input('From',1981,date.today().year-2,2016,step=1)
    with c2: end_year=st.number_input('Through',1982,date.today().year-1,2025,step=1)
    with c3:
        st.write('')
        fetch=st.button('Fetch NASA observations',type='primary',use_container_width=True)
    if fetch:
        if start_year>=end_year:
            st.error('The beginning year must precede the final year.')
        else:
            with st.spinner('Loading historical gridded data from NASA POWER...'):
                try:
                    new_df, new_source=fetch_power(lat,lon,date(int(start_year),1,1),date(int(end_year),12,31),cache_dir=Path(__file__).parent/'data'/'cache')
                    state['nasa_data']=new_df
                    state['nasa_source']=new_source
                    state['nasa_location']=key
                    st.rerun()
                except Exception as exc:
                    st.error(f'NASA data unavailable: {exc}. No synthetic observations were substituted.')
    st.map(pd.DataFrame({'lat':[lat],'lon':[lon]}),zoom=8)
    if evidence:
        st.success(f'{source} · {evidence.period} · {evidence.valid_days:,} valid rainfall days')
        a,b,c,d=st.columns(4)
        a.metric('Mean yearly rainfall',f'{evidence.mean_annual_rain_mm:,.0f} mm' if evidence.mean_annual_rain_mm is not None else 'N/A')
        b.metric('Yearly rainfall CV',evidence.rainfall_cv if evidence.rainfall_cv is not None else 'N/A')
        c.metric('Avg. hot days/year',evidence.annual_hot_days if evidence.annual_hot_days is not None else 'N/A')
        d.metric('Avg. 7+ day dry spells',evidence.annual_dry_spells if evidence.annual_dry_spells is not None else 'N/A')
        annual=df.PRECTOTCORR.clip(lower=0).resample('YE').sum(min_count=300).dropna()
        if len(annual):
            chart_df=pd.DataFrame({'Year':annual.index.year.astype(str),'Rainfall (mm)':annual.values})
            st.plotly_chart(px.bar(chart_df,x='Year',y='Rainfall (mm)',title='Year-by-year estimated rainfall',color_discrete_sequence=['#378763']),use_container_width=True)
        monthly=df[['PRECTOTCORR','T2M_MAX']].resample('MS').agg({'PRECTOTCORR':'sum','T2M_MAX':'mean'}).reset_index()
        monthly=monthly.rename(columns={'date':'Month','PRECTOTCORR':'Monthly rainfall (mm)','T2M_MAX':'Average max temperature (°C)'})
        st.plotly_chart(px.line(monthly,x='date',y='Monthly rainfall (mm)',title='Monthly precipitation history',color_discrete_sequence=['#2f83a6']),use_container_width=True)
        flags=evidence_flags(evidence)
        if flags:
            for name,description in flags: st.warning(f'**{name}:** {description}')
        else: st.info('No historical diagnostic exceeded our explicit demonstration thresholds. This does not imply that the farm is risk-free.')
        st.download_button('Download NASA observations CSV',df.to_csv().encode(),file_name='terrarotate_nasa_power.csv',mime='text/csv')
        st.caption('Thresholds are exploratory and NOT locally validated warning levels. POWER estimates represent a grid cell rather than your specific field.')
    else:
        st.info('Select **Fetch NASA observations** to see real historical climate indicators. Rotation screening remains usable without the download.')
        st.write('Source: [NASA POWER Daily API](https://power.larc.nasa.gov/docs/services/api/temporal/daily/)')

with tab2:
    st.subheader('Three-way crop strategy comparison')
    st.write('Your current rotation is always included. Alternatives are exploratory candidates based on transparent, simplified ratings and constraints.')
    view=pd.DataFrame([{'Strategy':r['name'],'Score (illustrative)':r['score'],'Type':'Current' if r['baseline'] else 'Alternative'} for r in results])
    st.plotly_chart(px.bar(view,x='Score (illustrative)',y='Strategy',color='Type',orientation='h',range_x=[0,100],color_discrete_map={'Current':'#85928c','Alternative':'#238654'},title='Preference-weighted screening scores'),use_container_width=True)
    st.caption('Scores are not crop yields, actual water savings, profitability, or NASA-derived crop suitability.')
    for r in results:
        with st.expander(('🏡 EXISTING · ' if r['baseline'] else '🌿 CANDIDATE · ')+r['name']+f" — {r['score']:.1f}/100",expanded=r['baseline']):
            st.write(r['note'])
            st.write('**Review status:** '+r['status'])
            if r['warnings']:
                for issue in r['warnings']: st.warning(issue)
            else: st.info('Local growing calendar, drainage, crop water requirements, soil test and economics still need verification.')
    if evidence:
        st.info('NASA climate evidence is displayed in the Climate tab and attached to your report. These screening scores do not yet use NASA-derived water balances; integrating calibrated crop parameters is a next-phase task.')
    st.markdown('**Source for regional candidate sequences:** [TNAU cropping-pattern resources](https://www.agritech.tnau.ac.in/)')

with tab3:
    st.subheader('Risks a farmer can act on')
    c1,c2=st.columns(2)
    with c1:
        st.markdown('#### 💧 Water planning')
        st.write('Use historical seasonal precipitation, farmer-described irrigation supply and soil information to identify questions about water availability before changing crops.')
        if evidence:
            st.metric('Historical rainfall variation',evidence.rainfall_cv if evidence.rainfall_cv is not None else 'N/A')
            st.metric('Last complete year rainfall departure',f'{evidence.rainfall_anomaly_last_pct:+.1f}%' if evidence.rainfall_anomaly_last_pct is not None else 'N/A')
        st.warning('No on-farm water-table depth, borewell success, subsurface flow or real-time soil moisture is inferred from POWER.')
    with c2:
        st.markdown('#### 🌬️ Banana and lightning safety')
        st.write('Bananas can require wind-protection planning, including locally appropriate propping and crop-stage review before hazardous weather.')
        if evidence: st.metric('Historical mean daily 10 m wind',f'{evidence.mean_wind_ms:.2f} m/s' if evidence.mean_wind_ms is not None else 'N/A')
        st.error('Historical wind means are not gust forecasts. The app does not predict lightning strikes. During storms, stop work and use official warnings.')
        st.markdown('[India Meteorological Department](https://mausam.imd.gov.in/) · [NASA POWER documentation](https://power.larc.nasa.gov/)')
    st.divider()
    st.markdown('#### 🧭 Decision boundaries')
    for line in ['Satellite data describe broad environmental patterns, not the state of an individual soil layer.','A soil-moisture probe could later provide measured shallow soil values, subject to calibration.','Regional groundwater indicators do not measure a specific farm’s water table.','Dry and wet scenario sliders are hypothetical, not seasonal forecasts.']:
        st.write('• '+line)

with tab4:
    st.subheader('Farm Resilience Report')
    st.write('As in a strong decision-support submission, every strategy can be exported alongside the available evidence, uncertainties and action points.')
    html=build_report(farm,(lat,lon),results,evidence,source,rain_change,temp_change)
    st.download_button('⬇️ Download printable HTML report',html.encode('utf-8'),file_name='TerraRotate_Farm_Resilience_Report.html',mime='text/html',type='primary')
    st.markdown('**Report includes**: farm assumptions · actual NASA evidence if loaded · baseline and alternative strategies · feasibility checks · scientific limitations · data attribution.')
    st.info('Open the downloaded HTML in a browser and choose Print → Save as PDF if you want a PDF copy.')

st.divider()
st.caption('TerraRotate AI · Pilot research build · Built for the NASA Space Apps Field Shift challenge · Farmers and local experts retain decision authority.')

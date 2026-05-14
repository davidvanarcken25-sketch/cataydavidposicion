import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="MPU6050 Dashboard IoT",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%); }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1b2a 0%, #112240 100%); border-right: 1px solid #1e3a5f; }
h1 { font-family: 'Syne', sans-serif !important; font-weight: 800 !important; background: linear-gradient(90deg, #00d4ff, #7b2fff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
h2, h3 { font-family: 'Syne', sans-serif !important; color: #64ffda !important; }
[data-testid="metric-container"] { background: linear-gradient(135deg, #112240, #0d1b2a); border: 1px solid #1e3a5f; border-radius: 12px; padding: 16px !important; box-shadow: 0 4px 20px rgba(0,212,255,0.08); transition: transform 0.2s, box-shadow 0.2s; }
[data-testid="metric-container"]:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(0,212,255,0.18); border-color: #00d4ff; }
[data-testid="metric-container"] label { color: #8892b0 !important; font-family: 'Space Mono', monospace !important; font-size: 0.75rem !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #00d4ff !important; font-family: 'Space Mono', monospace !important; font-size: 1.4rem !important; }
[data-baseweb="tab-list"] { background: #112240; border-radius: 12px; padding: 4px; border: 1px solid #1e3a5f; gap: 4px; }
[data-baseweb="tab"] { border-radius: 8px !important; color: #8892b0 !important; font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important; padding: 8px 16px !important; }
[aria-selected="true"] { background: linear-gradient(135deg, #00d4ff22, #7b2fff22) !important; color: #00d4ff !important; border: 1px solid #00d4ff44 !important; }
.stButton > button { background: linear-gradient(135deg, #00d4ff22, #7b2fff22); border: 1px solid #00d4ff66; color: #00d4ff; font-family: 'Space Mono', monospace; border-radius: 8px; transition: all 0.2s; }
.stButton > button:hover { background: linear-gradient(135deg, #00d4ff44, #7b2fff44); border-color: #00d4ff; box-shadow: 0 0 20px rgba(0,212,255,0.3); }
.sensor-card { background: linear-gradient(135deg, #112240, #0d1b2a); border: 1px solid #1e3a5f; border-radius: 12px; padding: 20px; margin: 8px 0; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
.header-badge { display: inline-block; background: linear-gradient(135deg, #00d4ff22, #7b2fff22); border: 1px solid #00d4ff44; border-radius: 20px; padding: 4px 14px; font-family: 'Space Mono', monospace; font-size: 0.75rem; color: #00d4ff; margin: 4px 2px; }
</style>
""", unsafe_allow_html=True)

COLORES_EJES = {
    'accel_x': '#00d4ff', 'accel_y': '#7b2fff', 'accel_z': '#00ff88',
    'gyro_x' : '#ff6b6b', 'gyro_y' : '#ffd93d', 'gyro_z' : '#ff9f43',
}
UNIDADES = {
    'accel_x': 'm/s²', 'accel_y': 'm/s²', 'accel_z': 'm/s²',
    'gyro_x' : 'rad/s', 'gyro_y' : 'rad/s', 'gyro_z' : 'rad/s',
}
CAMPOS_ACCEL = ['accel_x','accel_y','accel_z']
CAMPOS_GYRO  = ['gyro_x','gyro_y','gyro_z']
TODOS_CAMPOS = CAMPOS_ACCEL + CAMPOS_GYRO

st.markdown("""
<h1 style='text-align:center; font-size:2.8rem; margin-bottom:0'>
    🤖 MPU6050 · Dashboard IoT
</h1>
<p style='text-align:center; color:#8892b0; font-family:Space Mono,monospace; font-size:0.85rem; margin-top:4px'>
    Análisis de movimiento · ESP32 + InfluxDB · Universidad EAFIT
</p>
<div style='text-align:center; margin:12px 0 24px'>
    <span class='header-badge'>📡 ESP32</span>
    <span class='header-badge'>🧭 MPU6050</span>
    <span class='header-badge'>☁️ InfluxDB</span>
    <span class='header-badge'>📍 Medellín</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    st.markdown("---")
    st.markdown("### 📁 Cargar datos")
    uploaded_file = st.file_uploader("Archivo CSV del sensor", type=["csv"])
    st.markdown("---")
    st.markdown("### 🎛️ Parámetros")
    umbral_z   = st.slider("Umbral Z-score", 1.5, 4.0, 2.5, 0.1)
    ventana_mm = st.slider("Ventana media móvil (min)", 2, 20, 5, 1)
    st.markdown("---")
    st.markdown("""
    <div class='sensor-card'>
        <p style='color:#64ffda; font-family:Space Mono,monospace; font-size:0.8rem; margin:0'>
        🏫 Universidad EAFIT<br>
        📌 6.2006°N, 75.5783°W<br>
        🔧 ESP32 + MPU6050<br>
        ⏱️ Cada 2 segundos
        </p>
    </div>
    """, unsafe_allow_html=True)

with st.expander("📍 Ubicación del sensor — Universidad EAFIT", expanded=False):
    mapa_df = pd.DataFrame({'lat':[6.2006],'lon':[-75.5783]})
    st.map(mapa_df, zoom=15)

if uploaded_file is None:
    st.info("⬅️ Carga un archivo CSV en el panel izquierdo para comenzar.")
    st.markdown("### 📋 Formato esperado del CSV")
    ejemplo = pd.DataFrame({
        'Time'   : ['2025-05-14 20:10:00','2025-05-14 20:10:02'],
        'accel_x': [0.12, 0.11], 'accel_y': [-0.05, -0.06], 'accel_z': [9.78, 9.79],
        'gyro_x' : [0.001,0.002], 'gyro_y': [-0.003,-0.002], 'gyro_z': [0.000,0.001],
    })
    st.dataframe(ejemplo, use_container_width=True)
    st.stop()

try:
    df_raw = pd.read_csv(uploaded_file)
    time_col = None
    for c in df_raw.columns:
        if c.lower() in ['time','timestamp','fecha','tiempo','datetime']:
            time_col = c
            break
    if time_col:
        df_raw[time_col] = pd.to_datetime(df_raw[time_col], utc=True, errors='coerce')
        df_raw = df_raw.set_index(time_col)
        df_raw.index = df_raw.index.tz_convert('America/Bogota')
        df_raw.index.name = 'tiempo'
    campos_disponibles = [c for c in TODOS_CAMPOS if c in df_raw.columns]
    if not campos_disponibles:
        campos_disponibles = list(df_raw.select_dtypes(include='number').columns)
    df = df_raw[campos_disponibles].copy()
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df[~df.isin([np.inf, -np.inf])].dropna(how='all')
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.resample('1min').mean().dropna(how='all')
except Exception as e:
    st.error(f"❌ Error al procesar el CSV: {e}")
    st.stop()

accel_cols = [c for c in CAMPOS_ACCEL if c in df.columns]
gyro_cols  = [c for c in CAMPOS_GYRO  if c in df.columns]

if accel_cols:
    mag = np.sqrt(sum(df[c]**2 for c in accel_cols))
    mag_mean = mag.mean()
else:
    mag = None; mag_mean = 0

cols_top = st.columns(4)
with cols_top[0]: st.metric("📋 Registros", f"{len(df):,}")
with cols_top[1]: st.metric("📐 Ejes detectados", len(campos_disponibles))
with cols_top[2]:
    if mag is not None:
        st.metric("⚡ Magnitud media", f"{mag_mean:.3f} m/s²", delta=f"±{mag.std():.3f}")
with cols_top[3]:
    if mag is not None:
        z = (mag - mag.mean()) / mag.std() if mag.std() > 0 else mag*0
        n_anom = (z.abs() > umbral_z).sum()
        st.metric("⚠️ Anomalías", int(n_anom))

st.markdown("---")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📈 Series de Tiempo", "📊 Estadísticas", "⚠️ Anomalías Z-score",
    "🎯 Nivel de Actividad", "🔗 Correlación", "🗺️ Ubicación",
])

with tab1:
    st.subheader("📈 Series de Tiempo")
    col_sel, col_tipo = st.columns([2,1])
    with col_sel:
        campo_sel = st.selectbox("Seleccionar eje", campos_disponibles,
                                  format_func=lambda x: f"{x}  ({UNIDADES.get(x,'')})")
    with col_tipo:
        tipo_graf = st.selectbox("Tipo de gráfico", ["Línea","Área","Barras"])
    serie  = df[campo_sel].dropna()
    color  = COLORES_EJES.get(campo_sel, '#00d4ff')
    unidad = UNIDADES.get(campo_sel, '')
    fig = go.Figure()
    if tipo_graf == "Línea":
        fig.add_trace(go.Scatter(x=serie.index, y=serie.values, mode='lines',
            name=campo_sel, line=dict(color=color, width=2)))
    elif tipo_graf == "Área":
        fig.add_trace(go.Scatter(x=serie.index, y=serie.values, fill='tozeroy',
            mode='lines', name=campo_sel, line=dict(color=color, width=2)))
    else:
        fig.add_trace(go.Bar(x=serie.index, y=serie.values,
            name=campo_sel, marker_color=color))
    mm = serie.rolling(window=ventana_mm, center=True).mean()
    fig.add_trace(go.Scatter(x=mm.index, y=mm.values, mode='lines',
        name=f'MM {ventana_mm} min', line=dict(color='#ffffff', width=1.5, dash='dash')))
    fig.add_hline(y=serie.mean(), line_dash='dot', line_color='#8892b0',
                  annotation_text=f"Media: {serie.mean():.3f} {unidad}")
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,20,40,0.6)', font=dict(family='Space Mono', color='#8892b0'),
        xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f'),
        height=420, margin=dict(t=30,b=40), legend=dict(bgcolor='rgba(0,0,0,0)'))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("#### Todos los ejes")
    for campos_g, titulo_g in [(accel_cols,'Acelerómetro (m/s²)'),(gyro_cols,'Giroscopio (rad/s)')]:
        if not campos_g: continue
        fig2 = go.Figure()
        for c in campos_g:
            s = df[c].dropna()
            fig2.add_trace(go.Scatter(x=s.index, y=s.values, mode='lines',
                name=c, line=dict(color=COLORES_EJES.get(c,'#fff'), width=1.8)))
        fig2.update_layout(title=titulo_g, template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(10,20,40,0.6)',
            font=dict(family='Space Mono', color='#8892b0'),
            xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f'),
            height=300, margin=dict(t=40,b=30), legend=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig2, use_container_width=True)
    if st.checkbox("Mostrar datos crudos"):
        st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("📊 Estadísticas descriptivas")
    st.dataframe(df.describe().round(4), use_container_width=True)
    st.markdown("#### Estadísticos adicionales")
    adicionales = pd.DataFrame({
        'rango'    : (df.max()-df.min()).round(4),
        'IQR'      : (df.quantile(0.75)-df.quantile(0.25)).round(4),
        'varianza' : df.var().round(4),
        'asimetría': df.skew().round(4),
        'curtosis' : df.kurt().round(4),
    })
    st.dataframe(adicionales, use_container_width=True)
    st.markdown("#### Métricas por eje")
    cols_m = st.columns(min(3, len(campos_disponibles)))
    for i, campo in enumerate(campos_disponibles):
        s = df[campo].dropna()
        with cols_m[i % 3]:
            st.metric(f"{campo} ({UNIDADES.get(campo,'')})", f"{s.mean():.4f}", delta=f"std ±{s.std():.4f}")
    st.markdown("#### Distribuciones")
    n = len(campos_disponibles)
    fig_hist = make_subplots(rows=(n+2)//3, cols=3, subplot_titles=campos_disponibles)
    for i, campo in enumerate(campos_disponibles):
        r, c = divmod(i, 3)
        s = df[campo].dropna()
        fig_hist.add_trace(go.Histogram(x=s.values, name=campo, nbinsx=20,
            marker_color=COLORES_EJES.get(campo,'#00d4ff'), opacity=0.75), row=r+1, col=c+1)
    fig_hist.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,20,40,0.6)', showlegend=False,
        font=dict(family='Space Mono', color='#8892b0'), height=300*((n+2)//3))
    st.plotly_chart(fig_hist, use_container_width=True)

with tab3:
    st.subheader(f"⚠️ Anomalías Z-score (umbral = {umbral_z})")
    campo_z = st.selectbox("Seleccionar eje", campos_disponibles, key='campo_z',
                            format_func=lambda x: f"{x}  ({UNIDADES.get(x,'')})")
    serie_z = df[campo_z].dropna()
    serie_z = serie_z[~serie_z.isin([np.inf, -np.inf])]
    if serie_z.std() == 0:
        st.warning("Sin variación en este campo.")
    else:
        z_scores  = (serie_z - serie_z.mean()) / serie_z.std()
        anomalias = serie_z[z_scores.abs() > umbral_z]
        lim_sup   = serie_z.mean() + umbral_z*serie_z.std()
        lim_inf   = serie_z.mean() - umbral_z*serie_z.std()
        color_z   = COLORES_EJES.get(campo_z, '#00d4ff')
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Total registros", len(serie_z))
        col_b.metric("⚠️ Anomalías", len(anomalias))
        col_c.metric("% anomalías", f"{len(anomalias)/len(serie_z)*100:.1f}%")
        fig_z = go.Figure()
        fig_z.add_trace(go.Scatter(x=serie_z.index, y=serie_z.values, mode='lines',
            name='Señal', line=dict(color=color_z, width=1.8)))
        fig_z.add_trace(go.Scatter(x=anomalias.index, y=anomalias.values, mode='markers',
            name=f'Anomalías ({len(anomalias)})',
            marker=dict(color='#ffd93d', size=10, line=dict(color='#ff6b6b', width=2))))
        fig_z.add_hline(y=lim_sup, line_dash='dot', line_color='#ff6b6b', annotation_text=f"+{umbral_z}σ")
        fig_z.add_hline(y=lim_inf, line_dash='dot', line_color='#ff6b6b', annotation_text=f"-{umbral_z}σ")
        fig_z.add_hrect(y0=lim_inf, y1=lim_sup, fillcolor=color_z, opacity=0.06, layer='below', line_width=0)
        fig_z.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,20,40,0.6)', font=dict(family='Space Mono', color='#8892b0'),
            xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f'),
            height=400, legend=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig_z, use_container_width=True)
        if len(anomalias) > 0:
            st.markdown("#### Detalle de anomalías")
            df_anom = pd.DataFrame({
                'tiempo' : anomalias.index, 'valor': anomalias.values.round(4),
                'z_score': z_scores[anomalias.index].round(3),
                'tipo'   : ['⬆️ Alto' if v > lim_sup else '⬇️ Bajo' for v in anomalias.values],
            })
            st.dataframe(df_anom, use_container_width=True)
        else:
            st.success("✅ No se detectaron anomalías.")

with tab4:
    st.subheader("🎯 Nivel de Actividad")
    if not accel_cols:
        st.warning("No se encontraron columnas accel_x/y/z.")
    else:
        mag_serie = np.sqrt(sum(df[c]**2 for c in accel_cols)).dropna()
        condiciones = [mag_serie < 2, (mag_serie>=2)&(mag_serie<6),
                       (mag_serie>=6)&(mag_serie<12), mag_serie>=12]
        etiquetas  = ['😴 Reposo','🚶 Leve','🏃 Moderado','⚡ Intenso']
        colores_act= ['#00d4ff','#00ff88','#ffd93d','#ff6b6b']
        df_act  = pd.Series(np.select(condiciones, etiquetas, default='😴 Reposo'),
                            index=mag_serie.index)
        conteo  = df_act.value_counts()
        col_pie, col_bar = st.columns(2)
        with col_pie:
            fig_pie = go.Figure(go.Pie(labels=conteo.index, values=conteo.values, hole=0.45,
                marker=dict(colors=colores_act[:len(conteo)], line=dict(color='#0a0e1a', width=3)),
                textfont=dict(family='Space Mono', size=12)))
            fig_pie.update_layout(title='Distribución de actividad', template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Space Mono', color='#8892b0'),
                legend=dict(bgcolor='rgba(0,0,0,0)'), height=360)
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_bar:
            fig_bar = go.Figure(go.Bar(x=conteo.index, y=conteo.values,
                marker=dict(color=colores_act[:len(conteo)], line=dict(color='#0a0e1a', width=1)),
                text=[f'{v/len(df_act)*100:.1f}%' for v in conteo.values], textposition='outside'))
            fig_bar.update_layout(title='Frecuencia por nivel', template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(10,20,40,0.6)',
                font=dict(family='Space Mono', color='#8892b0'),
                yaxis=dict(gridcolor='#1e3a5f'), height=360)
            st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown("#### Magnitud en el tiempo")
        fig_mag = go.Figure()
        fig_mag.add_trace(go.Scatter(x=mag_serie.index, y=mag_serie.values, mode='lines',
            fill='tozeroy', name='Magnitud', line=dict(color='#00d4ff', width=2),
            fillcolor='rgba(0,212,255,0.1)'))
        for val, label, col in zip([2,6,12],['Reposo→Leve','Leve→Moderado','Moderado→Intenso'],
                                    ['#00ff88','#ffd93d','#ff6b6b']):
            fig_mag.add_hline(y=val, line_dash='dash', line_color=col,
                              annotation_text=label, annotation_font_color=col)
        fig_mag.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(10,20,40,0.6)', font=dict(family='Space Mono', color='#8892b0'),
            xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f', title='Magnitud (m/s²)'),
            height=320, legend=dict(bgcolor='rgba(0,0,0,0)'))
        st.plotly_chart(fig_mag, use_container_width=True)
        c1,c2,c3 = st.columns(3)
        c1.metric("⚡ Magnitud máxima", f"{mag_serie.max():.3f} m/s²")
        c2.metric("📊 Magnitud media",  f"{mag_serie.mean():.3f} m/s²")
        c3.metric("📉 Magnitud mínima", f"{mag_serie.min():.3f} m/s²")

with tab5:
    st.subheader("🔗 Correlación")
    if len(campos_disponibles) < 2:
        st.warning("Se necesitan al menos 2 columnas.")
    else:
        corr = df[campos_disponibles].corr().round(3)
        fig_heat = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.index,
            colorscale='RdBu_r', zmid=0, zmin=-1, zmax=1,
            text=corr.values.round(2), texttemplate='%{text}',
            textfont=dict(family='Space Mono', size=12)))
        fig_heat.update_layout(title='Matriz de Correlación de Pearson', template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(10,20,40,0.6)',
            font=dict(family='Space Mono', color='#8892b0'), height=420)
        st.plotly_chart(fig_heat, use_container_width=True)
        st.markdown("#### Dispersión entre dos ejes")
        col_x, col_y = st.columns(2)
        with col_x: eje_x = st.selectbox("Eje X", campos_disponibles, index=0, key='eje_x')
        with col_y: eje_y = st.selectbox("Eje Y", campos_disponibles, index=min(1,len(campos_disponibles)-1), key='eje_y')
        if eje_x != eje_y:
            r_val = df[eje_x].corr(df[eje_y])
            fig_sc = px.scatter(df, x=eje_x, y=eje_y, trendline='ols',
                trendline_color_override='#ffd93d',
                color_discrete_sequence=[COLORES_EJES.get(eje_x,'#00d4ff')],
                opacity=0.6, title=f'{eje_x} vs {eje_y} — r = {r_val:.3f}')
            fig_sc.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(10,20,40,0.6)', font=dict(family='Space Mono', color='#8892b0'),
                xaxis=dict(gridcolor='#1e3a5f'), yaxis=dict(gridcolor='#1e3a5f'), height=380)
            st.plotly_chart(fig_sc, use_container_width=True)
            nivel = "fuerte" if abs(r_val)>0.7 else "moderada" if abs(r_val)>0.3 else "débil o nula"
            emoji_r = "🔴" if r_val<0 and abs(r_val)>0.7 else "🟢" if abs(r_val)>0.7 else "🟡" if abs(r_val)>0.3 else "⚪"
            st.info(f"{emoji_r} Correlación **{'negativa' if r_val<0 else 'positiva'} {nivel}** (r = {r_val:.3f})")

with tab6:
    st.subheader("🗺️ Ubicación del Sensor")
    col_map, col_info = st.columns([2,1])
    with col_map:
        st.map(pd.DataFrame({'lat':[6.2006],'lon':[-75.5783]}), zoom=16)
    with col_info:
        st.markdown("""
        <div class='sensor-card'>
            <h4 style='color:#64ffda;font-family:Space Mono,monospace;margin-top:0'>📍 Detalles</h4>
            <p style='color:#8892b0;font-family:Space Mono,monospace;font-size:0.82rem'>
            🏫 <b style='color:#ccd6f6'>Universidad EAFIT</b><br><br>
            📌 Lat: 6.2006°N<br>📌 Lon: 75.5783°W<br>🏔️ Alt: ~1,495 m.s.n.m<br><br>
            🔧 <b style='color:#ccd6f6'>Hardware</b><br>
            • ESP32<br>• MPU6050<br>• I²C SDA=21, SCL=22<br><br>
            📡 <b style='color:#ccd6f6'>Datos</b><br>
            • Frecuencia: 2 seg<br>• InfluxDB Cloud<br>• Bucket: CATAYDAVIDFINAL
            </p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<p style='text-align:center;color:#8892b0;font-family:Space Mono,monospace;font-size:0.75rem'>
    🤖 MPU6050 Dashboard IoT · Universidad EAFIT · Medellín 2025
</p>
""", unsafe_allow_html=True)

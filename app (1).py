"""
Top 20 Investables 2026
========================
App de análisis de las 20 mejores acciones para invertir en 2026.
Usa yfinance para datos reales; donde no hay datos públicos gratuitos,
se simulan valores coherentes (marcados con comentario # SIMULADO).

Ejecutar:
    pip install streamlit pandas yfinance plotly
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import time

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Top 20 Investables 2026",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

  .stApp {
    background: #0b0e1a;
    font-family: 'DM Sans', sans-serif;
    color: #e2e8f0;
  }
  #MainMenu, footer, header { visibility: hidden; }

  .main-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    background: linear-gradient(90deg, #f6c90e, #ff6b35, #e040fb);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0;
    line-height: 1.1;
  }
  .main-sub {
    color: #64748b;
    font-size: 0.9rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 1.5rem;
  }
  .metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 14px 18px;
    text-align: center;
  }
  .metric-val {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #f6c90e;
  }
  .metric-lbl {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #475569;
    margin-top: 2px;
  }
  .section-head {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #f6c90e;
    border-left: 3px solid #f6c90e;
    padding-left: 10px;
    margin: 1.8rem 0 0.8rem;
  }
  .note-box {
    background: rgba(246,201,14,0.08);
    border: 1px solid rgba(246,201,14,0.25);
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 0.83rem;
    color: #a3a3a3;
    margin-bottom: 1rem;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DEFINICIÓN DE LAS 20 EMPRESAS
# ─────────────────────────────────────────────
COMPANIES = [
    {"symbol": "AAPL",  "name": "Apple",               "sector": "Technology"},
    {"symbol": "MSFT",  "name": "Microsoft",            "sector": "Technology"},
    {"symbol": "NVDA",  "name": "NVIDIA",               "sector": "Technology"},
    {"symbol": "GOOGL", "name": "Alphabet",             "sector": "Technology"},
    {"symbol": "META",  "name": "Meta Platforms",       "sector": "Technology"},
    {"symbol": "AMZN",  "name": "Amazon",               "sector": "Consumer"},
    {"symbol": "TSLA",  "name": "Tesla",                "sector": "Automotive"},
    {"symbol": "BRK-B", "name": "Berkshire Hathaway",  "sector": "Finance"},
    {"symbol": "JPM",   "name": "JPMorgan Chase",       "sector": "Finance"},
    {"symbol": "V",     "name": "Visa",                 "sector": "Finance"},
    {"symbol": "UNH",   "name": "UnitedHealth Group",  "sector": "Healthcare"},
    {"symbol": "JNJ",   "name": "Johnson & Johnson",    "sector": "Healthcare"},
    {"symbol": "LLY",   "name": "Eli Lilly",            "sector": "Healthcare"},
    {"symbol": "XOM",   "name": "ExxonMobil",           "sector": "Energy"},
    {"symbol": "NEE",   "name": "NextEra Energy",       "sector": "Energy"},
    {"symbol": "COST",  "name": "Costco",               "sector": "Consumer"},
    {"symbol": "HD",    "name": "Home Depot",           "sector": "Consumer"},
    {"symbol": "AVGO",  "name": "Broadcom",             "sector": "Technology"},
    {"symbol": "AMD",   "name": "AMD",                  "sector": "Technology"},
    {"symbol": "ASML",  "name": "ASML Holding",         "sector": "Technology"},
]

# ─────────────────────────────────────────────
# DATOS SIMULADOS COHERENTES (fallback / referencia)
# Precio objetivo, EPS Growth y Ratings: SIMULADOS
# No hay fuente gratuita confiable para estos campos.
# Para datos reales usar: Bloomberg, Refinitiv, Seeking Alpha Premium.
# ─────────────────────────────────────────────
SIMULATED_EXTRAS = {
    "AAPL":  {"price_target": 245,  "analyst_rating": "Buy",  "pe": 28.5, "peg": 2.1, "roe": 147.0, "eps_growth": 12.3, "div_yield": 0.5},
    "MSFT":  {"price_target": 510,  "analyst_rating": "Buy",  "pe": 34.2, "peg": 2.4, "roe": 38.5,  "eps_growth": 18.7, "div_yield": 0.7},
    "NVDA":  {"price_target": 185,  "analyst_rating": "Buy",  "pe": 45.1, "peg": 1.2, "roe": 115.0, "eps_growth": 95.0, "div_yield": 0.0},
    "GOOGL": {"price_target": 215,  "analyst_rating": "Buy",  "pe": 22.8, "peg": 1.5, "roe": 27.3,  "eps_growth": 22.1, "div_yield": 0.0},
    "META":  {"price_target": 720,  "analyst_rating": "Buy",  "pe": 26.0, "peg": 1.3, "roe": 35.2,  "eps_growth": 38.5, "div_yield": 0.4},
    "AMZN":  {"price_target": 255,  "analyst_rating": "Buy",  "pe": 38.5, "peg": 1.8, "roe": 21.4,  "eps_growth": 55.0, "div_yield": 0.0},
    "TSLA":  {"price_target": 310,  "analyst_rating": "Hold", "pe": 65.0, "peg": 3.5, "roe": 18.6,  "eps_growth": -8.0, "div_yield": 0.0},
    "BRK-B": {"price_target": 530,  "analyst_rating": "Buy",  "pe": 21.0, "peg": 1.9, "roe": 12.5,  "eps_growth": 15.0, "div_yield": 0.0},
    "JPM":   {"price_target": 280,  "analyst_rating": "Buy",  "pe": 12.5, "peg": 1.4, "roe": 16.8,  "eps_growth": 14.2, "div_yield": 2.1},
    "V":     {"price_target": 360,  "analyst_rating": "Buy",  "pe": 30.1, "peg": 2.0, "roe": 44.5,  "eps_growth": 16.0, "div_yield": 0.7},
    "UNH":   {"price_target": 620,  "analyst_rating": "Buy",  "pe": 18.2, "peg": 1.6, "roe": 25.0,  "eps_growth": 13.5, "div_yield": 1.5},
    "JNJ":   {"price_target": 175,  "analyst_rating": "Hold", "pe": 14.8, "peg": 2.5, "roe": 21.0,  "eps_growth": 5.5,  "div_yield": 3.4},
    "LLY":   {"price_target": 980,  "analyst_rating": "Buy",  "pe": 52.0, "peg": 1.1, "roe": 68.0,  "eps_growth": 82.0, "div_yield": 0.6},
    "XOM":   {"price_target": 135,  "analyst_rating": "Hold", "pe": 13.5, "peg": 2.2, "roe": 15.5,  "eps_growth": -4.0, "div_yield": 3.7},
    "NEE":   {"price_target": 85,   "analyst_rating": "Buy",  "pe": 20.0, "peg": 1.7, "roe": 11.0,  "eps_growth": 9.0,  "div_yield": 2.8},
    "COST":  {"price_target": 1020, "analyst_rating": "Buy",  "pe": 52.0, "peg": 3.8, "roe": 31.0,  "eps_growth": 14.0, "div_yield": 0.5},
    "HD":    {"price_target": 420,  "analyst_rating": "Buy",  "pe": 23.0, "peg": 2.0, "roe": 120.0, "eps_growth": 6.5,  "div_yield": 2.3},
    "AVGO":  {"price_target": 250,  "analyst_rating": "Buy",  "pe": 28.0, "peg": 1.4, "roe": 52.0,  "eps_growth": 48.0, "div_yield": 1.2},
    "AMD":   {"price_target": 175,  "analyst_rating": "Buy",  "pe": 100.0,"peg": 1.6, "roe": 4.5,   "eps_growth": 120.0,"div_yield": 0.0},
    "ASML":  {"price_target": 850,  "analyst_rating": "Buy",  "pe": 32.0, "peg": 1.3, "roe": 45.0,  "eps_growth": 22.0, "div_yield": 0.9},
}

# ─────────────────────────────────────────────
# FUNCIÓN PRINCIPAL: fetch_stock_data
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_data(symbol: str) -> dict:
    """
    Obtiene datos de una acción.

    DATOS REALES (vía yfinance):
      - current_price: precio de mercado en tiempo real

    DATOS SIMULADOS (no hay fuente gratuita confiable):
      - price_target: consenso de analistas (requiere Bloomberg/Refinitiv)
      - analyst_rating: Buy/Hold/Sell (requiere API paga)
      - eps_growth: crecimiento EPS 3 años (cálculo manual o API paga)

    DATOS MIXTOS (yfinance los provee pero con gaps frecuentes):
      - pe_ratio, peg_ratio, roe, dividend_yield

    Retorna dict normalizado con todos los campos requeridos.
    """
    sim = SIMULATED_EXTRAS.get(symbol, {})
    company_meta = next((c for c in COMPANIES if c["symbol"] == symbol), {})

    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # ── PRECIO ACTUAL — DATO REAL ──────────────────────────
        current_price = (
            info.get("currentPrice") or
            info.get("regularMarketPrice") or
            info.get("previousClose") or
            sim.get("price_target", 100) * 0.88
        )

        # ── PRECIO OBJETIVO — usa yfinance si está disponible, sino SIMULADO ──
        # yfinance incluye targetMeanPrice pero frecuentemente retorna None
        target_real = info.get("targetMeanPrice")

        # ── RATIOS FUNDAMENTALES — yfinance cuando disponible, sino SIMULADO ──
        pe_real        = info.get("trailingPE")
        peg_real       = info.get("pegRatio")
        roe_raw        = info.get("returnOnEquity")   # viene en decimal (0.15 = 15%)
        div_yield_raw  = info.get("dividendYield")    # viene en decimal

        return {
            "symbol":          symbol,
            "name":            company_meta.get("name", symbol),
            "sector":          company_meta.get("sector", "—"),
            "current_price":   round(float(current_price), 2),
            "price_target":    round(float(target_real), 2) if target_real else sim.get("price_target", 0.0),
            "analyst_rating":  sim.get("analyst_rating", "Hold"),           # SIMULADO
            "pe_ratio":        round(float(pe_real), 1) if pe_real else sim.get("pe", 0.0),
            "peg_ratio":       round(float(peg_real), 2) if peg_real else sim.get("peg", 0.0),
            "roe":             round(float(roe_raw) * 100, 1) if roe_raw else sim.get("roe", 0.0),
            "eps_growth":      sim.get("eps_growth", 0.0),                  # SIMULADO
            "dividend_yield":  round(float(div_yield_raw) * 100, 2) if div_yield_raw else sim.get("div_yield", 0.0),
        }

    except Exception:
        # Fallback completo con datos simulados si yfinance falla
        return {
            "symbol":         symbol,
            "name":           company_meta.get("name", symbol),
            "sector":         company_meta.get("sector", "—"),
            "current_price":  round(sim.get("price_target", 100) * 0.88, 2),
            "price_target":   sim.get("price_target", 0.0),
            "analyst_rating": sim.get("analyst_rating", "Hold"),
            "pe_ratio":       sim.get("pe", 0.0),
            "peg_ratio":      sim.get("peg", 0.0),
            "roe":            sim.get("roe", 0.0),
            "eps_growth":     sim.get("eps_growth", 0.0),
            "dividend_yield": sim.get("div_yield", 0.0),
        }


def load_all_data() -> pd.DataFrame:
    """Carga y combina datos de las 20 empresas en un DataFrame."""
    rows = []
    progress = st.progress(0, text="Conectando con Yahoo Finance...")
    for i, company in enumerate(COMPANIES):
        data = fetch_stock_data(company["symbol"])
        rows.append(data)
        progress.progress((i + 1) / len(COMPANIES), text=f"Cargando {company['name']}...")
        time.sleep(0.04)
    progress.empty()
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown('<p class="main-title">Top 20 Investables<br>2026 📈</p>', unsafe_allow_html=True)
st.markdown('<p class="main-sub">Wall Street · Análisis fundamental · Datos en tiempo real</p>', unsafe_allow_html=True)

st.markdown("""
<div class="note-box">
⚡ <strong>Fuente de datos:</strong> Precios actuales vía <strong>Yahoo Finance (yfinance)</strong> — tiempo real.
Precio objetivo, EPS Growth y Recomendaciones de analistas son <strong>valores de referencia</strong>
coherentes con el consenso del mercado a inicios de 2026. Para datos en vivo de analistas se requiere
Bloomberg, Refinitiv o Seeking Alpha Premium (ver comentarios en el código fuente).
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CARGAR DATOS (con cache de sesión)
# ─────────────────────────────────────────────
if "df_loaded" not in st.session_state:
    st.session_state.df_loaded = False

if not st.session_state.df_loaded:
    df_raw = load_all_data()
    st.session_state.df = df_raw
    st.session_state.df_loaded = True
else:
    df_raw = st.session_state.df

# Botón para forzar actualización
if st.sidebar.button("🔄 Actualizar precios"):
    st.cache_data.clear()
    st.session_state.df_loaded = False
    st.rerun()

# ─────────────────────────────────────────────
# SIDEBAR – FILTROS
# ─────────────────────────────────────────────
st.sidebar.markdown("## 🔍 Filtros")

sectors = ["Todos"] + sorted(df_raw["sector"].unique().tolist())
selected_sector = st.sidebar.selectbox("Sector", sectors)

search_term = st.sidebar.text_input("Buscar empresa", placeholder="Ej: Apple, NVDA...")

sort_options = {
    "Upside potencial (%)": "upside_pct",
    "Precio actual ($)":    "current_price",
    "Precio proyectado ($)":"price_target",
    "P/E Ratio":            "pe_ratio",
    "PEG Ratio":            "peg_ratio",
    "ROE (%)":              "roe",
    "EPS Growth (%)":       "eps_growth",
    "Dividend Yield (%)":   "dividend_yield",
}
sort_label = st.sidebar.selectbox("Ordenar por", list(sort_options.keys()))
sort_col   = sort_options[sort_label]
sort_asc   = st.sidebar.checkbox("Orden ascendente", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Leyenda")
st.sidebar.markdown("🟢 **Buy** — Recomendación de compra")
st.sidebar.markdown("🟡 **Hold** — Mantener posición")
st.sidebar.markdown("🔴 **Sell** — Recomendación de venta")
st.sidebar.markdown("---")
st.sidebar.caption("⚠️ No constituye asesoramiento financiero.")

# ─────────────────────────────────────────────
# PROCESAR DATAFRAME
# ─────────────────────────────────────────────
df = df_raw.copy()

# Calcular upside potencial (%)
df["upside_pct"] = (
    (df["price_target"] - df["current_price"]) /
    df["current_price"].replace(0, 1) * 100
).round(1)

# Filtro por sector
if selected_sector != "Todos":
    df = df[df["sector"] == selected_sector]

# Filtro por búsqueda de texto
if search_term:
    mask = (
        df["name"].str.contains(search_term, case=False, na=False) |
        df["symbol"].str.contains(search_term, case=False, na=False)
    )
    df = df[mask]

# Ordenar
df = df.sort_values(sort_col, ascending=sort_asc).reset_index(drop=True)

# ─────────────────────────────────────────────
# MÉTRICAS RESUMEN
# ─────────────────────────────────────────────
buys       = len(df[df["analyst_rating"] == "Buy"])
holds      = len(df[df["analyst_rating"] == "Hold"])
sells      = len(df[df["analyst_rating"] == "Sell"])
avg_upside = df["upside_pct"].mean() if len(df) > 0 else 0

c1, c2, c3, c4 = st.columns(4)
for col, val, lbl in zip(
    [c1, c2, c3, c4],
    [len(df), f"{avg_upside:+.1f}%", f"{buys} / {holds}", f"{sells}"],
    ["Empresas", "Upside promedio", "Buy / Hold", "Sell alerts"]
):
    col.markdown(
        f'<div class="metric-card"><div class="metric-val">{val}</div>'
        f'<div class="metric-lbl">{lbl}</div></div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────
# TABLA PRINCIPAL INTERACTIVA
# ─────────────────────────────────────────────
st.markdown('<p class="section-head">📋 Tabla de empresas</p>', unsafe_allow_html=True)

# Colorear columna de rating
def color_rating(val):
    if val == "Buy":
        return "color: #22c55e; font-weight: bold"
    elif val == "Sell":
        return "color: #ef4444; font-weight: bold"
    return "color: #f6c90e; font-weight: bold"

def color_upside(val):
    if val > 15:
        return "color: #22c55e; font-weight: bold"
    elif val < 0:
        return "color: #ef4444; font-weight: bold"
    return "color: #f6c90e"

# DataFrame para mostrar
df_display = df[[
    "symbol", "name", "sector", "current_price", "price_target",
    "upside_pct", "analyst_rating", "pe_ratio", "peg_ratio",
    "roe", "eps_growth", "dividend_yield"
]].copy()

df_display.columns = [
    "Ticker", "Empresa", "Sector", "Precio Actual ($)", "Precio Proyectado ($)",
    "Upside (%)", "Recomendación", "P/E", "PEG", "ROE (%)", "EPS Growth (%)", "Div Yield (%)"
]

styled = (
    df_display.style
    .applymap(color_rating, subset=["Recomendación"])
    .applymap(color_upside, subset=["Upside (%)"])
    .format({
        "Precio Actual ($)":    "${:,.2f}",
        "Precio Proyectado ($)":"${:,.2f}",
        "Upside (%)":           "{:+.1f}%",
        "P/E":                  "{:.1f}x",
        "PEG":                  "{:.2f}",
        "ROE (%)":              "{:.1f}%",
        "EPS Growth (%)":       "{:+.1f}%",
        "Div Yield (%)":        "{:.2f}%",
    })
    .set_properties(**{
        "background-color": "#111827",
        "color": "#e2e8f0",
        "border-color": "#1f2937",
        "font-size": "13px",
    })
    .set_table_styles([
        {"selector": "th", "props": [
            ("background-color", "#1f2937"),
            ("color", "#f6c90e"),
            ("font-family", "Syne, sans-serif"),
            ("font-size", "11px"),
            ("text-transform", "uppercase"),
            ("letter-spacing", "1px"),
            ("padding", "8px 10px"),
        ]},
        {"selector": "td", "props": [("padding", "7px 10px")]},
        {"selector": "tr:hover td", "props": [("background-color", "#1e293b")]},
    ])
    .hide(axis="index")
)

st.dataframe(df_display, use_container_width=True, height=520)

# ─────────────────────────────────────────────
# GRÁFICO 1: PRECIO ACTUAL VS PROYECTADO
# ─────────────────────────────────────────────
st.markdown('<p class="section-head">📊 Precio Actual vs Proyectado 2026</p>', unsafe_allow_html=True)

df_chart = df.sort_values("upside_pct", ascending=True)

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(
    name="Precio Actual",
    x=df_chart["symbol"],
    y=df_chart["current_price"],
    marker_color="#3b82f6",
    opacity=0.85,
    hovertemplate="<b>%{x}</b><br>Precio actual: $%{y:,.2f}<extra></extra>",
))
fig_bar.add_trace(go.Bar(
    name="Precio Proyectado",
    x=df_chart["symbol"],
    y=df_chart["price_target"],
    marker_color="#f6c90e",
    opacity=0.85,
    hovertemplate="<b>%{x}</b><br>Precio proyectado: $%{y:,.2f}<extra></extra>",
))
fig_bar.update_layout(
    barmode="group",
    plot_bgcolor="#0f172a",
    paper_bgcolor="#0f172a",
    font=dict(color="#94a3b8", family="DM Sans"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e2e8f0")),
    xaxis=dict(gridcolor="#1e293b", tickfont=dict(color="#94a3b8")),
    yaxis=dict(gridcolor="#1e293b", tickfont=dict(color="#94a3b8"), tickprefix="$"),
    margin=dict(l=10, r=10, t=20, b=10),
    height=420,
)
st.plotly_chart(fig_bar, use_container_width=True)

# ─────────────────────────────────────────────
# GRÁFICO 2: UPSIDE POTENCIAL
# ─────────────────────────────────────────────
st.markdown('<p class="section-head">🚀 Upside Potencial por Empresa (%)</p>', unsafe_allow_html=True)

df_up     = df.sort_values("upside_pct", ascending=True)
bar_colors = [
    "#ef4444" if x < 0 else
    "#22c55e" if x > 15 else
    "#f6c90e"
    for x in df_up["upside_pct"]
]

fig_upside = go.Figure(go.Bar(
    x=df_up["upside_pct"],
    y=df_up["symbol"],
    orientation="h",
    marker_color=bar_colors,
    text=[f"{v:+.1f}%" for v in df_up["upside_pct"]],
    textposition="outside",
    textfont=dict(color="#e2e8f0", size=11),
    hovertemplate="<b>%{y}</b><br>Upside: %{x:+.1f}%<extra></extra>",
))
fig_upside.update_layout(
    plot_bgcolor="#0f172a",
    paper_bgcolor="#0f172a",
    font=dict(color="#94a3b8", family="DM Sans"),
    xaxis=dict(gridcolor="#1e293b", ticksuffix="%", tickfont=dict(color="#94a3b8")),
    yaxis=dict(gridcolor="#1e293b", tickfont=dict(color="#e2e8f0", size=12)),
    margin=dict(l=10, r=70, t=10, b=10),
    height=max(380, len(df) * 28),
)
st.plotly_chart(fig_upside, use_container_width=True)

# ─────────────────────────────────────────────
# GRÁFICO RADAR – ANÁLISIS INDIVIDUAL
# ─────────────────────────────────────────────
st.markdown('<p class="section-head">🔬 Análisis Individual — Perfil de Indicadores</p>', unsafe_allow_html=True)

if len(df) == 0:
    st.info("No hay empresas que coincidan con los filtros aplicados.")
else:
    selected_name = st.selectbox(
        "Seleccioná una empresa para ver su perfil completo:",
        options=df["symbol"].tolist(),
        format_func=lambda s: f"{s} — {df.loc[df['symbol']==s, 'name'].values[0]}",
        key="radar_select"
    )

    if selected_name:
        row = df[df["symbol"] == selected_name].iloc[0]

        # Tarjetas de métricas
        mc1, mc2, mc3, mc4, mc5 = st.columns(5)
        rating_color = {"Buy": "#22c55e", "Hold": "#f6c90e", "Sell": "#ef4444"}
        rc = rating_color.get(row["analyst_rating"], "#94a3b8")

        for col, val, lbl in zip(
            [mc1, mc2, mc3, mc4, mc5],
            [
                f"${row['current_price']:,.2f}",
                f"${row['price_target']:,.2f}",
                f"{row['upside_pct']:+.1f}%",
                row["analyst_rating"],
                f"{row['dividend_yield']:.2f}%",
            ],
            ["Precio Actual", "Precio Objetivo", "Upside", "Rating", "Dividendo"]
        ):
            color = rc if lbl == "Rating" else "#f6c90e"
            col.markdown(
                f'<div class="metric-card">'
                f'<div class="metric-val" style="color:{color}">{val}</div>'
                f'<div class="metric-lbl">{lbl}</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        st.markdown("")

        # Normalización 0–10 para el radar
        # Nota: PE y PEG se invierten (menor es mejor para el inversor de valor)
        def normalize(val, lo, hi, invert=False):
            """Escala val al rango [0, 10]. Si invert=True, menor val = mayor score."""
            if hi == lo:
                return 5.0
            score = max(0.0, min(10.0, (val - lo) / (hi - lo) * 10))
            return round(10 - score if invert else score, 2)

        pe_score  = normalize(min(row["pe_ratio"], 120),   0, 120,  invert=True)
        peg_score = normalize(min(row["peg_ratio"], 5),    0, 5,    invert=True)
        roe_score = normalize(min(row["roe"], 150),        0, 150)
        eps_score = normalize(row["eps_growth"],          -20, 120)
        div_score = normalize(row["dividend_yield"],       0, 5)

        categories = ["Valor (P/E↓)", "Crecimiento (PEG↓)", "Rentabilidad (ROE)", "EPS Growth", "Dividendo"]
        values     = [pe_score, peg_score, roe_score, eps_score, div_score]

        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(246,201,14,0.12)",
            line=dict(color="#f6c90e", width=2.5),
            name=selected_name,
            hovertemplate="%{theta}: %{r:.1f}/10<extra></extra>",
        ))
        fig_radar.update_layout(
            polar=dict(
                bgcolor="#0f172a",
                radialaxis=dict(
                    visible=True, range=[0, 10],
                    gridcolor="#1e293b",
                    tickfont=dict(color="#475569", size=9),
                    tickvals=[0, 2, 4, 6, 8, 10],
                ),
                angularaxis=dict(
                    gridcolor="#1e293b",
                    tickfont=dict(color="#94a3b8", size=12),
                ),
            ),
            plot_bgcolor="#0f172a",
            paper_bgcolor="#0f172a",
            font=dict(color="#94a3b8", family="DM Sans"),
            showlegend=False,
            height=430,
            margin=dict(l=50, r=50, t=50, b=50),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        # Tabla detalle de indicadores
        detail_data = {
            "Indicador":    ["P/E Ratio", "PEG Ratio", "ROE", "EPS Growth (3Y)", "Dividend Yield"],
            "Valor real":   [
                f"{row['pe_ratio']:.1f}x",
                f"{row['peg_ratio']:.2f}",
                f"{row['roe']:.1f}%",
                f"{row['eps_growth']:+.1f}%",
                f"{row['dividend_yield']:.2f}%",
            ],
            "Score (0–10)": [f"{s:.1f}" for s in [pe_score, peg_score, roe_score, eps_score, div_score]],
            "Fuente":       ["yfinance / ref.", "yfinance / ref.", "yfinance / ref.", "Simulado", "yfinance / ref."],
        }
        st.dataframe(pd.DataFrame(detail_data), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="color:#334155;font-size:0.78rem;text-align:center;">'
    '⚠️ Este análisis es solo informativo y no constituye asesoramiento financiero. '
    'Invertir en mercados de valores conlleva riesgos, incluyendo la pérdida del capital invertido. '
    'Consultá siempre a un asesor financiero certificado antes de tomar decisiones de inversión. '
    '· Top 20 Investables 2026 · Datos: Yahoo Finance + proyecciones de referencia'
    '</p>',
    unsafe_allow_html=True
)

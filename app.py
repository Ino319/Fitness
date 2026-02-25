"""
Smart Football Trainer
======================
Genera automáticamente un plan semanal de entrenamiento para jugadores amateurs de fútbol.
Ejecutar con: streamlit run app.py
"""

import streamlit as st
import json
import os
from datetime import date, datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Football Trainer",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# ESTILOS CSS PERSONALIZADOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=Barlow:wght@300;400;500&display=swap');

  /* Fondo oscuro tipo estadio nocturno */
  .stApp {
    background: linear-gradient(160deg, #0a0f1e 0%, #0d1a2b 50%, #0a1520 100%);
    font-family: 'Barlow', sans-serif;
    color: #e8eef5;
  }

  /* Ocultar elementos de Streamlit */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1rem; padding-bottom: 2rem; max-width: 700px; }

  /* Título principal */
  .main-title {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: clamp(2.5rem, 8vw, 4.5rem);
    font-weight: 800;
    letter-spacing: -1px;
    text-transform: uppercase;
    line-height: 1;
    margin-bottom: 0;
    background: linear-gradient(90deg, #00e676, #1de9b6, #00bcd4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .main-subtitle {
    font-family: 'Barlow', sans-serif;
    font-size: 0.95rem;
    color: #607d8b;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-top: 2px;
    margin-bottom: 1.5rem;
  }

  .section-label {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #00e676;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    border-left: 3px solid #00e676;
    padding-left: 10px;
  }

  /* Tarjetas de días */
  .day-card {
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    border-left: 4px solid;
    backdrop-filter: blur(4px);
  }
  .day-card.match {
    background: rgba(255, 193, 7, 0.12);
    border-color: #ffc107;
  }
  .day-card.rest {
    background: rgba(96, 125, 139, 0.1);
    border-color: #455a64;
  }
  .day-card.regen {
    background: rgba(0, 188, 212, 0.1);
    border-color: #00bcd4;
  }
  .day-card.low {
    background: rgba(139, 195, 74, 0.1);
    border-color: #8bc34a;
  }
  .day-card.medium {
    background: rgba(255, 152, 0, 0.1);
    border-color: #ff9800;
  }
  .day-card.high {
    background: rgba(244, 67, 54, 0.1);
    border-color: #f44336;
  }
  .day-name {
    font-family: 'Barlow Condensed', sans-serif;
    font-weight: 700;
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .day-type {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    opacity: 0.7;
  }
  .day-detail {
    font-size: 0.95rem;
    margin-top: 3px;
    color: #cfd8dc;
  }
  .intensity-bar {
    display: inline-block;
    height: 6px;
    border-radius: 3px;
    margin-top: 6px;
  }

  /* Tarjeta de carga */
  .load-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 16px;
    margin-top: 1rem;
  }
  .load-number {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: #00e676;
  }
  .load-label {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: #607d8b;
  }

  /* Advertencia */
  .warning-box {
    background: rgba(255, 87, 34, 0.15);
    border: 1px solid #ff5722;
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 1rem;
    font-size: 0.9rem;
    color: #ff8a65;
  }

  /* Botón principal */
  div.stButton > button {
    background: linear-gradient(90deg, #00e676, #1de9b6) !important;
    color: #0a0f1e !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
  }
  div.stButton > button:hover {
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
  }

  /* Sliders y selectboxes */
  .stSlider > div { padding-top: 0 !important; }
  label { color: #b0bec5 !important; font-size: 0.9rem !important; }

  /* Divisor */
  hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.5rem 0 !important; }

  /* Historial badge */
  .badge-up { color: #f44336; font-weight: 600; }
  .badge-down { color: #00e676; font-weight: 600; }
  .badge-same { color: #ffc107; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
DAYS_ES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
DAYS_LABEL = {
    "Monday": "Lunes", "Tuesday": "Martes", "Wednesday": "Miércoles",
    "Thursday": "Jueves", "Friday": "Viernes", "Saturday": "Sábado", "Sunday": "Domingo"
}
HISTORY_FILE = "training_history.json"

# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────

def load_history() -> list:
    """Carga el historial desde el archivo JSON. Devuelve lista vacía si no existe."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history: list) -> None:
    """Guarda el historial en el archivo JSON."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def calculate_load(minutes: int, fatigue: int) -> int:
    """
    Calcula la carga semanal del jugador.
    Fórmula: carga = minutos * fatiga
    """
    return minutes * fatigue


def day_offset(base_day: str, offset: int) -> str:
    """Devuelve el día de la semana sumando 'offset' días a 'base_day'."""
    idx = DAYS_ES.index(base_day)
    return DAYS_ES[(idx + offset) % 7]


def intensity_bar_html(level: int, max_level: int = 5) -> str:
    """Genera una barra de intensidad visual en HTML."""
    colors = ["#607d8b", "#8bc34a", "#ffeb3b", "#ff9800", "#f44336"]
    color = colors[min(level - 1, 4)]
    width = int((level / max_level) * 100)
    return (
        f'<div class="intensity-bar" style="width:{width}%;background:{color};"></div>'
        f'<span style="font-size:0.78rem;color:{color};margin-left:6px;">{level}/5</span>'
    )


def card_class(session_type: str) -> str:
    """Determina la clase CSS de la tarjeta según el tipo de sesión."""
    t = session_type.lower()
    if "match" in t or "partido" in t:
        return "match"
    if "rest" in t or "descanso" in t:
        return "rest"
    if "regen" in t or "recup" in t:
        return "regen"
    if "baja" in t or "activaci" in t:
        return "low"
    if "media" in t:
        return "medium"
    return "high"


def generate_week_plan(
    match: bool,
    match_day: str,
    fatigue: int,
    objective: str
) -> list:
    """
    Genera el plan semanal de entrenamiento.

    Parámetros:
        match      - ¿Hay partido esta semana?
        match_day  - Día del partido (string del día en inglés)
        fatigue    - Nivel de fatiga (1–5)
        objective  - 'Velocidad' | 'Resistencia' | 'Mantener'

    Devuelve lista de dicts:
        [{ 'day', 'type', 'detail', 'intensity' }, ...]
    """

    # Inicializar plan con descanso por defecto
    plan = {day: {"type": "Descanso", "detail": "Recuperación completa. Hidratación y sueño.", "intensity": 0}
            for day in DAYS_ES}

    if match:
        idx_match = DAYS_ES.index(match_day)

        # Día del partido
        plan[match_day] = {
            "type": "⚽ MATCH DAY",
            "detail": "Partido oficial. Calentamiento 15 min. Mantén concentración.",
            "intensity": 5
        }

        # Día posterior → regenerativo
        post = DAYS_ES[(idx_match + 1) % 7]
        plan[post] = {
            "type": "Regenerativo",
            "detail": "Trote suave 15 min + estiramientos. Foco en recuperación.",
            "intensity": 1
        }

        # 3 días antes → intensidad media
        day_minus3 = DAYS_ES[(idx_match - 3) % 7]
        plan[day_minus3] = _build_session("media", fatigue, objective)

        # 2 días antes → intensidad baja
        day_minus2 = DAYS_ES[(idx_match - 2) % 7]
        plan[day_minus2] = _build_session("baja", fatigue, objective)

        # 1 día antes → activación corta (NUNCA intenso)
        day_minus1 = DAYS_ES[(idx_match - 1) % 7]
        plan[day_minus1] = {
            "type": "Activación",
            "detail": "Activación corta 20 min: movilidad, pases cortos, remates suaves.",
            "intensity": 2
        }

    else:
        # Sin partido: plan distribuido por objetivos
        sessions = _no_match_sessions(objective)
        rest_days = set()

        # Distribuir sesiones en días no consecutivos preferentemente
        used = []
        for i, session in enumerate(sessions):
            day = DAYS_ES[i]
            plan[day] = session
            used.append(day)

        # Los 2 días restantes quedan como descanso (ya inicializados)

    # Ajuste de volumen si fatiga >= 4: reducir intensidad en 1 (mínimo 1)
    if fatigue >= 4:
        for day, session in plan.items():
            if session["intensity"] > 1:
                session["intensity"] = max(1, session["intensity"] - 1)
                session["detail"] += " [Vol. -30% por fatiga alta]"

    # Construir lista ordenada de lunes a domingo
    return [{"day": day, **plan[day]} for day in DAYS_ES]


def _build_session(intensity_level: str, fatigue: int, objective: str) -> dict:
    """Genera una sesión según nivel de intensidad y objetivo."""
    if intensity_level == "media":
        if objective == "Velocidad":
            return {
                "type": "Velocidad / Media",
                "detail": "Pasadas cortas 5×30m + circuito de agilidad 3 rondas.",
                "intensity": 3
            }
        elif objective == "Resistencia":
            return {
                "type": "Resistencia / Media",
                "detail": "Carrera continua 30 min ritmo moderado + técnica de balón.",
                "intensity": 3
            }
        else:
            return {
                "type": "Balanceado / Media",
                "detail": "Técnica de pase 20 min + trote 20 min. Ejercicios tácticos.",
                "intensity": 3
            }
    else:  # baja
        if objective == "Velocidad":
            return {
                "type": "Velocidad / Baja",
                "detail": "Aceleración progresiva 4×20m. Sin forzar. Técnica de carrera.",
                "intensity": 2
            }
        elif objective == "Resistencia":
            return {
                "type": "Aeróbico / Baja",
                "detail": "Trote suave 25 min. Mantener frecuencia cardíaca baja.",
                "intensity": 2
            }
        else:
            return {
                "type": "Técnica / Baja",
                "detail": "Control, dominio y pases cortos. Ritmo tranquilo 25 min.",
                "intensity": 2
            }


def _no_match_sessions(objective: str) -> list:
    """Devuelve 5 sesiones para semana sin partido según objetivo."""
    base = [
        {
            "type": "VO₂ Máx",
            "detail": "Intervalos: 8×1 min al 90% + 1 min descanso. Mejora capacidad aeróbica.",
            "intensity": 5
        },
        {
            "type": "Pasadas Explosivas",
            "detail": "Sprints 6×40m + cambios de dirección. Máxima potencia muscular.",
            "intensity": 4
        },
        {
            "type": "Fondo",
            "detail": "Carrera continua 40 min a ritmo cómodo. Construir base aeróbica.",
            "intensity": 3
        },
        {
            "type": "Técnica",
            "detail": "Control, regate, pases en corto y largo. Dominio del balón 45 min.",
            "intensity": 2
        },
        {
            "type": "Descanso Activo",
            "detail": "Estiramientos, movilidad articular y foam roller 20 min.",
            "intensity": 1
        }
    ]

    # Ajuste por objetivo
    if objective == "Velocidad":
        base[1]["detail"] = "Sprints 8×30m + reacciones explosivas. Énfasis en potencia de arranque."
        base[1]["intensity"] = 5
        base[0]["detail"] = "Intervalos cortos: 10×30s al máximo + 90s descanso (pasadas explosivas)."
    elif objective == "Resistencia":
        base[2]["detail"] = "Carrera continua 45 min ritmo moderado-alto. Trabajo aeróbico principal."
        base[2]["intensity"] = 4
        base[0]["detail"] = "VO₂ Máx largo: 6×2 min al 85% + 2 min recuperación activa."

    return base


# ─────────────────────────────────────────────
# HEADER PRINCIPAL
# ─────────────────────────────────────────────
st.markdown('<p class="main-title">⚽ Smart Football<br>Trainer</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Generador de plan semanal · Amateur Edition</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECCIÓN 1 – INPUTS DEL USUARIO
# ─────────────────────────────────────────────
st.markdown('<p class="section-label">01 — Esta semana</p>', unsafe_allow_html=True)

col1, col2 = st.columns([1, 1])

with col1:
    match_raw = st.selectbox("¿Hay partido esta semana?", ["No", "Sí"], key="match_input")
    match = (match_raw == "Sí")

with col2:
    match_day = st.selectbox(
        "Día del partido",
        options=DAYS_ES,
        format_func=lambda d: DAYS_LABEL[d],
        disabled=not match,
        key="match_day_input"
    )

st.markdown('<p class="section-label">02 — Tu estado</p>', unsafe_allow_html=True)

fatigue = st.slider(
    "Nivel de fatiga actual",
    min_value=1, max_value=5, value=2,
    help="1 = fresco, 5 = muy cansado"
)

# Etiqueta visual de fatiga
fatigue_labels = {1: "🟢 Fresco", 2: "🟡 Ligero", 3: "🟠 Moderado", 4: "🔴 Fatigado", 5: "🔴 Muy fatigado"}
st.caption(fatigue_labels[fatigue])

minutes_played = st.number_input(
    "Minutos jugados la semana pasada",
    min_value=0, max_value=300, value=60, step=5,
    help="Incluye partido + entrenamientos"
)

st.markdown('<p class="section-label">03 — Tu objetivo</p>', unsafe_allow_html=True)

objective = st.radio(
    "Objetivo principal",
    options=["Velocidad", "Resistencia", "Mantener"],
    horizontal=True,
    key="objective_input"
)

st.markdown("---")

# ─────────────────────────────────────────────
# BOTÓN PRINCIPAL
# ─────────────────────────────────────────────
generate = st.button("🏃 Generate My Week")

# ─────────────────────────────────────────────
# LÓGICA PRINCIPAL AL PRESIONAR EL BOTÓN
# ─────────────────────────────────────────────
if generate:
    history = load_history()

    # ── SECCIÓN 2: CÁLCULO DE CARGA ──────────────────────────────
    current_load = calculate_load(minutes_played, fatigue)
    today_str = date.today().isoformat()

    # Construir registro nuevo
    new_entry = {
        "date": today_str,
        "load": current_load,
        "inputs": {
            "match": match,
            "match_day": match_day if match else None,
            "fatigue": fatigue,
            "minutes_played": minutes_played,
            "objective": objective
        }
    }

    # Obtener carga anterior (última entrada, si existe)
    prev_load = history[-1]["load"] if history else None

    # Comparar cargas
    overload_warning = False
    variation_pct = None
    if prev_load and prev_load > 0:
        variation_pct = ((current_load - prev_load) / prev_load) * 100
        if variation_pct > 20:
            overload_warning = True

    # Guardar en historial
    history.append(new_entry)
    save_history(history)

    # ── SECCIÓN 3: GENERAR PLAN ───────────────────────────────────
    week_plan = generate_week_plan(match, match_day, fatigue, objective)

    # ── MOSTRAR CARGA ─────────────────────────────────────────────
    st.markdown('<p class="section-label">📊 Carga semanal</p>', unsafe_allow_html=True)

    cols = st.columns(3)
    with cols[0]:
        st.markdown(
            f'<div class="load-card" style="text-align:center">'
            f'<div class="load-label">Carga actual</div>'
            f'<div class="load-number">{current_load}</div>'
            f'</div>', unsafe_allow_html=True
        )
    with cols[1]:
        prev_val = prev_load if prev_load is not None else "—"
        st.markdown(
            f'<div class="load-card" style="text-align:center">'
            f'<div class="load-label">Carga anterior</div>'
            f'<div class="load-number" style="color:#607d8b">{prev_val}</div>'
            f'</div>', unsafe_allow_html=True
        )
    with cols[2]:
        if variation_pct is not None:
            sign = "+" if variation_pct > 0 else ""
            color = "#f44336" if variation_pct > 20 else ("#00e676" if variation_pct <= 0 else "#ffc107")
            var_str = f"{sign}{variation_pct:.1f}%"
        else:
            var_str = "—"
            color = "#607d8b"
        st.markdown(
            f'<div class="load-card" style="text-align:center">'
            f'<div class="load-label">Variación</div>'
            f'<div class="load-number" style="color:{color}">{var_str}</div>'
            f'</div>', unsafe_allow_html=True
        )

    # Advertencia de sobrecarga
    if overload_warning:
        st.markdown(
            f'<div class="warning-box">⚠️ <strong>Advertencia de sobrecarga:</strong> '
            f'Tu carga aumentó un <strong>{variation_pct:.1f}%</strong> respecto a la semana pasada '
            f'(límite recomendado: 20%). Considera reducir volumen o intensidad para evitar lesiones.</div>',
            unsafe_allow_html=True
        )

    # ── MOSTRAR PLAN SEMANAL ──────────────────────────────────────
    st.markdown('<p class="section-label">📅 Tu plan semanal</p>', unsafe_allow_html=True)

    if fatigue >= 4:
        st.caption("💡 Volumen reducido 30% debido a fatiga alta (≥ 4)")

    for session in week_plan:
        day_label = DAYS_LABEL[session["day"]]
        s_type = session["type"]
        s_detail = session["detail"]
        s_intensity = session["intensity"]
        css_class = card_class(s_type)

        bar_html = intensity_bar_html(s_intensity) if s_intensity > 0 else '<span style="font-size:0.78rem;color:#455a64;">Descanso</span>'

        st.markdown(
            f'<div class="day-card {css_class}">'
            f'  <div style="display:flex;justify-content:space-between;align-items:center;">'
            f'    <span class="day-name">{day_label}</span>'
            f'    <span class="day-type">{s_type}</span>'
            f'  </div>'
            f'  <div class="day-detail">{s_detail}</div>'
            f'  <div style="margin-top:8px;">{bar_html}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

    # ── SECCIÓN 4: HISTORIAL ──────────────────────────────────────
    if len(history) > 1:
        st.markdown('<p class="section-label">📈 Historial de carga</p>', unsafe_allow_html=True)

        # Mostrar últimas 5 entradas
        recent = history[-5:][::-1]
        for i, entry in enumerate(recent):
            label = "Esta semana" if i == 0 else entry["date"]
            emoji = "🔥" if i == 0 else "📅"
            obj_str = entry["inputs"].get("objective", "—")
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:6px 0;'
                f'border-bottom:1px solid rgba(255,255,255,0.05);font-size:0.88rem;">'
                f'<span style="color:#90a4ae;">{emoji} {label}</span>'
                f'<span style="color:#b0bec5;">{obj_str}</span>'
                f'<span style="color:#00e676;font-family:Barlow Condensed,sans-serif;'
                f'font-size:1rem;font-weight:700;">{entry["load"]}</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.caption("Smart Football Trainer · Generado el " + datetime.now().strftime("%d/%m/%Y %H:%M"))

# Mensaje de bienvenida si no se ha generado el plan aún
else:
    st.markdown(
        '<div style="text-align:center;padding:2rem 1rem;color:#455a64;">'
        '<div style="font-size:3rem;">⚽</div>'
        '<p style="font-size:0.9rem;letter-spacing:2px;text-transform:uppercase;">'
        'Completa los campos y presiona<br><strong style="color:#00e676;">Generate My Week</strong></p>'
        '</div>',
        unsafe_allow_html=True
    )

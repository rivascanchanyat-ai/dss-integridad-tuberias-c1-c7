
# ==========================================================
# DSS DRBI - IOWs - BAYES
# APP STREAMLIT
# VERSION 2.1 - INTERFAZ PROFESIONAL
# ==========================================================

import os
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st

from datetime import date, datetime


# ==========================================================
# CONFIGURACION DE PAGINA
# ==========================================================

st.set_page_config(

    page_title=
        "DSS Integridad de Tuberías",

    page_icon=
        "⚙️",

    layout=
        "wide",

    initial_sidebar_state=
        "expanded"

)


# ==========================================================
# RUTA DE BASE DE DATOS
# ==========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

RUTA_DB = os.path.join(
    BASE_DIR,
    "dss_drbi.db"
)


# ==========================================================
# CONEXION SQLITE
# ==========================================================

def obtener_conexion():

    con = sqlite3.connect(

        RUTA_DB,

        timeout=30,

        check_same_thread=False

    )

    con.row_factory = sqlite3.Row

    con.execute(
        "PRAGMA foreign_keys = ON;"
    )

    con.execute(
        "PRAGMA busy_timeout = 30000;"
    )

    return con


# ==========================================================
# FUNCION DE CONSULTA
# ==========================================================

def leer_sql(
    consulta,
    params=None
):

    con = obtener_conexion()

    try:

        df = pd.read_sql_query(

            consulta,

            con,

            params=params

        )

    finally:

        con.close()

    return df


# ==========================================================
# FUNCION DE AUDITORIA
# ==========================================================

def registrar_auditoria(

    modulo,

    accion,

    entidad,

    id_entidad,

    detalle

):

    con = obtener_conexion()

    try:

        with con:

            con.execute(
                """
                INSERT INTO auditoria
                (
                    modulo,
                    accion,
                    entidad,
                    id_entidad,
                    detalle,
                    version_dss
                )

                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    modulo,
                    accion,
                    entidad,
                    id_entidad,
                    detalle,
                    "2.0"
                )
            )

    finally:

        con.close()


# ==========================================================
# FUNCION: REGISTRAR NUEVA LINEA
# ==========================================================

def registrar_linea(

    id_linea,

    nombre,

    tipo_tuberia,

    servicio,

    unidad_area,

    origen,

    destino

):

    con = obtener_conexion()

    try:

        existe = con.execute(
            """
            SELECT COUNT(*)

            FROM lineas

            WHERE id_linea = ?
            """,
            (
                id_linea,
            )
        ).fetchone()[0]


        if existe > 0:

            raise ValueError(
                f"Ya existe la línea {id_linea}."
            )


        with con:

            con.execute(
                """
                INSERT INTO lineas
                (
                    id_linea,
                    nombre,
                    tipo_tuberia,
                    servicio,
                    unidad_area,
                    origen,
                    destino,
                    estado
                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    id_linea,
                    nombre,
                    tipo_tuberia,
                    servicio,
                    unidad_area,
                    origen,
                    destino,
                    "ACTIVO"
                )
            )


            con.execute(
                """
                INSERT INTO auditoria
                (
                    modulo,
                    accion,
                    entidad,
                    id_entidad,
                    detalle,
                    version_dss
                )

                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "GESTION_ACTIVOS",
                    "ALTA_LINEA",
                    "LINEA",
                    id_linea,
                    f"Nueva línea registrada: {tipo_tuberia}",
                    "2.0"
                )
            )

    finally:

        con.close()


# ==========================================================
# PERFIL CoF BASE
# ==========================================================

PERFIL_COF = {

    "Transferencia":
        "COF-TR-BASE",

    "Proceso":
        "COF-PR-BASE",

    "Submarina":
        "COF-SM-BASE"

}


# ==========================================================
# FUNCION: REGISTRAR NUEVO TRAMO
# ==========================================================

def registrar_tramo(

    id_tramo,

    id_linea,

    condicion_activo,

    material,

    especificacion_material,

    diametro_nominal_pulg,

    schedule,

    longitud_m,

    espesor_nominal_mm,

    espesor_minimo_aprobado_mm,

    fuente_espesor_minimo,

    codigo_diseno,

    presion_diseno_bar,

    temperatura_diseno_c,

    presion_operacion_bar,

    temperatura_operacion_c,

    caudal_operacion_m3h,

    fase_fluido,

    modo_operacion,

    condicion_instalacion,

    ambiente_externo,

    tiene_aislamiento,

    tiene_recubrimiento,

    tiene_proteccion_catodica,

    fecha_instalacion

):

    con = obtener_conexion()

    try:

        linea = con.execute(
            """
            SELECT
                tipo_tuberia

            FROM lineas

            WHERE id_linea = ?
            """,
            (
                id_linea,
            )
        ).fetchone()


        if linea is None:

            raise ValueError(
                "La línea seleccionada no existe."
            )


        existe = con.execute(
            """
            SELECT COUNT(*)

            FROM tramos

            WHERE id_tramo = ?
            """,
            (
                id_tramo,
            )
        ).fetchone()[0]


        if existe > 0:

            raise ValueError(
                f"Ya existe el tramo {id_tramo}."
            )


        tipo_tuberia = linea[
            "tipo_tuberia"
        ]


        id_perfil_cof = PERFIL_COF[
            tipo_tuberia
        ]


        with con:

            con.execute(
                """
                INSERT INTO tramos
                (
                    id_tramo,
                    id_linea,
                    condicion_activo,
                    material,
                    especificacion_material,
                    diametro_nominal_pulg,
                    schedule,
                    longitud_m,
                    espesor_nominal_mm,
                    espesor_minimo_aprobado_mm,
                    fuente_espesor_minimo,
                    codigo_diseno,
                    presion_diseno_bar,
                    temperatura_diseno_c,
                    presion_operacion_bar,
                    temperatura_operacion_c,
                    caudal_operacion_m3h,
                    fase_fluido,
                    modo_operacion,
                    condicion_instalacion,
                    ambiente_externo,
                    tiene_aislamiento,
                    tiene_recubrimiento,
                    tiene_proteccion_catodica,
                    fecha_instalacion,
                    id_perfil_cof,
                    estado,
                    clasificacion_dato
                )

                VALUES
                (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?
                )
                """,
                (
                    id_tramo,
                    id_linea,
                    condicion_activo,
                    material,
                    especificacion_material,
                    diametro_nominal_pulg,
                    schedule,
                    longitud_m,
                    espesor_nominal_mm,
                    espesor_minimo_aprobado_mm,
                    fuente_espesor_minimo,
                    codigo_diseno,
                    presion_diseno_bar,
                    temperatura_diseno_c,
                    presion_operacion_bar,
                    temperatura_operacion_c,
                    caudal_operacion_m3h,
                    fase_fluido,
                    modo_operacion,
                    condicion_instalacion,
                    ambiente_externo,
                    int(tiene_aislamiento),
                    int(tiene_recubrimiento),
                    int(tiene_proteccion_catodica),
                    (
                        fecha_instalacion.isoformat()
                        if fecha_instalacion
                        else None
                    ),
                    id_perfil_cof,
                    "ACTIVO",
                    "CONFIGURADO"
                )
            )


            con.execute(
                """
                INSERT INTO auditoria
                (
                    modulo,
                    accion,
                    entidad,
                    id_entidad,
                    detalle,
                    version_dss
                )

                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "GESTION_ACTIVOS",
                    "ALTA_TRAMO",
                    "TRAMO",
                    id_tramo,
                    (
                        f"Nuevo tramo. "
                        f"Línea={id_linea}; "
                        f"Tipo={tipo_tuberia}; "
                        f"Condición={condicion_activo}"
                    ),
                    "2.0"
                )
            )

    finally:

        con.close()


# ==========================================================
# ESTILOS - INTERFAZ PROFESIONAL
# ==========================================================

st.markdown(
    """
    <style>
    :root {
        --navy:#082a4a;
        --navy-2:#0b3f6e;
        --blue:#1186d9;
        --blue-soft:#eaf5ff;
        --red:#ff3b3b;
        --red-soft:#fff1f1;
        --green:#1caf67;
        --green-soft:#eefbf4;
        --amber:#f5a623;
        --amber-soft:#fff7e8;
        --text:#102a43;
        --muted:#6f8192;
        --border:#dfe8f0;
        --panel:#ffffff;
        --page:#f4f7fb;
    }

    html, body, [class*="css"] {
        font-family: Inter, "Segoe UI", Arial, sans-serif;
    }

    .stApp {
        background: var(--page);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: transparent;
        height: 0rem;
    }

    [data-testid="stToolbar"] {
        display: none;
    }

    [data-testid="stAppViewContainer"] > .main {
        background: var(--page);
    }

    .block-container {
        max-width: 1550px;
        padding-top: 0.35rem;
        padding-left: 1.15rem;
        padding-right: 1.15rem;
        padding-bottom: 2rem;
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        min-width: 235px;
        max-width: 235px;
        background:
            linear-gradient(180deg, #082744 0%, #082e50 55%, #06233e 100%);
        border-right: none;
    }

    [data-testid="stSidebar"] * {
        color: #e8f2fb;
    }

    [data-testid="stSidebar"] .stRadio > label {
        display:none;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.20rem;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label {
        padding: 0.52rem 0.62rem;
        border-radius: 7px;
        transition: all .15s ease;
        margin: 0;
        font-size: 0.90rem;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(255,255,255,0.08);
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, #0c79bf, #0c6ba8);
        box-shadow: inset 3px 0 0 #72c9ff;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.13);
    }

    .sb-brand {
        text-align:center;
        padding: .15rem .25rem .55rem .25rem;
    }

    .sb-logo {
        font-size:2.55rem;
        line-height:1;
        margin-bottom:.25rem;
    }

    .sb-title {
        font-size:1.08rem;
        font-weight:800;
        letter-spacing:.2px;
    }

    .sb-subtitle {
        font-size:.74rem;
        color:#a9c3d9 !important;
        margin-top:.15rem;
    }

    .sb-section {
        margin:.35rem 0 .15rem 0;
        font-size:.72rem;
        color:#7fa5c3 !important;
        text-transform:uppercase;
        letter-spacing:.8px;
    }

    .sb-footer {
        margin-top:.25rem;
        padding:.45rem .2rem 0 .2rem;
        font-size:.67rem;
        color:#7fa5c3 !important;
        line-height:1.45;
    }

    /* HERO */
    .hero {
        min-height: 96px;
        border-radius: 0 0 10px 10px;
        padding: 18px 24px;
        margin: 0 0 12px 0;
        color: white;
        position: relative;
        overflow: hidden;
        background-image:
            linear-gradient(90deg, rgba(7,44,77,.98) 0%, rgba(10,74,121,.88) 43%, rgba(4,35,62,.48) 100%),
            url("https://images.unsplash.com/photo-1513828583688-c52646db42da?auto=format&fit=crop&w=1800&q=80");
        background-size: cover;
        background-position: center 48%;
        box-shadow: 0 2px 8px rgba(16,42,67,.15);
    }

    .hero-title {
        font-size: 1.50rem;
        font-weight: 800;
        line-height: 1.12;
        margin-bottom: 3px;
        max-width: 720px;
    }

    .hero-sub {
        font-size: .93rem;
        opacity: .96;
    }

    .hero-update {
        position:absolute;
        right:18px;
        top:18px;
        background:rgba(4,25,45,.73);
        border:1px solid rgba(255,255,255,.16);
        border-radius:7px;
        padding:9px 13px;
        font-size:.70rem;
        line-height:1.35;
        min-width:150px;
    }

    /* KPI CARDS */
    .kpi-grid {
        display:grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap:10px;
        margin: 8px 0 12px 0;
    }

    .kpi-card {
        min-height: 78px;
        border-radius: 8px;
        padding: 12px 13px;
        border:1px solid var(--border);
        box-shadow:0 2px 7px rgba(25,59,91,.05);
        display:flex;
        align-items:center;
        gap:11px;
    }

    .kpi-blue { background:#eef8ff; }
    .kpi-red { background:#fff2f2; }
    .kpi-green { background:#eefbf5; }
    .kpi-amber { background:#fff8ea; }

    .kpi-icon {
        width:38px;
        height:38px;
        border-radius:9px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:1.32rem;
        flex:0 0 auto;
    }

    .ki-blue { background:#d9efff; color:#0a86dc; }
    .ki-red { background:#ffe1e1; color:#f33e3e; }
    .ki-green { background:#dff6e9; color:#14a45c; }
    .ki-amber { background:#ffefc8; color:#e99b00; }

    .kpi-label {
        font-size:.68rem;
        color:#536b7f;
        font-weight:700;
        margin-bottom:1px;
    }

    .kpi-value {
        color:#102a43;
        font-size:1.34rem;
        font-weight:850;
        line-height:1.12;
    }

    .kpi-note {
        font-size:.62rem;
        color:#698091;
        margin-top:2px;
    }

    /* PANELS */
    .section-card {
        background:#fff;
        border:1px solid var(--border);
        border-radius:9px;
        box-shadow:0 2px 8px rgba(30,60,90,.045);
        padding:12px;
        margin-bottom:12px;
    }

    .section-title {
        font-size:1.02rem;
        font-weight:800;
        color:#102a43;
        display:flex;
        align-items:center;
        gap:8px;
        margin:0 0 8px 0;
    }

    .chart-card {
        background:#fff;
        border:1px solid var(--border);
        border-radius:9px;
        box-shadow:0 2px 8px rgba(30,60,90,.045);
        padding:11px 12px 12px 12px;
        min-height: 228px;
    }

    .chart-title {
        font-size:.83rem;
        font-weight:800;
        color:#17324a;
        margin-bottom:9px;
    }

    /* DONUT */
    .donut-wrap {
        display:flex;
        align-items:center;
        justify-content:center;
        gap:20px;
        padding-top:5px;
    }

    .donut {
        width:125px;
        height:125px;
        border-radius:50%;
        position:relative;
        flex:0 0 auto;
    }

    .donut::after {
        content:"";
        position:absolute;
        width:66px;
        height:66px;
        border-radius:50%;
        background:white;
        left:29.5px;
        top:29.5px;
    }

    .legend-row {
        display:flex;
        align-items:center;
        gap:7px;
        font-size:.72rem;
        color:#536b7f;
        margin:7px 0;
    }

    .legend-dot {
        width:8px;
        height:8px;
        border-radius:50%;
    }

    /* SIMPLE BARS */
    .vbars {
        height:160px;
        display:flex;
        align-items:flex-end;
        justify-content:space-around;
        gap:7px;
        border-bottom:1px solid #dce5ed;
        padding:12px 6px 0 6px;
    }

    .vbar-item {
        width:15%;
        text-align:center;
        font-size:.60rem;
        color:#647b8e;
    }

    .vbar-value {
        font-size:.62rem;
        font-weight:800;
        color:#314c61;
        margin-bottom:4px;
    }

    .vbar {
        width:70%;
        margin:0 auto 5px auto;
        border-radius:4px 4px 0 0;
        min-height:5px;
    }

    .hbar-row {
        display:grid;
        grid-template-columns: 120px 1fr 58px;
        align-items:center;
        gap:8px;
        margin:9px 0;
        font-size:.66rem;
        color:#536b7f;
    }

    .hbar-track {
        height:10px;
        background:#eef2f5;
        border-radius:4px;
        overflow:hidden;
    }

    .hbar-fill {
        height:100%;
        border-radius:4px;
    }

    .hbar-value {
        text-align:right;
        font-weight:700;
        color:#4b6275;
    }

    /* DATAFRAME */
    [data-testid="stDataFrame"] {
        border:1px solid #dfe8f0;
        border-radius:8px;
        overflow:hidden;
    }

    [data-testid="stDataFrame"] iframe {
        background:white;
    }

    /* INPUTS */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        border-radius:6px !important;
        min-height:35px;
        background:white;
    }

    .stDownloadButton button {
        background:#0b84d6 !important;
        color:white !important;
        border:none !important;
        border-radius:6px !important;
        min-height:35px;
    }

    .stButton button {
        border-radius:6px;
    }

    /* PAGE TITLES FOR SUBPAGES */
    .page-title {
        font-size:1.65rem;
        font-weight:850;
        color:#102a43;
        margin:8px 0 2px 0;
    }

    .page-sub {
        color:#6f8192;
        font-size:.92rem;
        margin-bottom:18px;
    }

    @media (max-width: 1100px) {
        .kpi-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
        .hero-update { display:none; }
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="sb-brand">
            <div class="sb-logo">🏭</div>
            <div class="sb-title">DSS Integridad</div>
            <div class="sb-subtitle">DRBI · IOWs · Bayes</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sb-section">Navegación</div>',
        unsafe_allow_html=True
    )

    opciones_sidebar = {
        "🏠  Dashboard": "Dashboard",
        "▣  Activos y Tramos": "Activos y Tramos",
        "◉  IOW / Umbrales": "IOW / Umbrales",
        "◉  Bayes / PoF": "Bayes / PoF",
        "◉  DRBI": "DRBI",
        "▣  Inspecciones UT": "Inspecciones UT",
        "🛠  Mantenimiento": "Mantenimiento",
        "⬡  Fuentes de datos": "Fuentes de datos",
        "⚙  Configuración": "Configuración"
    }

    pagina_visual = st.radio(
        "Navegación",
        list(opciones_sidebar.keys()),
        label_visibility="collapsed"
    )

    pagina = opciones_sidebar[pagina_visual]

    st.divider()

    st.markdown(
        '<div class="sb-section">Modo de análisis</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="
            background:rgba(255,255,255,.08);
            border-radius:6px;
            padding:8px 10px;
            font-size:.69rem;
            color:#cfe3f3;">
            SIMULADO_ACADEMICO
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="sb-footer">
            ⓘ &nbsp; DSS v2.0<br>
            Modelo integrado<br>
            DRBI · IOWs · MPD-RVO<br>
            con actualización Bayesiana<br>
            y soporte IIoT
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# DASHBOARD
# ==========================================================

if pagina == "Dashboard":

    df = leer_sql(
        """
        SELECT *
        FROM vista_dss_ejecutiva
        ORDER BY riesgo DESC
        """
    )

    if df.empty:

        st.warning(
            "No existen resultados DRBI disponibles."
        )

    else:

        # ------------------------------------------------------
        # HERO
        # ------------------------------------------------------

        fecha_actualizacion = datetime.now().strftime("%d %b %Y  %H:%M")

        st.markdown(
            f"""
            <div class="hero">
                <div class="hero-title">
                    Sistema de soporte a decisiones
                </div>
                <div class="hero-sub">
                    para la integridad de tuberías de refinería
                </div>
                <div class="hero-update">
                    🗓 &nbsp; <b>Actualizado</b><br>
                    {fecha_actualizacion}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ------------------------------------------------------
        # KPI
        # ------------------------------------------------------

        total = int(len(df))

        altos = int(
            (
                df["categoria_riesgo"]
                .astype(str)
                .str.upper()
                == "ALTO"
            ).sum()
        )

        criticos = int(
            (
                df["categoria_riesgo"]
                .astype(str)
                .str.upper()
                == "CRITICO"
            ).sum()
        )

        rul_min = float(
            pd.to_numeric(
                df["rul_anos"],
                errors="coerce"
            ).min()
        )

        fila_rul = df.loc[
            pd.to_numeric(
                df["rul_anos"],
                errors="coerce"
            ).idxmin()
        ]

        tramo_rul_min = str(
            fila_rul["id_tramo"]
        )

        riesgo_total = float(
            pd.to_numeric(
                df["riesgo"],
                errors="coerce"
            ).fillna(0).sum()
        )

        pct_altos = (
            100.0 * altos / total
            if total > 0 else 0.0
        )

        pct_criticos = (
            100.0 * criticos / total
            if total > 0 else 0.0
        )

        st.markdown(
            f"""
            <div class="kpi-grid">
                <div class="kpi-card kpi-blue">
                    <div class="kpi-icon ki-blue">⌘</div>
                    <div>
                        <div class="kpi-label">Total de tramos</div>
                        <div class="kpi-value">{total}</div>
                        <div class="kpi-note">Tuberías analizadas</div>
                    </div>
                </div>

                <div class="kpi-card kpi-red">
                    <div class="kpi-icon ki-red">⚠</div>
                    <div>
                        <div class="kpi-label">Riesgo alto</div>
                        <div class="kpi-value">{altos}</div>
                        <div class="kpi-note">{pct_altos:.1f}% del total</div>
                    </div>
                </div>

                <div class="kpi-card kpi-red">
                    <div class="kpi-icon ki-red">▥</div>
                    <div>
                        <div class="kpi-label">Riesgo crítico</div>
                        <div class="kpi-value">{criticos}</div>
                        <div class="kpi-note">{pct_criticos:.1f}% del total</div>
                    </div>
                </div>

                <div class="kpi-card kpi-green">
                    <div class="kpi-icon ki-green">◷</div>
                    <div>
                        <div class="kpi-label">RUL mínimo</div>
                        <div class="kpi-value">{rul_min:.2f} años</div>
                        <div class="kpi-note">En tramo {tramo_rul_min}</div>
                    </div>
                </div>

                <div class="kpi-card kpi-amber">
                    <div class="kpi-icon ki-amber">◉</div>
                    <div>
                        <div class="kpi-label">Riesgo agregado</div>
                        <div class="kpi-value">USD {riesgo_total:,.0f}</div>
                        <div class="kpi-note">Costo esperado anual</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ------------------------------------------------------
        # PRIORIZACIÓN + FILTROS
        # ------------------------------------------------------

        st.markdown(
            '<div class="section-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">☷ &nbsp; Priorización de tramos</div>',
            unsafe_allow_html=True
        )

        f1, f2, f3, f4 = st.columns(
            [2.2, 1.15, 1.35, .8]
        )

        with f1:
            texto_busqueda = st.text_input(
                "Buscar",
                placeholder="Buscar tramo, mecanismo...",
                label_visibility="collapsed"
            )

        categorias = ["Todos"] + sorted(
            [
                str(x)
                for x in df["categoria_riesgo"]
                .dropna()
                .unique()
            ]
        )

        with f2:
            filtro_riesgo = st.selectbox(
                "Filtrar riesgo",
                categorias
            )

        tipos = ["Todos"] + sorted(
            [
                str(x)
                for x in df["tipo_tuberia"]
                .dropna()
                .unique()
            ]
        )

        with f3:
            filtro_tipo = st.selectbox(
                "Filtrar tipo de tubería",
                tipos
            )

        df_filtrado = df.copy()

        if texto_busqueda.strip():

            patron = texto_busqueda.strip().lower()

            mascara = (
                df_filtrado["id_tramo"]
                .astype(str)
                .str.lower()
                .str.contains(
                    patron,
                    regex=False
                )
            )

            if "mecanismo_gobernante" in df_filtrado.columns:
                mascara = mascara | (
                    df_filtrado["mecanismo_gobernante"]
                    .astype(str)
                    .str.lower()
                    .str.contains(
                        patron,
                        regex=False
                    )
                )

            df_filtrado = df_filtrado[
                mascara
            ]

        if filtro_riesgo != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado["categoria_riesgo"]
                .astype(str)
                == filtro_riesgo
            ]

        if filtro_tipo != "Todos":
            df_filtrado = df_filtrado[
                df_filtrado["tipo_tuberia"]
                .astype(str)
                == filtro_tipo
            ]

        def accion_corta(valor, prioridad=""):

            texto = str(valor).lower()
            pr = str(prioridad).upper()

            if "inspección" in texto or "inspeccion" in texto:
                return "Inspección UT"

            if "monitoreo rutinario" in texto:
                return "Monitoreo"

            if "incrementar" in texto:
                return "Incrementar monitoreo"

            if "repar" in texto:
                return "Reparación"

            if "reempl" in texto:
                return "Reemplazo"

            if "P2" in pr:
                return "Inspección UT"

            if "P3" in pr:
                return "Incrementar monitoreo"

            if "P4" in pr:
                return "Monitoreo"

            return str(valor)

        df_tabla = df_filtrado.copy()

        df_tabla["Acción recomendada"] = [
            accion_corta(
                a,
                p
            )
            for a, p
            in zip(
                df_tabla["accion_recomendada"],
                df_tabla["prioridad"]
            )
        ]

        columnas_tabla = {
            "id_tramo": "ID Tramo",
            "tipo_tuberia": "Tipo de tubería",
            "mecanismo_gobernante": "Mecanismo gobernante",
            "pof": "PoF",
            "riesgo": "Riesgo",
            "categoria_riesgo": "Categoría",
            "cr_estimada_mm_ano": "CR estimada (mm/año)",
            "rul_anos": "RUL (años)",
            "prioridad": "Prioridad"
        }

        export_cols = list(
            columnas_tabla.keys()
        ) + ["Acción recomendada"]

        df_export = df_tabla[
            export_cols
        ].rename(
            columns=columnas_tabla
        )

        with f4:
            st.download_button(
                "⬇ Exportar",
                data=df_export.to_csv(
                    index=False
                ).encode("utf-8-sig"),
                file_name="priorizacion_tramos.csv",
                mime="text/csv",
                use_container_width=True
            )

        formato = {
            "PoF": st.column_config.NumberColumn(
                "PoF",
                format="%.4f"
            ),
            "Riesgo": st.column_config.NumberColumn(
                "Riesgo",
                format="%.2f"
            ),
            "CR estimada (mm/año)": st.column_config.NumberColumn(
                "CR estimada (mm/año)",
                format="%.4f"
            ),
            "RUL (años)": st.column_config.NumberColumn(
                "RUL (años)",
                format="%.2f"
            )
        }

        st.dataframe(
            df_export,
            use_container_width=True,
            hide_index=True,
            height=255,
            column_config=formato
        )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

        # ------------------------------------------------------
        # GRÁFICOS INFERIORES
        # ------------------------------------------------------

        g1, g2, g3 = st.columns(
            [1, 1.22, 1.18]
        )

        # ---------------- DONUT ----------------
        with g1:

            alto_n = int(
                (
                    df["categoria_riesgo"]
                    .astype(str)
                    .str.upper()
                    == "ALTO"
                ).sum()
            )

            medio_n = int(
                (
                    df["categoria_riesgo"]
                    .astype(str)
                    .str.upper()
                    == "MEDIO"
                ).sum()
            )

            bajo_n = int(
                (
                    df["categoria_riesgo"]
                    .astype(str)
                    .str.upper()
                    == "BAJO"
                ).sum()
            )

            crit_n = int(
                (
                    df["categoria_riesgo"]
                    .astype(str)
                    .str.upper()
                    == "CRITICO"
                ).sum()
            )

            denom = max(
                alto_n + medio_n + bajo_n + crit_n,
                1
            )

            p_alto = 100 * alto_n / denom
            p_medio = 100 * medio_n / denom
            p_bajo = 100 * bajo_n / denom
            p_crit = 100 * crit_n / denom

            fin_crit = p_crit
            fin_alto = fin_crit + p_alto
            fin_medio = fin_alto + p_medio

            donut_bg = (
                f"conic-gradient("
                f"#8b1e2d 0 {fin_crit:.2f}%, "
                f"#f43b3b {fin_crit:.2f}% {fin_alto:.2f}%, "
                f"#f7b719 {fin_alto:.2f}% {fin_medio:.2f}%, "
                f"#25ad67 {fin_medio:.2f}% 100%)"
            )

            st.markdown(
                f"""
                <div class="chart-card">
                    <div class="chart-title">
                        ▣ &nbsp; Distribución de riesgo por categoría
                    </div>
                    <div class="donut-wrap">
                        <div class="donut"
                             style="background:{donut_bg};">
                        </div>
                        <div>
                            <div class="legend-row">
                                <span class="legend-dot" style="background:#8b1e2d"></span>
                                Crítico ({crit_n})
                            </div>
                            <div class="legend-row">
                                <span class="legend-dot" style="background:#f43b3b"></span>
                                Alto ({alto_n})
                            </div>
                            <div class="legend-row">
                                <span class="legend-dot" style="background:#f7b719"></span>
                                Medio ({medio_n})
                            </div>
                            <div class="legend-row">
                                <span class="legend-dot" style="background:#25ad67"></span>
                                Bajo ({bajo_n})
                            </div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------------- RUL ----------------
        with g2:

            df_rul = (
                df[
                    [
                        "id_tramo",
                        "rul_anos",
                        "categoria_riesgo"
                    ]
                ]
                .copy()
                .sort_values(
                    "id_tramo"
                )
            )

            max_rul = max(
                float(
                    pd.to_numeric(
                        df_rul["rul_anos"],
                        errors="coerce"
                    ).max()
                ),
                1.0
            )

            barras_html = ""

            for fila in df_rul.itertuples():

                valor = float(
                    fila.rul_anos
                )

                altura = max(
                    10,
                    int(
                        130
                        * valor
                        / max_rul
                    )
                )

                cat = str(
                    fila.categoria_riesgo
                ).upper()

                if cat in (
                    "CRITICO",
                    "ALTO"
                ):
                    color = "#f34a3e"
                elif cat == "MEDIO":
                    color = "#f5b62b"
                else:
                    color = "#28ad67"

                barras_html += f"""
                <div class="vbar-item">
                    <div class="vbar-value">
                        {valor:.2f}
                    </div>
                    <div class="vbar"
                         style="
                            height:{altura}px;
                            background:{color};
                         ">
                    </div>
                    <div>{fila.id_tramo}</div>
                </div>
                """

            st.markdown(
                f"""
                <div class="chart-card">
                    <div class="chart-title">
                        ♙ &nbsp; RUL estimado por tramo
                    </div>
                    <div class="vbars">
                        {barras_html}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ---------------- RIESGO MECANISMO ----------------
        with g3:

            df_mec = (
                df.groupby(
                    "mecanismo_gobernante",
                    as_index=False
                )["riesgo"]
                .sum()
                .sort_values(
                    "riesgo",
                    ascending=False
                )
            )

            max_r = max(
                float(
                    pd.to_numeric(
                        df_mec["riesgo"],
                        errors="coerce"
                    ).max()
                ),
                1.0
            )

            hbars = ""

            colores = [
                "#f33f4d",
                "#ff8a3d",
                "#ffa940",
                "#f4bf2d",
                "#29ae67",
                "#f4b52a"
            ]

            for i, fila in enumerate(
                df_mec.itertuples()
            ):

                width = max(
                    4,
                    100
                    * float(
                        fila.riesgo
                    )
                    / max_r
                )

                color = colores[
                    i % len(colores)
                ]

                hbars += f"""
                <div class="hbar-row">
                    <div title="{fila.mecanismo_gobernante}">
                        {str(fila.mecanismo_gobernante)[:22]}
                    </div>
                    <div class="hbar-track">
                        <div class="hbar-fill"
                             style="
                                width:{width:.1f}%;
                                background:{color};
                             ">
                        </div>
                    </div>
                    <div class="hbar-value">
                        {float(fila.riesgo):,.0f}
                    </div>
                </div>
                """

            st.markdown(
                f"""
                <div class="chart-card">
                    <div class="chart-title">
                        Riesgo agregado por mecanismo
                    </div>
                    {hbars}
                    <div style="
                        text-align:center;
                        font-size:.60rem;
                        color:#8091a0;
                        margin-top:8px;">
                        Riesgo (USD)
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )


# ==========================================================
# ACTIVOS Y TRAMOS
# ==========================================================

elif pagina == "Activos y Tramos":

    st.title(
        "Activos y Tramos"
    )

    st.caption(
        "Registro, consulta y ampliación de la población de tuberías."
    )


    tab1, tab2, tab3 = st.tabs(
        [
            "📋 Ver activos",
            "➕ Nueva línea",
            "➕ Nuevo tramo"
        ]
    )


    # ------------------------------------------------------
    # VER ACTIVOS
    # ------------------------------------------------------

    with tab1:

        df_activos = leer_sql(
            """
            SELECT

                l.id_linea,

                l.nombre
                    AS linea,

                l.tipo_tuberia,

                l.servicio,

                l.unidad_area,

                t.id_tramo,

                t.condicion_activo,

                t.material,

                t.diametro_nominal_pulg,

                t.schedule,

                t.espesor_nominal_mm,

                t.codigo_diseno,

                t.estado

            FROM lineas l

            LEFT JOIN tramos t

                ON l.id_linea =
                   t.id_linea

            ORDER BY

                l.id_linea,

                t.id_tramo
            """
        )


        st.dataframe(

            df_activos,

            use_container_width=True,

            hide_index=True

        )


    # ------------------------------------------------------
    # NUEVA LINEA
    # ------------------------------------------------------

    with tab2:

        st.subheader(
            "Registrar nueva línea"
        )


        with st.form(
            "form_nueva_linea"
        ):

            col1, col2 = st.columns(2)


            with col1:

                id_linea = st.text_input(
                    "ID de línea *",
                    placeholder="Ej.: L-PR-02"
                )

                nombre_linea = st.text_input(
                    "Nombre de línea *"
                )

                tipo_tuberia = st.selectbox(

                    "Tipo de tubería *",

                    [
                        "Proceso",
                        "Transferencia",
                        "Submarina"
                    ]

                )

                servicio = st.text_input(
                    "Servicio"
                )


            with col2:

                unidad_area = st.text_input(
                    "Unidad / área"
                )

                origen = st.text_input(
                    "Origen"
                )

                destino = st.text_input(
                    "Destino"
                )


            guardar_linea = st.form_submit_button(

                "Registrar línea",

                type="primary"

            )


        if guardar_linea:

            if (
                not id_linea.strip()
                or not nombre_linea.strip()
            ):

                st.error(
                    "ID y nombre de línea son obligatorios."
                )

            else:

                try:

                    registrar_linea(

                        id_linea.strip(),

                        nombre_linea.strip(),

                        tipo_tuberia,

                        servicio.strip(),

                        unidad_area.strip(),

                        origen.strip(),

                        destino.strip()

                    )


                    st.success(
                        f"Línea {id_linea} registrada correctamente."
                    )

                    st.info(
                        "Ahora puede registrar uno o varios "
                        "tramos homogéneos asociados."
                    )


                except Exception as error:

                    st.error(
                        str(error)
                    )


    # ------------------------------------------------------
    # NUEVO TRAMO
    # ------------------------------------------------------

    with tab3:

        st.subheader(
            "Registrar nuevo tramo homogéneo"
        )


        df_lineas = leer_sql(
            """
            SELECT
                id_linea,
                nombre,
                tipo_tuberia

            FROM lineas

            WHERE estado = 'ACTIVO'

            ORDER BY id_linea
            """
        )


        if df_lineas.empty:

            st.warning(
                "Primero debe registrar una línea."
            )

        else:

            opciones_lineas = {

                (
                    f"{fila.id_linea} | "
                    f"{fila.tipo_tuberia} | "
                    f"{fila.nombre}"
                ):
                fila.id_linea

                for fila
                in df_lineas.itertuples()
            }


            with st.form(
                "form_nuevo_tramo"
            ):

                seccion1, seccion2 = st.columns(2)


                with seccion1:

                    linea_label = st.selectbox(

                        "Línea *",

                        list(
                            opciones_lineas.keys()
                        )

                    )

                    id_tramo = st.text_input(
                        "ID del tramo *",
                        placeholder="Ej.: TR-PR-003"
                    )

                    condicion = st.selectbox(

                        "Condición del activo *",

                        [
                            "Nuevo",
                            "Existente"
                        ]

                    )

                    material = st.text_input(
                        "Material *",
                        value="Acero al carbono"
                    )

                    especificacion = st.text_input(
                        "Especificación de material"
                    )

                    codigo_diseno = st.selectbox(

                        "Código de diseño",

                        [
                            "ASME B31.3",
                            "ASME B31.4",
                            "ASME B31.8",
                            "Otro"
                        ]

                    )


                with seccion2:

                    diametro = st.number_input(

                        "Diámetro nominal (pulg)",

                        min_value=0.0,

                        value=8.0,

                        step=0.5

                    )

                    schedule = st.text_input(
                        "Schedule",
                        value="40"
                    )

                    longitud = st.number_input(

                        "Longitud (m)",

                        min_value=0.0,

                        value=10.0,

                        step=1.0

                    )

                    espesor_nominal = st.number_input(

                        "Espesor nominal (mm)",

                        min_value=0.0,

                        value=8.0,

                        step=0.1

                    )

                    espesor_minimo = st.number_input(

                        "Espesor mínimo aprobado (mm)",

                        min_value=0.0,

                        value=5.0,

                        step=0.1

                    )

                    fuente_tmin = st.text_input(

                        "Fuente de t_min",

                        value="Ingeniería de diseño"

                    )


                st.markdown(
                    "#### Condiciones de diseño y operación"
                )


                c1, c2, c3 = st.columns(3)


                with c1:

                    pd_bar = st.number_input(

                        "Presión diseño (bar)",

                        min_value=0.0,

                        value=20.0

                    )

                    po_bar = st.number_input(

                        "Presión operación (bar)",

                        min_value=0.0,

                        value=10.0

                    )


                with c2:

                    td_c = st.number_input(

                        "Temperatura diseño (°C)",

                        value=180.0

                    )

                    to_c = st.number_input(

                        "Temperatura operación (°C)",

                        value=120.0

                    )


                with c3:

                    caudal = st.number_input(

                        "Caudal operación (m³/h)",

                        min_value=0.0,

                        value=80.0

                    )

                    fecha_inst = st.date_input(

                        "Fecha de instalación",

                        value=date.today()

                    )


                st.markdown(
                    "#### Condición operativa y externa"
                )


                c4, c5 = st.columns(2)


                with c4:

                    fase = st.selectbox(

                        "Fase de fluido",

                        [
                            "Líquido",
                            "Vapor",
                            "Gas",
                            "Líquido-vapor",
                            "Otro"
                        ]

                    )

                    modo = st.selectbox(

                        "Modo de operación",

                        [
                            "Continuo",
                            "Intermitente",
                            "Batch",
                            "Otro"
                        ]

                    )

                    condicion_inst = st.text_input(

                        "Condición de instalación",

                        value="Rack de proceso"

                    )


                with c5:

                    ambiente = st.text_input(

                        "Ambiente externo",

                        value="Industrial"

                    )

                    aislamiento = st.checkbox(
                        "Tiene aislamiento"
                    )

                    recubrimiento = st.checkbox(
                        "Tiene recubrimiento externo"
                    )

                    pc = st.checkbox(
                        "Tiene protección catódica"
                    )


                guardar_tramo = st.form_submit_button(

                    "Registrar tramo",

                    type="primary"

                )


            if guardar_tramo:

                id_linea_sel = opciones_lineas[
                    linea_label
                ]


                if (
                    not id_tramo.strip()
                    or not material.strip()
                ):

                    st.error(
                        "ID del tramo y material son obligatorios."
                    )


                elif (
                    espesor_minimo
                    >= espesor_nominal
                ):

                    st.error(
                        "El espesor mínimo debe ser menor "
                        "que el espesor nominal."
                    )


                else:

                    try:

                        registrar_tramo(

                            id_tramo.strip(),

                            id_linea_sel,

                            condicion,

                            material.strip(),

                            especificacion.strip(),

                            diametro,

                            schedule.strip(),

                            longitud,

                            espesor_nominal,

                            espesor_minimo,

                            fuente_tmin.strip(),

                            codigo_diseno,

                            pd_bar,

                            td_c,

                            po_bar,

                            to_c,

                            caudal,

                            fase,

                            modo,

                            condicion_inst.strip(),

                            ambiente.strip(),

                            aislamiento,

                            recubrimiento,

                            pc,

                            fecha_inst

                        )


                        st.success(
                            f"Tramo {id_tramo} registrado correctamente."
                        )


                        if condicion == "Nuevo":

                            st.info(

                                "Activo NUEVO registrado. "
                                "CR y RUL permanecerán pendientes "
                                "hasta contar con evidencia de inspección UT."

                            )


                        st.warning(

                            "Siguiente etapa: screening de mecanismos, "
                            "confirmación de ingeniería y asignación IOW."

                        )


                    except Exception as error:

                        st.error(
                            str(error)
                        )


# ==========================================================
# IOW / UMBRALES
# ==========================================================

elif pagina == "IOW / Umbrales":

    st.title(
        "IOW y Umbrales de Integridad"
    )

    st.caption(
        "Biblioteca maestra y perfiles asignados a los tramos."
    )


    df_iow = leer_sql(
        """
        SELECT

            p.id_perfil_iow,

            p.tipo_tuberia,

            p.tipo_perfil,

            p.id_mecanismo,

            m.nombre AS mecanismo,

            lim.id_variable,

            v.nombre AS variable,

            lim.unidad,

            lim.normal_min,

            lim.normal_max,

            lim.limite_inferior,

            lim.limite_superior,

            lim.critico_inferior,

            lim.critico_superior,

            lim.tiempo_max_excursion_min

        FROM perfiles_iow p

        INNER JOIN mecanismos m

            ON p.id_mecanismo =
               m.id_mecanismo

        INNER JOIN limites_iow lim

            ON p.id_perfil_iow =
               lim.id_perfil_iow

        INNER JOIN variables v

            ON lim.id_variable =
               v.id_variable

        ORDER BY

            p.tipo_tuberia,

            p.id_perfil_iow,

            lim.id_variable
        """
    )


    st.dataframe(

        df_iow,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# BAYES / PoF
# ==========================================================

elif pagina == "Bayes / PoF":

    st.title(
        "Actualización Bayesiana / PoF"
    )


    df_bayes = leer_sql(
        """
        WITH ultimo AS
        (
            SELECT

                id_tramo,

                id_mecanismo,

                MAX(fecha_hora)
                    AS fecha_max

            FROM estado_bayes

            GROUP BY

                id_tramo,

                id_mecanismo
        )

        SELECT

            eb.id_tramo,

            eb.id_mecanismo,

            m.nombre AS mecanismo,

            eb.fecha_hora,

            eb.posterior_bueno
                AS p_bueno,

            eb.posterior_degradado
                AS p_degradado,

            eb.posterior_severo
                AS p_severo,

            eb.pof_actualizada
                AS pof_1y,

            eb.incertidumbre_pof
                AS incertidumbre

        FROM estado_bayes eb

        INNER JOIN ultimo u

            ON eb.id_tramo =
               u.id_tramo

            AND eb.id_mecanismo =
                u.id_mecanismo

            AND eb.fecha_hora =
                u.fecha_max

        INNER JOIN mecanismos m

            ON eb.id_mecanismo =
               m.id_mecanismo

        ORDER BY

            eb.id_tramo,

            eb.id_mecanismo
        """
    )


    st.dataframe(

        df_bayes,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# DRBI
# ==========================================================

elif pagina == "DRBI":

    st.title(
        "DRBI Dinámico"
    )


    df_drbi = leer_sql(
        """
        SELECT *

        FROM vista_dss_ejecutiva

        ORDER BY riesgo DESC
        """
    )


    st.dataframe(

        df_drbi,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# INSPECCIONES UT
# ==========================================================

elif pagina == "Inspecciones UT":

    st.title(
        "Inspecciones UT / NDT"
    )


    df_ut = leer_sql(
        """
        SELECT

            id_tramo,

            id_cml,

            fecha_inspeccion,

            espesor_medido_mm,

            incertidumbre_mm,

            metodo,

            equipo,

            fuente_documento,

            calidad

        FROM inspecciones_ut

        ORDER BY

            id_tramo,

            fecha_inspeccion DESC
        """
    )


    st.dataframe(

        df_ut,

        use_container_width=True,

        hide_index=True

    )


# ==========================================================
# MANTENIMIENTO
# ==========================================================

elif pagina == "Mantenimiento":

    st.markdown(
        '<div class="page-title">Mantenimiento y decisión prescriptiva</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="page-sub">'
        'Recomendaciones C5, programación C6 y evaluación C7.'
        '</div>',
        unsafe_allow_html=True
    )

    def objeto_sql_existe(nombre):

        con = obtener_conexion()

        try:

            fila = con.execute(
                """
                SELECT COUNT(*)
                FROM sqlite_master
                WHERE
                    name = ?
                    AND type IN ('table','view')
                """,
                (nombre,)
            ).fetchone()

            return bool(
                fila[0]
            )

        finally:

            con.close()

    tab_c5, tab_c6, tab_c7 = st.tabs(
        [
            "Decisión prescriptiva",
            "Programa optimizado",
            "Evaluación"
        ]
    )

    with tab_c5:

        if objeto_sql_existe(
            "vista_c5_recomendacion_actual"
        ):

            df_c5_m = leer_sql(
                """
                SELECT *
                FROM vista_c5_recomendacion_actual
                ORDER BY
                    riesgo_residual_usd_ano DESC
                """
            )

            if df_c5_m.empty:

                st.info(
                    "No existen recomendaciones C5."
                )

            else:

                columnas = [
                    c
                    for c in [
                        "id_tramo",
                        "accion_recomendada",
                        "costo_accion_usd",
                        "pof_residual",
                        "riesgo_residual_usd_ano",
                        "plazo_max_seguro_meses",
                        "voi_usd"
                    ]
                    if c in df_c5_m.columns
                ]

                st.dataframe(
                    df_c5_m[columnas],
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.info(
                "La base actual no contiene todavía "
                "la vista C5 para mantenimiento."
            )

    with tab_c6:

        if objeto_sql_existe(
            "vista_c6_programa_actual"
        ):

            df_c6_m = leer_sql(
                """
                SELECT *
                FROM vista_c6_programa_actual
                ORDER BY
                    CASE
                        WHEN mes_programado IS NULL
                        THEN 999
                        ELSE mes_programado
                    END,
                    id_tramo
                """
            )

            if df_c6_m.empty:

                st.info(
                    "No existe programación C6."
                )

            else:

                columnas = [
                    c
                    for c in [
                        "id_tramo",
                        "accion_programada",
                        "mes_programado",
                        "fecha_programada",
                        "plazo_max_seguro_meses",
                        "costo_directo_usd",
                        "hh",
                        "estado_programacion"
                    ]
                    if c in df_c6_m.columns
                ]

                st.dataframe(
                    df_c6_m[columnas],
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.info(
                "La base actual no contiene todavía "
                "la vista C6 de programación."
            )

    with tab_c7:

        if objeto_sql_existe(
            "vista_c7_evaluacion_actual"
        ):

            df_c7_m = leer_sql(
                """
                SELECT *
                FROM vista_c7_evaluacion_actual
                """
            )

            if df_c7_m.empty:

                st.info(
                    "No existen indicadores C7."
                )

            else:

                columnas = [
                    c
                    for c in [
                        "indicador",
                        "baseline",
                        "dss",
                        "diferencia",
                        "mejora_pct",
                        "unidad"
                    ]
                    if c in df_c7_m.columns
                ]

                st.dataframe(
                    df_c7_m[columnas],
                    use_container_width=True,
                    hide_index=True
                )

        else:

            st.info(
                "La base actual no contiene todavía "
                "la vista C7 de evaluación."
            )




# ==========================================================
# FUENTES DE DATOS
# ==========================================================

elif pagina == "Fuentes de datos":

    st.title(
        "Fuentes de datos e integración"
    )


    df_fuentes = leer_sql(
        """
        SELECT *

        FROM fuentes_datos

        ORDER BY tipo_fuente
        """
    )


    st.dataframe(

        df_fuentes,

        use_container_width=True,

        hide_index=True

    )


    st.info(
        """
        Arquitectura prevista:

        • DCS/Historian → OPC UA / API
        • IIoT → MQTT / API
        • LIMS → API / integración de base de datos
        • UT/NDT → carga estructurada / API
        • Excel histórico → importación masiva
        """
    )


# ==========================================================
# CONFIGURACION
# ==========================================================

elif pagina == "Configuración":

    st.title(
        "Configuración del DSS"
    )


    st.write(
        "**Versión:** 2.1"
    )

    st.write(
        "**Unidad de análisis:** Tramo homogéneo"
    )

    st.write(
        "**Modo actual:** SIMULADO_ACADEMICO"
    )

    st.write(
        "**Mapa de red:** No incluido"
    )


    st.warning(
        """
        Los valores IOW, CoF, likelihoods Bayesianas y umbrales
        utilizados en esta versión son configuraciones sintéticas
        para desarrollo y validación académica.

        Para operación industrial deberán calibrarse y aprobarse
        mediante ingeniería, inspección, procesos y gestión de
        integridad.
        """
    )
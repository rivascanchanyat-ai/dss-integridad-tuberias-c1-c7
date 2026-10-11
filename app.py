import os
import sqlite3
from datetime import date, datetime
from textwrap import dedent

import pandas as pd
import streamlit as st

# ==========================================================
# DSS INTEGRIDAD DE TUBERÍAS - STREAMLIT
# DRBI · IOWs · Bayes · Decisión · MILP · Evaluación
# INTERFAZ PROFESIONAL V4.0
# ==========================================================

st.set_page_config(
    page_title="DSS Integridad de Tuberías",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(BASE_DIR, "dss_drbi.db")
VERSION_DSS = "4.0"
MODO_DATOS = "SIMULADO_ACADEMICO"

# ==========================================================
# BASE DE DATOS
# ==========================================================

def obtener_conexion():
    con = sqlite3.connect(RUTA_DB, timeout=30, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    con.execute("PRAGMA busy_timeout = 30000;")
    return con


def leer_sql(sql, params=None):
    con = obtener_conexion()
    try:
        return pd.read_sql_query(sql, con, params=params)
    finally:
        con.close()


def existe_objeto(nombre, tipo=None):
    con = obtener_conexion()
    try:
        if tipo:
            q = "SELECT COUNT(*) FROM sqlite_master WHERE name=? AND type=?"
            return con.execute(q, (nombre, tipo)).fetchone()[0] > 0
        q = "SELECT COUNT(*) FROM sqlite_master WHERE name=?"
        return con.execute(q, (nombre,)).fetchone()[0] > 0
    finally:
        con.close()


PERFIL_COF = {
    "Transferencia": "COF-TR-BASE",
    "Proceso": "COF-PR-BASE",
    "Submarina": "COF-SM-BASE",
}


def registrar_linea(id_linea, nombre, tipo_tuberia, servicio, unidad_area, origen, destino):
    id_linea = str(id_linea).strip()
    nombre = str(nombre).strip()
    if not id_linea or not nombre:
        raise ValueError("ID y nombre de línea son obligatorios.")

    con = obtener_conexion()
    try:
        if con.execute("SELECT COUNT(*) FROM lineas WHERE id_linea=?", (id_linea,)).fetchone()[0]:
            raise ValueError(f"Ya existe la línea {id_linea}.")
        with con:
            con.execute(
                """
                INSERT INTO lineas
                (id_linea,nombre,tipo_tuberia,servicio,unidad_area,origen,destino,estado)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (id_linea, nombre, tipo_tuberia, servicio, unidad_area, origen, destino, "ACTIVO"),
            )
            if existe_objeto("auditoria", "table"):
                con.execute(
                    """
                    INSERT INTO auditoria
                    (modulo,accion,entidad,id_entidad,detalle,version_dss)
                    VALUES (?,?,?,?,?,?)
                    """,
                    (
                        "GESTION_ACTIVOS",
                        "ALTA_LINEA",
                        "LINEA",
                        id_linea,
                        f"Nueva línea registrada. Tipo={tipo_tuberia}; Servicio={servicio}",
                        VERSION_DSS,
                    ),
                )
    finally:
        con.close()


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
    fecha_instalacion,
):
    id_tramo = str(id_tramo).strip()
    if not id_tramo:
        raise ValueError("El ID del tramo es obligatorio.")
    if espesor_minimo_aprobado_mm >= espesor_nominal_mm:
        raise ValueError("El espesor mínimo aprobado debe ser menor que el espesor nominal.")

    con = obtener_conexion()
    try:
        linea = con.execute(
            "SELECT tipo_tuberia FROM lineas WHERE id_linea=?", (id_linea,)
        ).fetchone()
        if linea is None:
            raise ValueError("La línea seleccionada no existe.")
        if con.execute("SELECT COUNT(*) FROM tramos WHERE id_tramo=?", (id_tramo,)).fetchone()[0]:
            raise ValueError(f"Ya existe el tramo {id_tramo}.")

        tipo_tuberia = linea["tipo_tuberia"]
        id_perfil_cof = PERFIL_COF.get(tipo_tuberia)

        with con:
            con.execute(
                """
                INSERT INTO tramos
                (
                    id_tramo,id_linea,condicion_activo,material,especificacion_material,
                    diametro_nominal_pulg,schedule,longitud_m,espesor_nominal_mm,
                    espesor_minimo_aprobado_mm,fuente_espesor_minimo,codigo_diseno,
                    presion_diseno_bar,temperatura_diseno_c,presion_operacion_bar,
                    temperatura_operacion_c,caudal_operacion_m3h,fase_fluido,modo_operacion,
                    condicion_instalacion,ambiente_externo,tiene_aislamiento,tiene_recubrimiento,
                    tiene_proteccion_catodica,fecha_instalacion,id_perfil_cof,estado,
                    clasificacion_dato
                )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
                    int(bool(tiene_aislamiento)),
                    int(bool(tiene_recubrimiento)),
                    int(bool(tiene_proteccion_catodica)),
                    fecha_instalacion.isoformat() if fecha_instalacion else None,
                    id_perfil_cof,
                    "ACTIVO",
                    "CONFIGURADO",
                ),
            )
    finally:
        con.close()

# ==========================================================
# HELPERS DE UI
# ==========================================================

def html(texto):
    st.markdown(dedent(texto).strip(), unsafe_allow_html=True)


def encabezado(titulo, subtitulo=""):
    actualizado = datetime.now().strftime("%d %b %Y %H:%M")
    html(
        f"""
        <div class="hero">
            <div>
                <div class="hero-title">{titulo}</div>
                <div class="hero-subtitle">{subtitulo}</div>
            </div>
            <div class="hero-status">▣ &nbsp; Actualizado<br><b>{actualizado}</b></div>
        </div>
        """
    )


def tarjeta_kpi(icono, titulo, valor, subtitulo, clase="blue"):
    html(
        f"""
        <div class="kpi-card kpi-{clase}">
            <div class="kpi-icon icon-{clase}">{icono}</div>
            <div class="kpi-content">
                <div class="kpi-title">{titulo}</div>
                <div class="kpi-value">{valor}</div>
                <div class="kpi-sub">{subtitulo}</div>
            </div>
        </div>
        """
    )


def prioridad_orden(valor):
    return {
        "P1 - INMEDIATA": 1,
        "P2 - ALTA": 2,
        "P3 - MEDIA": 3,
        "P4 - RUTINARIA": 4,
    }.get(str(valor), 99)


def accion_corta(texto):
    t = str(texto).lower()
    if "inspe" in t or "ut" in t:
        return "Inspección UT"
    if "increment" in t or "seguimiento" in t:
        return "Incrementar monitoreo"
    if "repar" in t:
        return "Reparación"
    if "reempl" in t:
        return "Reemplazo"
    if "mitig" in t:
        return "Mitigación operativa"
    return "Monitoreo"

# ==========================================================
# CSS GLOBAL
# ==========================================================
html(
    """
    <style>
    :root{
        --navy:#061a2f;
        --navy2:#0a2d4f;
        --blue:#0878d1;
        --light:#f5f8fc;
        --border:#d9e4ef;
        --text:#102b45;
        --muted:#6a7c90;
        --red:#ff4b4b;
        --amber:#f5a623;
        --green:#20a464;
    }

    .stApp{background:var(--light);color:var(--text)}
    .block-container{padding-top:1.45rem;padding-bottom:2rem;max-width:1650px}

    [data-testid="stSidebar"]{
        background:linear-gradient(180deg,#061a2f 0%,#092b4a 100%);
        border-right:1px solid rgba(255,255,255,.08)
    }
    [data-testid="stSidebar"] *{color:#f2f7fc}
    [data-testid="stSidebar"] hr{border-color:rgba(255,255,255,.14)}
    [data-testid="stSidebar"] [role="radiogroup"] label{
        padding:.42rem .55rem;border-radius:8px;margin-bottom:.06rem
    }

    .brand{padding:.15rem .1rem .5rem}
    .brand-icon{font-size:2rem;margin-bottom:.35rem}
    .brand-title{font-size:1.28rem;font-weight:800}
    .brand-sub{font-size:.78rem;color:#a9c4dd;margin-top:.16rem}
    .version-box{
        margin-top:1.2rem;padding:.75rem .8rem;border-radius:10px;
        background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.09);
        font-size:.72rem;line-height:1.55;color:#c4d6e8
    }

    .hero{
        min-height:110px;display:flex;align-items:center;justify-content:space-between;gap:1rem;
        border-radius:14px;padding:1.25rem 1.55rem;margin-bottom:1.15rem;
        background:
          radial-gradient(circle at 77% 5%,rgba(255,166,0,.24),transparent 20%),
          repeating-linear-gradient(90deg,rgba(255,255,255,.025) 0 2px,transparent 2px 45px),
          linear-gradient(105deg,#06223d 0%,#0a4b79 58%,#09233c 100%);
        box-shadow:0 7px 22px rgba(28,58,86,.12)
    }
    .hero-title{font-size:1.75rem;font-weight:800;color:white;line-height:1.15}
    .hero-subtitle{font-size:.94rem;color:#d4e5f3;margin-top:.3rem}
    .hero-status{
        min-width:165px;text-align:left;color:#edf7ff;background:rgba(3,22,39,.48);
        border:1px solid rgba(255,255,255,.15);border-radius:10px;padding:.62rem .8rem;
        font-size:.72rem;line-height:1.45
    }

    .kpi-card{
        min-height:105px;display:flex;align-items:center;gap:.85rem;
        background:white;border:1px solid var(--border);border-radius:10px;
        padding:.9rem 1rem;box-shadow:0 3px 14px rgba(26,61,95,.04)
    }
    .kpi-icon{
        width:43px;height:43px;display:flex;align-items:center;justify-content:center;
        border-radius:10px;font-size:1.25rem;font-weight:800;flex:0 0 43px
    }
    .icon-blue{background:#e8f4ff;color:#0b78d1}
    .icon-red{background:#fff0f0;color:#ef4444}
    .icon-green{background:#eaf8f0;color:#20a464}
    .icon-amber{background:#fff7df;color:#e89b05}
    .kpi-title{font-size:.74rem;font-weight:700;color:#586c80}
    .kpi-value{font-size:1.45rem;font-weight:850;color:#102b45;line-height:1.2;margin:.12rem 0}
    .kpi-sub{font-size:.68rem;color:#74879a}
    .kpi-blue{background:#f5fbff}.kpi-red{background:#fff8f8}.kpi-green{background:#f5fcf8}.kpi-amber{background:#fffaf0}

    .section-title{font-size:1.18rem;font-weight:800;color:#102b45;margin:.55rem 0 .55rem}
    .card-title{font-size:.92rem;font-weight:800;color:#173653;margin-bottom:.35rem}

    [data-testid="stDataFrame"]{
        border:1px solid var(--border);border-radius:9px;overflow:hidden;background:white
    }
    [data-testid="stMetric"]{
        background:white;border:1px solid var(--border);border-radius:10px;padding:.75rem .9rem
    }
    .stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{
        border-radius:8px!important;font-weight:700!important
    }
    .stDownloadButton>button{background:#0878d1!important;color:white!important;border-color:#0878d1!important}
    .stTabs [data-baseweb="tab-list"]{gap:.35rem}
    .stTabs [data-baseweb="tab"]{
        background:white;border:1px solid var(--border);border-radius:8px 8px 0 0;padding:.5rem .8rem
    }
    h1,h2,h3{color:#102b45;letter-spacing:-.02em}
    </style>
    """
)

# ==========================================================
# SIDEBAR
# ==========================================================
with st.sidebar:
    html(
        """
        <div class="brand">
            <div class="brand-icon">♜</div>
            <div class="brand-title">DSS Integridad</div>
            <div class="brand-sub">DRBI · IOWs · Bayes</div>
        </div>
        """
    )

    pagina = st.radio(
        "Navegación",
        [
            "Dashboard",
            "Activos y Tramos",
            "IOW / Umbrales",
            "Bayes / PoF",
            "DRBI",
            "Inspecciones UT",
            "Mantenimiento",
            "Fuentes de datos",
            "Configuración",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.caption("Modo de análisis")
    st.selectbox("Modo", [MODO_DATOS], label_visibility="collapsed", disabled=True)

    html(
        f"""
        <div class="version-box">
            <b>DSS v{VERSION_DSS}</b><br>
            Modelo integrado<br>
            DRBI · IOWs · Bayes · C5 · MILP-RH<br>
            Unidad: tramo homogéneo
        </div>
        """
    )

# ==========================================================
# DASHBOARD
# ==========================================================
if pagina == "Dashboard":
    encabezado(
        "Sistema de soporte a decisiones",
        "para la integridad de tuberías de refinería",
    )

    if not existe_objeto("vista_dss_ejecutiva"):
        st.error("No se encontró la vista 'vista_dss_ejecutiva' en dss_drbi.db.")
        st.stop()

    df = leer_sql("SELECT * FROM vista_dss_ejecutiva")
    if df.empty:
        st.warning("No existen resultados DRBI disponibles.")
        st.stop()

    df["orden_prioridad"] = df["prioridad"].apply(prioridad_orden)
    df = df.sort_values(["orden_prioridad", "riesgo"], ascending=[True, False])

    total = len(df)
    altos = int((df["categoria_riesgo"].astype(str).str.upper() == "ALTO").sum())
    criticos = int((df["categoria_riesgo"].astype(str).str.upper() == "CRITICO").sum())
    rul_min = float(pd.to_numeric(df["rul_anos"], errors="coerce").min())
    riesgo_total = float(pd.to_numeric(df["riesgo"], errors="coerce").sum())
    idx_min = pd.to_numeric(df["rul_anos"], errors="coerce").idxmin()
    tramo_rul_min = str(df.loc[idx_min, "id_tramo"])

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        tarjeta_kpi("⌘", "Total de tramos", str(total), "Tuberías analizadas", "blue")
    with c2:
        tarjeta_kpi("⚠", "Riesgo alto", str(altos), f"{altos/total*100:.1f}% del total", "red")
    with c3:
        tarjeta_kpi("▥", "Riesgo crítico", str(criticos), f"{criticos/total*100:.1f}% del total", "red")
    with c4:
        tarjeta_kpi("◷", "RUL mínimo", f"{rul_min:.2f} años", f"En tramo {tramo_rul_min}", "green")
    with c5:
        tarjeta_kpi("◉", "Riesgo agregado", f"USD {riesgo_total:,.0f}", "Costo esperado anual", "amber")

    st.write("")
    html('<div class="section-title">☷ &nbsp; Priorización de tramos</div>')

    f1, f2, f3, f4 = st.columns([1.7, .8, .9, .65])
    with f1:
        texto = st.text_input("Buscar", placeholder="Buscar tramo, mecanismo...", label_visibility="collapsed")
    with f2:
        riesgo_sel = st.selectbox(
            "Riesgo",
            ["Todos"] + sorted(df["categoria_riesgo"].dropna().astype(str).unique().tolist()),
            label_visibility="collapsed",
        )
    with f3:
        tipo_sel = st.selectbox(
            "Tipo",
            ["Todos"] + sorted(df["tipo_tuberia"].dropna().astype(str).unique().tolist()),
            label_visibility="collapsed",
        )

    df_f = df.copy()
    if texto:
        mask = (
            df_f["id_tramo"].astype(str).str.contains(texto, case=False, na=False)
            | df_f["mecanismo_gobernante"].astype(str).str.contains(texto, case=False, na=False)
        )
        df_f = df_f[mask]
    if riesgo_sel != "Todos":
        df_f = df_f[df_f["categoria_riesgo"].astype(str) == riesgo_sel]
    if tipo_sel != "Todos":
        df_f = df_f[df_f["tipo_tuberia"].astype(str) == tipo_sel]

    tabla = df_f[
        [
            "id_tramo",
            "tipo_tuberia",
            "mecanismo_gobernante",
            "pof",
            "riesgo",
            "categoria_riesgo",
            "cr_estimada_mm_ano",
            "rul_anos",
            "prioridad",
            "accion_recomendada",
        ]
    ].copy()

    tabla["accion_recomendada"] = tabla["accion_recomendada"].apply(accion_corta)

    with f4:
        csv = tabla.to_csv(index=False).encode("utf-8-sig")
        st.download_button("⬇ Exportar", csv, "priorizacion_tramos.csv", "text/csv", use_container_width=True)

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
        height=285,
        column_config={
            "id_tramo": st.column_config.TextColumn("ID Tramo", width="small"),
            "tipo_tuberia": st.column_config.TextColumn("Tipo de tubería", width="small"),
            "mecanismo_gobernante": st.column_config.TextColumn("Mecanismo gobernante", width="large"),
            "pof": st.column_config.NumberColumn("PoF", format="%.4f"),
            "riesgo": st.column_config.NumberColumn("Riesgo", format="%.2f"),
            "categoria_riesgo": st.column_config.TextColumn("Categoría"),
            "cr_estimada_mm_ano": st.column_config.NumberColumn("CR estimada\n(mm/año)", format="%.4f"),
            "rul_anos": st.column_config.NumberColumn("RUL\n(años)", format="%.2f"),
            "prioridad": st.column_config.TextColumn("Prioridad"),
            "accion_recomendada": st.column_config.TextColumn("Acción recomendada", width="medium"),
        },
    )

    g1, g2, g3 = st.columns(3)

    with g1:
        html('<div class="card-title">◉ &nbsp; Distribución de riesgo por categoría</div>')
        riesgo_count = df["categoria_riesgo"].value_counts().rename_axis("categoria").reset_index(name="cantidad")
        st.vega_lite_chart(
            riesgo_count,
            {
                "mark": {"type": "arc", "innerRadius": 58, "outerRadius": 98},
                "encoding": {
                    "theta": {"field": "cantidad", "type": "quantitative"},
                    "color": {
                        "field": "categoria",
                        "type": "nominal",
                        "scale": {
                            "domain": ["CRITICO", "ALTO", "MEDIO", "BAJO"],
                            "range": ["#b91c1c", "#ef4444", "#f5a623", "#20a464"],
                        },
                        "legend": {"title": None, "orient": "right"},
                    },
                    "tooltip": [
                        {"field": "categoria", "title": "Categoría"},
                        {"field": "cantidad", "title": "Tramos"},
                    ],
                },
                "height": 250,
            },
            use_container_width=True,
        )

    with g2:
        html('<div class="card-title">♙ &nbsp; RUL estimado por tramo</div>')
        rul_df = df[["id_tramo", "rul_anos"]].copy()
        st.vega_lite_chart(
            rul_df,
            {
                "mark": {"type": "bar", "cornerRadiusTopLeft": 4, "cornerRadiusTopRight": 4},
                "encoding": {
                    "x": {"field": "id_tramo", "type": "nominal", "axis": {"title": None}},
                    "y": {"field": "rul_anos", "type": "quantitative", "axis": {"title": "RUL (años)"}},
                    "color": {
                        "condition": [
                            {"test": "datum.rul_anos < 6", "value": "#ef4444"},
                            {"test": "datum.rul_anos < 10", "value": "#f5a623"},
                        ],
                        "value": "#20a464",
                    },
                    "tooltip": [
                        {"field": "id_tramo", "title": "Tramo"},
                        {"field": "rul_anos", "title": "RUL", "format": ".2f"},
                    ],
                },
                "height": 250,
            },
            use_container_width=True,
        )

    with g3:
        html('<div class="card-title">▰ &nbsp; Riesgo agregado por mecanismo</div>')
        r_mec = (
            df.groupby("mecanismo_gobernante", as_index=False)["riesgo"]
            .sum()
            .sort_values("riesgo", ascending=False)
        )
        st.vega_lite_chart(
            r_mec,
            {
                "mark": {"type": "bar", "cornerRadiusEnd": 4},
                "encoding": {
                    "y": {
                        "field": "mecanismo_gobernante",
                        "type": "nominal",
                        "sort": "-x",
                        "axis": {"title": None, "labelLimit": 180},
                    },
                    "x": {"field": "riesgo", "type": "quantitative", "axis": {"title": "Riesgo (USD/año)"}},
                    "color": {
                        "field": "riesgo",
                        "type": "quantitative",
                        "scale": {"range": ["#f5a623", "#ef4444"]},
                        "legend": None,
                    },
                    "tooltip": [
                        {"field": "mecanismo_gobernante", "title": "Mecanismo"},
                        {"field": "riesgo", "title": "Riesgo", "format": ",.0f"},
                    ],
                },
                "height": 250,
            },
            use_container_width=True,
        )

# ==========================================================
# ACTIVOS Y TRAMOS
# ==========================================================
elif pagina == "Activos y Tramos":
    encabezado("Activos y Tramos", "Registro, consulta y ampliación de la población de tuberías.")

    tab1, tab2, tab3 = st.tabs(["📋 Ver activos", "➕ Nueva línea", "➕ Nuevo tramo"])

    with tab1:
        df_activos = leer_sql(
            """
            SELECT
                l.id_linea,
                l.nombre AS linea,
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
            LEFT JOIN tramos t ON l.id_linea=t.id_linea
            ORDER BY l.id_linea,t.id_tramo
            """
        )
        a, b, c = st.columns(3)
        a.metric("Líneas registradas", df_activos["id_linea"].nunique())
        b.metric("Tramos registrados", int(df_activos["id_tramo"].notna().sum()))
        c.metric("Tipos de tubería", df_activos["tipo_tuberia"].nunique())
        st.dataframe(df_activos, use_container_width=True, hide_index=True, height=430)

    with tab2:
        st.subheader("Registrar nueva línea")
        with st.form("form_linea"):
            a, b = st.columns(2)
            with a:
                id_linea = st.text_input("ID de línea *", placeholder="Ej.: L-PR-02")
                nombre_linea = st.text_input("Nombre de línea *")
                tipo_tuberia = st.selectbox("Tipo de tubería *", ["Proceso", "Transferencia", "Submarina"])
                servicio = st.text_input("Servicio")
            with b:
                unidad_area = st.text_input("Unidad / área")
                origen = st.text_input("Origen")
                destino = st.text_input("Destino")
            guardar = st.form_submit_button("Registrar línea", type="primary", use_container_width=True)

        if guardar:
            try:
                registrar_linea(id_linea, nombre_linea, tipo_tuberia, servicio, unidad_area, origen, destino)
                st.success(f"Línea {id_linea} registrada correctamente.")
            except Exception as e:
                st.error(str(e))

    with tab3:
        st.subheader("Registrar nuevo tramo homogéneo")
        st.caption("CR, PoF y RUL no se ingresan manualmente; serán calculados por el DSS.")
        df_lineas = leer_sql(
            """
            SELECT id_linea,nombre,tipo_tuberia
            FROM lineas
            WHERE estado='ACTIVO'
            ORDER BY id_linea
            """
        )
        if df_lineas.empty:
            st.warning("Primero debe registrar una línea.")
        else:
            opciones = {
                f"{r.id_linea} | {r.tipo_tuberia} | {r.nombre}": r.id_linea
                for r in df_lineas.itertuples()
            }
            with st.form("form_tramo"):
                x1, x2 = st.columns(2)
                with x1:
                    linea_label = st.selectbox("Línea *", list(opciones.keys()))
                    id_tramo = st.text_input("ID del tramo *", placeholder="Ej.: TR-PR-003")
                    condicion = st.selectbox("Condición del activo *", ["Nuevo", "Existente"])
                    material = st.text_input("Material *", value="Acero al carbono")
                    especificacion = st.text_input("Especificación de material")
                    codigo = st.selectbox("Código de diseño", ["ASME B31.3", "ASME B31.4", "ASME B31.8", "Otro"])
                with x2:
                    diametro = st.number_input("Diámetro nominal (pulg)", min_value=0.1, value=8.0, step=0.5)
                    schedule = st.text_input("Schedule", value="40")
                    longitud = st.number_input("Longitud (m)", min_value=0.1, value=10.0)
                    e_nom = st.number_input("Espesor nominal (mm)", min_value=0.1, value=8.0, step=0.1)
                    e_min = st.number_input("Espesor mínimo aprobado (mm)", min_value=0.01, value=5.0, step=0.1)
                    fuente_min = st.text_input("Fuente de t_min", value="Ingeniería de diseño")

                st.markdown("#### Condiciones de diseño y operación")
                c1, c2, c3 = st.columns(3)
                with c1:
                    p_dis = st.number_input("Presión diseño (bar)", min_value=0.0, value=20.0)
                    p_op = st.number_input("Presión operación (bar)", min_value=0.0, value=10.0)
                with c2:
                    t_dis = st.number_input("Temperatura diseño (°C)", value=180.0)
                    t_op = st.number_input("Temperatura operación (°C)", value=120.0)
                with c3:
                    q_op = st.number_input("Caudal operación (m³/h)", min_value=0.0, value=80.0)
                    fecha_inst = st.date_input("Fecha de instalación", value=date.today())

                st.markdown("#### Condición operativa y externa")
                d1, d2 = st.columns(2)
                with d1:
                    fase = st.selectbox("Fase de fluido", ["Líquido", "Vapor", "Gas", "Líquido-vapor", "Otro"])
                    modo = st.selectbox("Modo de operación", ["Continuo", "Intermitente", "Batch", "Otro"])
                    cond_inst = st.text_input("Condición de instalación", value="Rack de proceso")
                with d2:
                    ambiente = st.text_input("Ambiente externo", value="Industrial")
                    aislamiento = st.checkbox("Tiene aislamiento")
                    recubrimiento = st.checkbox("Tiene recubrimiento externo")
                    pc = st.checkbox("Tiene protección catódica")

                guardar_tramo = st.form_submit_button("Registrar tramo", type="primary", use_container_width=True)

            if guardar_tramo:
                try:
                    registrar_tramo(
                        id_tramo, opciones[linea_label], condicion, material, especificacion,
                        diametro, schedule, longitud, e_nom, e_min, fuente_min, codigo,
                        p_dis, t_dis, p_op, t_op, q_op, fase, modo, cond_inst, ambiente,
                        aislamiento, recubrimiento, pc, fecha_inst,
                    )
                    st.success(f"Tramo {id_tramo} registrado correctamente.")
                    if condicion == "Nuevo":
                        st.info("Activo nuevo: CR y RUL permanecerán pendientes hasta contar con evidencia UT.")
                except Exception as e:
                    st.error(str(e))

# ==========================================================
# IOW / UMBRALES
# ==========================================================
elif pagina == "IOW / Umbrales":
    encabezado("IOW / Umbrales", "Biblioteca de ventanas operativas de integridad por mecanismo y tipo de tubería.")
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
        JOIN mecanismos m ON p.id_mecanismo=m.id_mecanismo
        JOIN limites_iow lim ON p.id_perfil_iow=lim.id_perfil_iow
        JOIN variables v ON lim.id_variable=v.id_variable
        ORDER BY p.tipo_tuberia,p.id_perfil_iow,lim.id_variable
        """
    )
    st.dataframe(df_iow, use_container_width=True, hide_index=True, height=520)

# ==========================================================
# BAYES / PoF
# ==========================================================
elif pagina == "Bayes / PoF":
    encabezado("Bayes / PoF", "Actualización probabilística del estado de degradación y de la probabilidad de falla.")
    df_bayes = leer_sql(
        """
        WITH ultimo AS (
            SELECT id_tramo,id_mecanismo,MAX(fecha_hora) AS fecha_max
            FROM estado_bayes
            GROUP BY id_tramo,id_mecanismo
        )
        SELECT
            eb.id_tramo,
            eb.id_mecanismo,
            m.nombre AS mecanismo,
            eb.fecha_hora,
            eb.posterior_bueno AS p_bueno,
            eb.posterior_degradado AS p_degradado,
            eb.posterior_severo AS p_severo,
            eb.pof_actualizada AS pof_1y,
            eb.incertidumbre_pof AS incertidumbre
        FROM estado_bayes eb
        JOIN ultimo u
          ON eb.id_tramo=u.id_tramo
         AND eb.id_mecanismo=u.id_mecanismo
         AND eb.fecha_hora=u.fecha_max
        JOIN mecanismos m ON eb.id_mecanismo=m.id_mecanismo
        ORDER BY eb.id_tramo,eb.id_mecanismo
        """
    )
    st.dataframe(df_bayes, use_container_width=True, hide_index=True, height=500)

# ==========================================================
# DRBI
# ==========================================================
elif pagina == "DRBI":
    encabezado("DRBI", "Evaluación dinámica del riesgo por tramo homogéneo.")
    df_drbi = leer_sql("SELECT * FROM vista_dss_ejecutiva ORDER BY riesgo DESC")
    a, b, c = st.columns(3)
    if not df_drbi.empty:
        a.metric("Riesgo agregado", f"USD {df_drbi['riesgo'].sum():,.0f}/año")
        b.metric("PoF máxima", f"{df_drbi['pof'].max():.4f}")
        c.metric("RUL mínima", f"{df_drbi['rul_anos'].min():.2f} años")
    st.dataframe(df_drbi, use_container_width=True, hide_index=True, height=500)

# ==========================================================
# INSPECCIONES UT
# ==========================================================
elif pagina == "Inspecciones UT":
    encabezado("Inspecciones UT / NDT", "Historial de mediciones de espesor y trazabilidad metrológica.")
    df_ut = leer_sql(
        """
        SELECT id_tramo,id_cml,fecha_inspeccion,espesor_medido_mm,
               incertidumbre_mm,metodo,equipo,fuente_documento,calidad
        FROM inspecciones_ut
        ORDER BY id_tramo,fecha_inspeccion DESC
        """
    )
    st.dataframe(df_ut, use_container_width=True, hide_index=True, height=520)

# ==========================================================
# MANTENIMIENTO C5-C7
# ==========================================================
elif pagina == "Mantenimiento":
    encabezado(
        "Mantenimiento y decisión prescriptiva",
        "C5 decisión · C6 programación MILP-RH · C7 evaluación del aporte.",
    )

    tab_c5, tab_c6, tab_c7, tab_val = st.tabs(
        ["C5 · Decisión", "C6 · Programa MILP", "C7 · Evaluación", "Validación"]
    )

    with tab_c5:
        if existe_objeto("vista_c5_recomendacion_actual", "view"):
            c5 = leer_sql("SELECT * FROM vista_c5_recomendacion_actual ORDER BY riesgo_residual_usd_ano DESC")
            st.subheader("Recomendación prescriptiva actual")
            st.dataframe(c5, use_container_width=True, hide_index=True, height=430)
        else:
            st.info("La vista C5 todavía no está disponible en la base cargada.")

    with tab_c6:
        if existe_objeto("vista_c6_programa_actual", "view"):
            c6 = leer_sql(
                """
                SELECT * FROM vista_c6_programa_actual
                ORDER BY CASE WHEN mes_programado IS NULL THEN 999 ELSE mes_programado END, id_tramo
                """
            )
            st.subheader("Programa optimizado de intervenciones")
            st.dataframe(c6, use_container_width=True, hide_index=True, height=430)
        else:
            st.info("La vista C6 todavía no está disponible en la base cargada.")

    with tab_c7:
        if existe_objeto("vista_c7_evaluacion_actual", "view"):
            c7 = leer_sql("SELECT * FROM vista_c7_evaluacion_actual")
            st.subheader("Baseline vs DSS")
            st.dataframe(c7, use_container_width=True, hide_index=True)
            if "mejora_pct" in c7.columns:
                graf = c7[c7["mejora_pct"].notna()][["indicador", "mejora_pct"]]
                if not graf.empty:
                    st.vega_lite_chart(
                        graf,
                        {
                            "mark": {"type": "bar", "cornerRadiusEnd": 4},
                            "encoding": {
                                "y": {"field": "indicador", "type": "nominal", "sort": "-x", "axis": {"title": None}},
                                "x": {"field": "mejora_pct", "type": "quantitative", "axis": {"title": "Mejora (%)"}},
                                "color": {"value": "#0878d1"},
                                "tooltip": [
                                    {"field": "indicador", "title": "Indicador"},
                                    {"field": "mejora_pct", "title": "Mejora %", "format": ".2f"},
                                ],
                            },
                            "height": 280,
                        },
                        use_container_width=True,
                    )
        else:
            st.info("La vista C7 todavía no está disponible en la base cargada.")

    with tab_val:
        if existe_objeto("vista_validacion_integral_actual", "view"):
            val = leer_sql("SELECT * FROM vista_validacion_integral_actual ORDER BY numero")
            pass_n = int((val["estado"] == "PASS").sum())
            fail_n = int((val["estado"] == "FAIL").sum())
            a, b, c = st.columns(3)
            a.metric("Pruebas", len(val))
            b.metric("PASS", pass_n)
            c.metric("FAIL", fail_n)
            st.dataframe(val, use_container_width=True, hide_index=True, height=430)
        else:
            st.info("La vista de validación integral todavía no está disponible.")

# ==========================================================
# FUENTES DE DATOS
# ==========================================================
elif pagina == "Fuentes de datos":
    encabezado("Fuentes de datos", "Arquitectura de integración OT/IT prevista para el DSS.")
    df_fuentes = leer_sql("SELECT * FROM fuentes_datos ORDER BY tipo_fuente")
    st.dataframe(df_fuentes, use_container_width=True, hide_index=True, height=420)
    st.info(
        "DCS/Historian → OPC UA/API · IIoT → MQTT/API · LIMS → API/BD · "
        "UT/NDT → carga estructurada/API · históricos → importación masiva."
    )

# ==========================================================
# CONFIGURACIÓN
# ==========================================================
elif pagina == "Configuración":
    encabezado("Configuración", "Parámetros generales y alcance del prototipo académico.")
    a, b, c = st.columns(3)
    a.metric("Versión", VERSION_DSS)
    b.metric("Unidad de análisis", "Tramo homogéneo")
    c.metric("Modo", MODO_DATOS)

    st.markdown("### Estado de la base")
    objetos = leer_sql(
        """
        SELECT type,name FROM sqlite_master
        WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'
        ORDER BY type,name
        """
    )
    st.dataframe(objetos, use_container_width=True, hide_index=True, height=300)

    st.warning(
        "Los datos y parámetros de esta versión se encuentran en modo académico/simulado. "
        "Para uso industrial, IOWs, CoF, transiciones, costos, recursos y criterios de seguridad "
        "deben calibrarse y aprobarse mediante ingeniería, inspección, procesos e integridad."
    )


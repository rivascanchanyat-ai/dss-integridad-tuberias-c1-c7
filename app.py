# ==========================================================
# DSS DRBI - IOWs - BAYES - POMDP/VoI - MILP (C1 -> C7)
# APP STREAMLIT COMPLETA Y MEJORADA PARA GITHUB
# VERSION 2.1
# ==========================================================

import os
import json
import sqlite3
import tempfile
import shutil
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from datetime import date, datetime


# ==========================================================
# 1. CONFIGURACION DE PAGINA
# ==========================================================

st.set_page_config(
    page_title="DSS Integridad de Tuberías (C1-C7)",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================
# 2. RUTA Y CONEXION SQLITE ROBUSTA
# ==========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_DB = os.path.join(BASE_DIR, "dss_drbi.db")

PERFIL_COF = {
    "Transferencia": "COF-TR-BASE",
    "Proceso": "COF-PR-BASE",
    "Submarina": "COF-SM-BASE",
}


def obtener_conexion():
    if not os.path.exists(RUTA_DB):
        st.error(
            f"❌ No se encontró el archivo de base de datos en: {RUTA_DB}. "
            "Asegúrate de subir 'dss_drbi.db' a la raíz de tu repositorio en GitHub."
        )
        st.stop()

    con = sqlite3.connect(RUTA_DB, timeout=30, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON;")
    con.execute("PRAGMA busy_timeout = 30000;")
    return con


def leer_sql(consulta, params=None):
    con = obtener_conexion()
    try:
        return pd.read_sql_query(consulta, con, params=params)
    finally:
        con.close()


def tabla_o_vista_existe(nombre):
    df = leer_sql(
        """
        SELECT COUNT(*) AS n
        FROM sqlite_master
        WHERE type IN ('table', 'view') AND name = ?
        """,
        params=(nombre,),
    )
    return int(df["n"].iloc[0]) > 0


# ==========================================================
# 3. FUNCIONES DE GESTION DE ACTIVOS Y SCREENING (C1-C2)
# ==========================================================

def registrar_linea(id_linea, nombre, tipo_tuberia, servicio, unidad_area, origen, destino):
    con = obtener_conexion()
    try:
        existe = con.execute(
            "SELECT COUNT(*) FROM lineas WHERE id_linea = ?", (id_linea,)
        ).fetchone()[0]
        if existe > 0:
            raise ValueError(f"Ya existe la línea {id_linea}.")

        with con:
            con.execute(
                """
                INSERT INTO lineas
                (id_linea, nombre, tipo_tuberia, servicio, unidad_area, origen, destino, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVO')
                """,
                (id_linea, nombre, tipo_tuberia, servicio, unidad_area, origen, destino),
            )
            con.execute(
                """
                INSERT INTO auditoria
                (modulo, accion, entidad, id_entidad, detalle, version_dss)
                VALUES ('GESTION_ACTIVOS', 'ALTA_LINEA', 'LINEA', ?, ?, '2.1')
                """,
                (id_linea, f"Nueva línea registrada: {tipo_tuberia} | Servicio: {servicio}"),
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
    con = obtener_conexion()
    try:
        linea = con.execute(
            "SELECT tipo_tuberia FROM lineas WHERE id_linea = ?", (id_linea,)
        ).fetchone()
        if linea is None:
            raise ValueError("La línea seleccionada no existe.")

        existe = con.execute(
            "SELECT COUNT(*) FROM tramos WHERE id_tramo = ?", (id_tramo,)
        ).fetchone()[0]
        if existe > 0:
            raise ValueError(f"Ya existe el tramo {id_tramo}.")

        tipo_tuberia = linea["tipo_tuberia"]
        id_perfil_cof = PERFIL_COF[tipo_tuberia]

        with con:
            con.execute(
                """
                INSERT INTO tramos
                (
                    id_tramo, id_linea, condicion_activo, material, especificacion_material,
                    diametro_nominal_pulg, schedule, longitud_m, espesor_nominal_mm,
                    espesor_minimo_aprobado_mm, fuente_espesor_minimo, codigo_diseno,
                    presion_diseno_bar, temperatura_diseno_c, presion_operacion_bar,
                    temperatura_operacion_c, caudal_operacion_m3h, fase_fluido,
                    modo_operacion, condicion_instalacion, ambiente_externo,
                    tiene_aislamiento, tiene_recubrimiento, tiene_proteccion_catodica,
                    fecha_instalacion, id_perfil_cof, estado, clasificacion_dato
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'ACTIVO', 'CONFIGURADO')
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
                    fecha_instalacion.isoformat() if fecha_instalacion else None,
                    id_perfil_cof,
                ),
            )
            con.execute(
                """
                INSERT INTO auditoria
                (modulo, accion, entidad, id_entidad, detalle, version_dss)
                VALUES ('GESTION_ACTIVOS', 'ALTA_TRAMO', 'TRAMO', ?, ?, '2.1')
                """,
                (
                    id_tramo,
                    f"Nuevo tramo. Línea={id_linea}; Tipo={tipo_tuberia}; Condición={condicion_activo}",
                ),
            )
    finally:
        con.close()


def evaluar_screening_tramo(id_tramo):
    df_tramo = leer_sql(
        """
        SELECT t.*, l.tipo_tuberia, l.servicio
        FROM tramos t
        INNER JOIN lineas l ON t.id_linea = l.id_linea
        WHERE t.id_tramo = ?
        """,
        params=(id_tramo,),
    )
    if df_tramo.empty:
        return pd.DataFrame()

    tramo = df_tramo.iloc[0]
    tipo = str(tramo["tipo_tuberia"])
    cond_inst = str(tramo["condicion_instalacion"] or "").lower()
    ambiente = str(tramo["ambiente_externo"] or "").lower()
    fase = str(tramo["fase_fluido"] or "").lower()

    candidatos = []
    if int(tramo["tiene_aislamiento"] or 0) == 1:
        candidatos.append({
            "id_mecanismo": "M009",
            "mecanismo": "Corrosión bajo aislamiento - CUI",
            "clasificacion": "Externo",
            "confianza": 0.85,
            "justificacion": "El tramo posee aislamiento térmico.",
        })

    if any(p in (cond_inst + " " + ambiente) for p in ["superficie", "aereo", "aéreo", "rack", "costero", "industrial"]):
        candidatos.append({
            "id_mecanismo": "M010",
            "mecanismo": "Corrosión atmosférica",
            "clasificacion": "Externo",
            "confianza": 0.80,
            "justificacion": "Exposición superficial / atmosférica detectada.",
        })

    if tipo == "Submarina" or "marino" in ambiente or "submar" in cond_inst:
        candidatos.append({
            "id_mecanismo": "M012",
            "mecanismo": "Corrosión externa marina",
            "clasificacion": "Externo",
            "confianza": 0.95,
            "justificacion": "Servicio submarino / ambiente marino.",
        })

    if "líquido" in fase or "liquido" in fase or tipo in ["Transferencia", "Submarina"]:
        candidatos.append({
            "id_mecanismo": "M001",
            "mecanismo": "Corrosión interna general",
            "clasificacion": "Principal",
            "confianza": 0.75,
            "justificacion": "Presencia potencial de fase líquida/acuosa.",
        })

    return pd.DataFrame(candidatos)


def confirmar_mecanismo_tramo_ui(id_tramo, id_mecanismo, clasificacion, justificacion, confianza):
    con = obtener_conexion()
    try:
        tramo = con.execute(
            """
            SELECT l.tipo_tuberia
            FROM tramos t
            INNER JOIN lineas l ON t.id_linea = l.id_linea
            WHERE t.id_tramo = ?
            """,
            (id_tramo,),
        ).fetchone()
        if tramo is None:
            raise ValueError("Tramo no encontrado.")

        tipo_tuberia = tramo["tipo_tuberia"]
        perfil = con.execute(
            """
            SELECT id_perfil_iow
            FROM perfiles_iow
            WHERE id_mecanismo = ? AND tipo_tuberia = ? AND estado LIKE 'VIGENTE%'
            ORDER BY version DESC LIMIT 1
            """,
            (id_mecanismo, tipo_tuberia),
        ).fetchone()

        ahora = datetime.now().isoformat()
        with con:
            con.execute(
                """
                INSERT INTO tramo_mecanismo
                (id_tramo, id_mecanismo, clasificacion, origen_evaluacion, justificacion, nivel_confianza, activo, fecha_confirmacion)
                VALUES (?, ?, ?, 'Screening DSS + Ingeniería', ?, ?, 1, ?)
                ON CONFLICT(id_tramo, id_mecanismo) DO UPDATE SET
                    clasificacion = excluded.clasificacion,
                    justificacion = excluded.justificacion,
                    nivel_confianza = excluded.nivel_confianza,
                    activo = 1,
                    fecha_confirmacion = excluded.fecha_confirmacion
                """,
                (id_tramo, id_mecanismo, clasificacion, justificacion, float(confianza), ahora),
            )

            if perfil is not None:
                con.execute(
                    """
                    INSERT INTO tramo_iow (id_tramo, id_perfil_iow, fecha_desde, activo)
                    VALUES (?, ?, ?, 1)
                    ON CONFLICT(id_tramo, id_perfil_iow) DO UPDATE SET activo = 1
                    """,
                    (id_tramo, perfil["id_perfil_iow"], ahora),
                )
        return perfil["id_perfil_iow"] if perfil else None
    finally:
        con.close()


# ==========================================================
# 4. EXPORTACION SEGURA DE SQLITE (CON WAL CHECKPOINT)
# ==========================================================

def obtener_bytes_db_segura():
    con = obtener_conexion()
    tmp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name
    try:
        con_backup = sqlite3.connect(tmp_path)
        with con_backup:
            con.backup(con_backup)
        con_backup.close()
        with open(tmp_path, "rb") as f:
            return f.read()
    finally:
        con.close()
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ==========================================================
# 5. ESTILOS CSS
# ==========================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 2rem;
    }
    .titulo-principal {
        font-size: 1.9rem;
        font-weight: 700;
        margin-bottom: 0.1rem;
    }
    .subtitulo {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# 6. SIDEBAR Y NAVEGACION
# ==========================================================

with st.sidebar:
    st.title("⚙️ DSS Integridad")
    st.caption("DRBI · IOWs · Bayes · POMDP · MILP")
    st.divider()

    pagina = st.radio(
        "Módulos del Sistema (C1 → C7)",
        [
            "📊 1. Dashboard Ejecutivo",
            "🏗️ 2. Activos, Tramos y Screening",
            "🚨 3. IOW y Excursiones (C2)",
            "🧠 4. Inferencia Bayesiana (C3)",
            "⚠️ 5. Riesgo DRBI e Inspección UT (C4)",
            "🎯 6. Decisión Prescriptiva y VoI (C5)",
            "📅 7. Programación MILP + RH (C6)",
            "📈 8. Evaluación Baseline vs DSS (C7)",
            "✅ 9. Validación Integral y Auditoría",
        ],
    )

    st.divider()
    st.subheader("💾 Persistencia SQLite")
    st.caption("Descarga o restaura tu base de datos con todos los cambios.")

    st.download_button(
        label="⬇️ Descargar dss_drbi.db",
        data=obtener_bytes_db_segura(),
        file_name=f"dss_drbi_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
        mime="application/octet-stream",
        use_container_width=True,
    )

    archivo_subido = st.file_uploader("Restaurar base .db", type=["db", "sqlite"])
    if archivo_subido is not None:
        if st.button("🔄 Aplicar base subida", use_container_width=True):
            with open(RUTA_DB, "wb") as f:
                f.write(archivo_subido.getbuffer())
            st.success("Base de datos actualizada correctamente.")
            st.rerun()

    st.divider()
    st.caption("Versión DSS: 2.1 (C1 → C7)")
    st.caption("Modo: SIMULADO_ACADEMICO")


# ==========================================================
# MODULO 1: DASHBOARD EJECUTIVO INTEGRADO
# ==========================================================

if pagina == "📊 1. Dashboard Ejecutivo":
    st.markdown('<div class="titulo-principal">Dashboard Ejecutivo de Integridad (C1 → C7)</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo">Visión integrada de riesgo dinámico DRBI, recomendación prescriptiva C5 y programación óptima C6</div>', unsafe_allow_html=True)

    usa_vista_c5_c6 = tabla_o_vista_existe("vista_dss_prescriptivo_actual")
    if usa_vista_c5_c6:
        df = leer_sql("SELECT * FROM vista_dss_prescriptivo_actual ORDER BY riesgo DESC")
    else:
        df = leer_sql("SELECT * FROM vista_dss_ejecutiva ORDER BY riesgo DESC")

    if df.empty:
        st.warning("No existen resultados disponibles en la base de datos.")
    else:
        c1, c2, c3, c4, c5 = st.columns(5)
        total_tramos = len(df)
        altos_criticos = int(df["categoria_riesgo"].isin(["ALTO", "CRITICO"]).sum())
        rul_min = float(df["rul_anos"].min())
        riesgo_total = float(df["riesgo"].sum())

        c1.metric("Tramos Monitoreados", total_tramos)
        c2.metric("Riesgo Alto / Crítico", altos_criticos)
        c3.metric("RUL Mínimo", f"{rul_min:.2f} años")
        c4.metric("Riesgo Actual (C4)", f"USD {riesgo_total:,.0f}/año")

        if usa_vista_c5_c6 and "costo_programado_usd" in df.columns:
            presupuesto_plan = float(df["costo_programado_usd"].fillna(0).sum())
            c5.metric("Inversión Plan C6", f"USD {presupuesto_plan:,.0f}")
        else:
            c5.metric("Estado Motor", "C1-C4 Activo")

        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            st.subheader("Matriz de Riesgo Dinámico por Tramo")
            fig_scatter = px.scatter(
                df,
                x="rul_anos",
                y="pof",
                size="riesgo",
                color="categoria_riesgo",
                hover_name="id_tramo",
                text="id_tramo",
                color_discrete_map={
                    "CRITICO": "#dc2626",
                    "ALTO": "#ea580c",
                    "MEDIO": "#ca8a04",
                    "BAJO": "#16a34a",
                },
                labels={
                    "rul_anos": "Vida Útil Remanente - RUL (años)",
                    "pof": "Probabilidad de Falla Dinámica - PoF (1 año)",
                    "riesgo": "Riesgo (USD/año)",
                    "categoria_riesgo": "Categoría",
                },
            )
            fig_scatter.update_traces(textposition="top center")
            fig_scatter.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col_graf2:
            st.subheader("Riesgo Actual vs Riesgo Residual Post-Acción (C5)")
            if usa_vista_c5_c6 and "riesgo_residual_c5" in df.columns:
                df_comp = df[["id_tramo", "riesgo", "riesgo_residual_c5"]].melt(
                    id_vars="id_tramo",
                    var_name="Escenario",
                    value_name="Riesgo_USD_Ano",
                )
                df_comp["Escenario"] = df_comp["Escenario"].replace({
                    "riesgo": "Riesgo Actual (C4)",
                    "riesgo_residual_c5": "Riesgo Residual Esperado (C5)",
                })
                fig_bar = px.bar(
                    df_comp,
                    x="id_tramo",
                    y="Riesgo_USD_Ano",
                    color="Escenario",
                    barmode="group",
                    color_discrete_sequence=["#ef4444", "#10b981"],
                    labels={"id_tramo": "Tramo", "Riesgo_USD_Ano": "USD / año"},
                )
                fig_bar.update_layout(height=380, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                fig_bar = px.bar(df, x="id_tramo", y="riesgo", color="categoria_riesgo")
                st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("📋 Tabla Maestra Ejecutiva (C4 → C5 → C6)")
        st.dataframe(df, use_container_width=True, hide_index=True)


# ==========================================================
# MODULO 2: ACTIVOS, TRAMOS Y SCREENING
# ==========================================================

elif pagina == "🏗️ 2. Activos, Tramos y Screening":
    st.title("Gestión de Activos, Tramos Homogéneos y Screening")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Inventario de Activos",
        "➕ Registrar Línea",
        "➕ Registrar Tramo",
        "🔍 Screening y Asignación IOW",
    ])

    with tab1:
        df_activos = leer_sql(
            """
            SELECT l.id_linea, l.nombre AS linea, l.tipo_tuberia, l.servicio,
                   t.id_tramo, t.condicion_activo, t.material, t.diametro_nominal_pulg,
                   t.espesor_nominal_mm, t.espesor_minimo_aprobado_mm,
                   t.presion_operacion_bar, t.temperatura_operacion_c, t.estado
            FROM lineas l
            LEFT JOIN tramos t ON l.id_linea = t.id_linea
            ORDER BY l.id_linea, t.id_tramo
            """
        )
        st.dataframe(df_activos, use_container_width=True, hide_index=True)

    with tab2:
        with st.form("form_nueva_linea"):
            col1, col2 = st.columns(2)
            with col1:
                id_linea = st.text_input("ID de línea *", placeholder="Ej.: L-PR-02")
                nombre_linea = st.text_input("Nombre de línea *")
                tipo_tuberia = st.selectbox("Tipo de tubería *", ["Proceso", "Transferencia", "Submarina"])
                servicio = st.text_input("Servicio")
            with col2:
                unidad_area = st.text_input("Unidad / área")
                origen = st.text_input("Origen")
                destino = st.text_input("Destino")

            if st.form_submit_button("Registrar línea", type="primary"):
                if not id_linea.strip() or not nombre_linea.strip():
                    st.error("ID y nombre de línea son obligatorios.")
                else:
                    try:
                        registrar_linea(
                            id_linea.strip(),
                            nombre_linea.strip(),
                            tipo_tuberia,
                            servicio.strip(),
                            unidad_area.strip(),
                            origen.strip(),
                            destino.strip(),
                        )
                        st.success(f"✅ Línea {id_linea} registrada correctamente.")
                    except Exception as e:
                        st.error(str(e))

    with tab3:
        df_lineas = leer_sql("SELECT id_linea, nombre, tipo_tuberia FROM lineas WHERE estado = 'ACTIVO' ORDER BY id_linea")
        if df_lineas.empty:
            st.warning("Primero registra una línea.")
        else:
            opciones_lineas = {
                f"{r.id_linea} | {r.tipo_tuberia} | {r.nombre}": r.id_linea
                for r in df_lineas.itertuples()
            }
            with st.form("form_nuevo_tramo"):
                s1, s2 = st.columns(2)
                with s1:
                    linea_label = st.selectbox("Línea *", list(opciones_lineas.keys()))
                    id_tramo = st.text_input("ID del tramo *", placeholder="Ej.: TR-PR-003")
                    condicion = st.selectbox("Condición del activo *", ["Nuevo", "Existente"])
                    material = st.text_input("Material *", value="Acero al carbono")
                    especificacion = st.text_input("Especificación", value="ASTM A106 Gr B")
                    codigo_diseno = st.selectbox("Código de diseño", ["ASME B31.3", "ASME B31.4", "ASME B31.8", "Otro"])
                with s2:
                    diametro = st.number_input("Diámetro nominal (pulg)", min_value=0.5, value=8.0, step=0.5)
                    schedule = st.text_input("Schedule", value="40")
                    longitud = st.number_input("Longitud (m)", min_value=0.1, value=25.0, step=1.0)
                    espesor_nominal = st.number_input("Espesor nominal (mm)", min_value=1.0, value=8.18, step=0.1)
                    espesor_minimo = st.number_input("Espesor mínimo aprobado t_min (mm)", min_value=0.5, value=5.50, step=0.1)
                    fuente_tmin = st.text_input("Fuente de t_min", value="Ingeniería / API 570")

                c1, c2, c3 = st.columns(3)
                with c1:
                    pd_bar = st.number_input("Presión diseño (bar)", min_value=0.0, value=20.0)
                    po_bar = st.number_input("Presión operación (bar)", min_value=0.0, value=10.0)
                with c2:
                    td_c = st.number_input("Temperatura diseño (°C)", value=180.0)
                    to_c = st.number_input("Temperatura operación (°C)", value=120.0)
                with c3:
                    caudal = st.number_input("Caudal operación (m³/h)", min_value=0.0, value=80.0)
                    fecha_inst = st.date_input("Fecha de instalación", value=date.today())

                c4, c5 = st.columns(2)
                with c4:
                    fase = st.selectbox("Fase de fluido", ["Líquido", "Líquido-vapor", "Gas", "Vapor"])
                    modo = st.selectbox("Modo de operación", ["Continuo", "Intermitente", "Batch"])
                    condicion_inst = st.text_input("Condición de instalación", value="Rack de proceso")
                with c5:
                    ambiente = st.text_input("Ambiente externo", value="Industrial")
                    aislamiento = st.checkbox("Tiene aislamiento térmico")
                    recubrimiento = st.checkbox("Tiene recubrimiento externo", value=True)
                    pc = st.checkbox("Tiene protección catódica")

                if st.form_submit_button("Registrar tramo homogéneo", type="primary"):
                    if not id_tramo.strip():
                        st.error("El ID del tramo es obligatorio.")
                    elif espesor_minimo >= espesor_nominal:
                        st.error("El espesor mínimo aprobado debe ser menor que el espesor nominal.")
                    else:
                        try:
                            registrar_tramo(
                                id_tramo.strip(),
                                opciones_lineas[linea_label],
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
                                fecha_inst,
                            )
                            st.success(f"✅ Tramo {id_tramo} registrado. Ve a la pestaña 'Screening' para asignar mecanismos e IOW.")
                        except Exception as e:
                            st.error(str(e))

    with tab4:
        st.subheader("Screening Preliminar y Confirmación de Mecanismos de Daño")
        df_tramos_lista = leer_sql("SELECT id_tramo FROM tramos ORDER BY id_tramo")
        tramo_sel = st.selectbox("Selecciona un tramo para evaluar:", df_tramos_lista["id_tramo"].tolist())

        if tramo_sel:
            df_cand = evaluar_screening_tramo(tramo_sel)
            st.markdown("**Mecanismos sugeridos por configuración del tramo:**")
            st.dataframe(df_cand, use_container_width=True, hide_index=True)

            df_mec_cat = leer_sql("SELECT id_mecanismo, nombre FROM mecanismos WHERE activo = 1 ORDER BY id_mecanismo")
            opciones_mec = {f"{r.id_mecanismo} - {r.nombre}": r.id_mecanismo for r in df_mec_cat.itertuples()}

            with st.form("form_confirmar_mec"):
                mec_label = st.selectbox("Mecanismo a confirmar", list(opciones_mec.keys()))
                clasif = st.selectbox("Clasificación", ["Principal", "Externo", "Secundario"])
                conf = st.slider("Nivel de confianza", 0.50, 1.00, 0.85, 0.05)
                justif = st.text_input("Justificación de ingeniería", value="Confirmado por revisión técnica de integridad.")

                if st.form_submit_button("Confirmar Mecanismo y Vincular IOW", type="primary"):
                    perfil_asignado = confirmar_mecanismo_tramo_ui(
                        tramo_sel, opciones_mec[mec_label], clasif, justif, conf
                    )
                    st.success(f"✅ Mecanismo confirmado para {tramo_sel}. Perfil IOW vinculado: {perfil_asignado or 'Pendiente en biblioteca'}")

            st.markdown("**Mecanismos actualmente activos en este tramo:**")
            df_act_mec = leer_sql(
                """
                SELECT tm.id_mecanismo, m.nombre AS mecanismo, tm.clasificacion, tm.nivel_confianza, tm.justificacion
                FROM tramo_mecanismo tm
                INNER JOIN mecanismos m ON tm.id_mecanismo = m.id_mecanismo
                WHERE tm.id_tramo = ? AND tm.activo = 1
                """,
                params=(tramo_sel,),
            )
            st.dataframe(df_act_mec, use_container_width=True, hide_index=True)


# ==========================================================
# MODULO 3: IOW Y EXCURSIONES (C2)
# ==========================================================

elif pagina == "🚨 3. IOW y Excursiones (C2)":
    st.title("Ventanas Operativas de Integridad (IOW) y Excursiones")

    tab_exc, tab_lib, tab_series = st.tabs([
        "⚡ Excursiones Consolidadas",
        "📚 Biblioteca Maestra de Límites IOW",
        "📈 Series Temporales de Sensores",
    ])

    with tab_exc:
        df_exc = leer_sql(
            """
            SELECT e.id_excursion, e.id_tramo, e.id_perfil_iow, p.tipo_perfil,
                   m.nombre AS mecanismo, e.id_variable, e.inicio, e.fin,
                   e.estado_maximo, e.valor_minimo, e.valor_maximo,
                   e.duracion_min, e.tiempo_max_permitido_min, e.magnitud, e.severidad
            FROM excursiones_iow e
            INNER JOIN perfiles_iow p ON e.id_perfil_iow = p.id_perfil_iow
            INNER JOIN mecanismos m ON p.id_mecanismo = m.id_mecanismo
            ORDER BY e.severidad DESC
            """
        )
        st.dataframe(df_exc, use_container_width=True, hide_index=True)

        if not df_exc.empty:
            fig_exc = px.bar(
                df_exc,
                x="id_tramo",
                y="severidad",
                color="estado_maximo",
                hover_data=["id_variable", "mecanismo", "duracion_min"],
                color_discrete_map={"CRITICO": "#dc2626", "ALERTA": "#f59e0b"},
                title="Severidad de Excursiones IOW por Tramo",
            )
            st.plotly_chart(fig_exc, use_container_width=True)

    with tab_lib:
        df_iow = leer_sql(
            """
            SELECT p.id_perfil_iow, p.tipo_tuberia, p.tipo_perfil, m.nombre AS mecanismo,
                   lim.id_variable, v.nombre AS variable, lim.unidad,
                   lim.normal_min, lim.normal_max, lim.limite_inferior, lim.limite_superior,
                   lim.critico_inferior, lim.critico_superior, lim.tiempo_max_excursion_min
            FROM perfiles_iow p
            INNER JOIN mecanismos m ON p.id_mecanismo = m.id_mecanismo
            INNER JOIN limites_iow lim ON p.id_perfil_iow = lim.id_perfil_iow
            INNER JOIN variables v ON lim.id_variable = v.id_variable
            ORDER BY p.tipo_tuberia, p.id_perfil_iow
            """
        )
        st.dataframe(df_iow, use_container_width=True, hide_index=True)

    with tab_series:
        df_vars_disp = leer_sql("SELECT DISTINCT id_tramo, id_variable FROM datos_validados ORDER BY id_tramo, id_variable")
        c1, c2 = st.columns(2)
        tramo_s = c1.selectbox("Tramo", df_vars_disp["id_tramo"].unique())
        vars_tramo = df_vars_disp[df_vars_disp["id_tramo"] == tramo_s]["id_variable"].unique()
        var_s = c2.selectbox("Variable", vars_tramo)

        df_serie = leer_sql(
            """
            SELECT fecha_hora, valor, unidad, calidad
            FROM datos_validados
            WHERE id_tramo = ? AND id_variable = ? AND calidad = 'GOOD'
            ORDER BY fecha_hora
            """,
            params=(tramo_s, var_s),
        )
        if not df_serie.empty:
            fig_ts = px.line(
                df_serie,
                x="fecha_hora",
                y="valor",
                title=f"Serie Validada: {tramo_s} - {var_s} ({df_serie['unidad'].iloc[0]})",
            )
            st.plotly_chart(fig_ts, use_container_width=True)


# ==========================================================
# MODULO 4: INFERENCIA BAYESIANA (C3)
# ==========================================================

elif pagina == "🧠 4. Inferencia Bayesiana (C3)":
    st.title("Actualización Bayesiana del Estado Latente de Degradación")

    df_bayes_ult = leer_sql(
        """
        WITH ultimo AS (
            SELECT id_tramo, id_mecanismo, MAX(fecha_hora) AS fecha_max
            FROM estado_bayes GROUP BY id_tramo, id_mecanismo
        )
        SELECT eb.id_tramo, eb.id_mecanismo, m.nombre AS mecanismo, eb.fecha_hora,
               ROUND(eb.posterior_bueno, 4) AS p_bueno,
               ROUND(eb.posterior_degradado, 4) AS p_degradado,
               ROUND(eb.posterior_severo, 4) AS p_severo,
               ROUND(eb.pof_actualizada, 5) AS pof_1y,
               ROUND(eb.incertidumbre_pof, 4) AS incertidumbre
        FROM estado_bayes eb
        INNER JOIN ultimo u ON eb.id_tramo = u.id_tramo AND eb.id_mecanismo = u.id_mecanismo AND eb.fecha_hora = u.fecha_max
        INNER JOIN mecanismos m ON eb.id_mecanismo = m.id_mecanismo
        ORDER BY eb.id_tramo, eb.id_mecanismo
        """
    )
    st.subheader("Estado Posterior al Cierre del Periodo")
    st.dataframe(df_bayes_ult, use_container_width=True, hide_index=True)

    st.subheader("Evolución Temporal del Belief State P(S_t | E_1:t)")
    c1, c2 = st.columns(2)
    tramo_b = c1.selectbox("Seleccionar Tramo", df_bayes_ult["id_tramo"].unique())
    mecs_b = df_bayes_ult[df_bayes_ult["id_tramo"] == tramo_b]
    mec_b = c2.selectbox(
        "Seleccionar Mecanismo",
        mecs_b["id_mecanismo"].tolist(),
        format_func=lambda x: f"{x} - {mecs_b[mecs_b['id_mecanismo']==x]['mecanismo'].iloc[0]}",
    )

    df_hist_bayes = leer_sql(
        """
        SELECT fecha_hora, posterior_bueno, posterior_degradado, posterior_severo, pof_actualizada
        FROM estado_bayes
        WHERE id_tramo = ? AND id_mecanismo = ?
        ORDER BY fecha_hora
        """,
        params=(tramo_b, mec_b),
    )

    if not df_hist_bayes.empty:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            df_area = df_hist_bayes.melt(
                id_vars="fecha_hora",
                value_vars=["posterior_bueno", "posterior_degradado", "posterior_severo"],
                var_name="Estado",
                value_name="Probabilidad",
            )
            fig_area = px.area(
                df_area,
                x="fecha_hora",
                y="Probabilidad",
                color="Estado",
                color_discrete_map={
                    "posterior_bueno": "#10b981",
                    "posterior_degradado": "#f59e0b",
                    "posterior_severo": "#ef4444",
                },
                title="Evolución de Probabilidades por Estado Latente",
            )
            st.plotly_chart(fig_area, use_container_width=True)

        with col_g2:
            fig_pof = px.line(
                df_hist_bayes,
                x="fecha_hora",
                y="pof_actualizada",
                title="Evolución de la PoF Dinámica (1 año)",
                markers=True,
            )
            fig_pof.update_traces(line_color="#dc2626")
            st.plotly_chart(fig_pof, use_container_width=True)


# ==========================================================
# MODULO 5: RIESGO DRBI E INSPECCION UT (C4)
# ==========================================================

elif pagina == "⚠️ 5. Riesgo DRBI e Inspección UT (C4)":
    st.title("Estado de Riesgo DRBI e Histórico de Espesores UT")

    df_drbi = leer_sql("SELECT * FROM vista_dss_ejecutiva ORDER BY riesgo DESC")
    st.subheader("Ranking DRBI por Mecanismo Gobernante")
    st.dataframe(df_drbi, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Mediciones de Espesor UT y Regresión de Velocidad de Corrosión (CR)")
    df_ut = leer_sql(
        """
        SELECT u.id_tramo, u.id_cml, u.fecha_inspeccion, u.espesor_medido_mm,
               u.incertidumbre_mm, t.espesor_nominal_mm, t.espesor_minimo_aprobado_mm
        FROM inspecciones_ut u
        INNER JOIN tramos t ON u.id_tramo = t.id_tramo
        ORDER BY u.id_tramo, u.fecha_inspeccion
        """
    )

    if not df_ut.empty:
        tramo_ut = st.selectbox("Seleccionar tramo para ver curva de desgaste UT:", df_ut["id_tramo"].unique())
        df_ut_tramo = df_ut[df_ut["id_tramo"] == tramo_ut]

        fig_ut = go.Figure()
        fig_ut.add_trace(go.Scatter(
            x=df_ut_tramo["fecha_inspeccion"],
            y=df_ut_tramo["espesor_medido_mm"],
            mode="lines+markers",
            name="Espesor Medido UT (mm)",
            line=dict(color="#2563eb", width=3),
        ))
        t_min_val = float(df_ut_tramo["espesor_minimo_aprobado_mm"].iloc[0])
        fig_ut.add_hline(
            y=t_min_val,
            line_dash="dash",
            line_color="#dc2626",
            annotation_text=f"t_min aprobado ({t_min_val} mm)",
        )
        fig_ut.update_layout(
            title=f"Degradación de Espesor vs Límite de Retiro ({tramo_ut})",
            xaxis_title="Fecha de Inspección",
            yaxis_title="Espesor (mm)",
            height=400,
        )
        st.plotly_chart(fig_ut, use_container_width=True)
        st.dataframe(df_ut_tramo, use_container_width=True, hide_index=True)


# ==========================================================
# MODULO 6: DECISION PRESCRIPTIVA Y VoI (C5)
# ==========================================================

elif pagina == "🎯 6. Decisión Prescriptiva y VoI (C5)":
    st.title("Motor Prescriptivo C5 — POMDP y Valor de la Información (VoI)")

    if not tabla_o_vista_existe("vista_c5_recomendacion_actual"):
        st.warning("La vista 'vista_c5_recomendacion_actual' no existe. Ejecuta las celdas C5–C7 en Colab.")
    else:
        df_c5_rec = leer_sql("SELECT * FROM vista_c5_recomendacion_actual ORDER BY costo_esperado_total_usd DESC")
        st.subheader("Recomendación Óptima por Tramo")
        st.dataframe(
            df_c5_rec[[
                "id_tramo", "accion_recomendada", "familia_accion",
                "costo_accion_usd", "costo_esperado_total_usd",
                "pof_residual", "riesgo_residual_usd_ano",
                "plazo_max_seguro_meses", "voi_usd"
            ]],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.subheader("Comparativa Completa de las 6 Alternativas por Tramo")
        tramo_c5 = st.selectbox("Seleccionar Tramo:", df_c5_rec["id_tramo"].unique())
        df_alt = leer_sql(
            """
            SELECT r.ranking, r.id_accion, a.nombre AS accion, r.cumple_seguridad,
                   r.costo_accion_usd, r.costo_riesgo_esperado_usd, r.costo_esperado_total_usd,
                   r.pof_residual, r.riesgo_residual_usd_ano, r.voi_usd, r.politica_posterior_json
            FROM resultados_c5 r
            INNER JOIN acciones_integridad_c5 a ON r.id_accion = a.id_accion
            WHERE r.id_tramo = ? AND r.snapshot = (SELECT MAX(snapshot) FROM resultados_c5)
            ORDER BY r.ranking
            """,
            params=(tramo_c5,),
        )
        st.dataframe(df_alt.drop(columns=["politica_posterior_json"]), use_container_width=True, hide_index=True)

        fig_c5 = px.bar(
            df_alt,
            x="accion",
            y=["costo_accion_usd", "costo_riesgo_esperado_usd"],
            title=f"Desglose de Costo Directo vs Riesgo Esperado ({tramo_c5})",
            barmode="stack",
            labels={"value": "USD", "accion": "Alternativa de Integridad"},
        )
        st.plotly_chart(fig_c5, use_container_width=True)

        fila_ins = df_alt[df_alt["id_accion"] == "A1_INS"]
        if not fila_ins.empty and fila_ins["politica_posterior_json"].iloc[0]:
            st.markdown("#### 🔍 Política Condicional Posterior si se realiza Inspección UT (`A1_INS`):")
            politica = json.loads(fila_ins["politica_posterior_json"].iloc[0])
            st.json(politica)


# ==========================================================
# MODULO 7: PROGRAMACION MILP + ROLLING HORIZON (C6)
# ==========================================================

elif pagina == "📅 7. Programación MILP + RH (C6)":
    st.title("Programación Multi-Periodo bajo Restricciones (MILP + Rolling Horizon)")

    if not tabla_o_vista_existe("vista_c6_programa_actual"):
        st.warning("No se encontró 'vista_c6_programa_actual'.")
    else:
        df_c6 = leer_sql(
            """
            SELECT * FROM vista_c6_programa_actual
            ORDER BY CASE WHEN mes_programado IS NULL THEN 999 ELSE mes_programado END, id_tramo
            """
        )
        st.subheader("Calendario Óptimo de Intervenciones Comprometido")
        st.dataframe(
            df_c6[[
                "id_tramo", "accion_programada", "familia_accion",
                "mes_programado", "fecha_programada", "plazo_max_seguro_meses",
                "costo_directo_usd", "hh", "indisponibilidad_h",
                "requiere_parada", "estado_programacion"
            ]],
            use_container_width=True,
            hide_index=True,
        )

        df_rec = leer_sql("SELECT * FROM recursos_c6 ORDER BY mes")
        if not df_rec.empty:
            st.divider()
            st.subheader("Utilización Mensual de Presupuesto y Horas-Hombre vs Capacidad")
            consumo = (
                df_c6[df_c6["mes_programado"].notna()]
                .groupby("mes_programado")
                .agg(
                    presupuesto_usado=("costo_directo_usd", "sum"),
                    hh_usadas=("hh", "sum"),
                    intervenciones=("id_tramo", "count"),
                )
                .reset_index()
                .rename(columns={"mes_programado": "mes"})
            )
            df_cap = df_rec.merge(consumo, on="mes", how="left").fillna(0)

            col1, col2 = st.columns(2)
            with col1:
                fig_pres = go.Figure()
                fig_pres.add_trace(go.Bar(x=df_cap["mes"], y=df_cap["presupuesto_usado"], name="Presupuesto Usado (USD)", marker_color="#2563eb"))
                fig_pres.add_trace(go.Scatter(x=df_cap["mes"], y=df_cap["presupuesto_usd"], name="Límite Mensual (USD)", line=dict(color="#dc2626", dash="dash")))
                fig_pres.update_layout(title="Presupuesto Mensual (USD)", xaxis_title="Mes del Plan", yaxis_title="USD")
                st.plotly_chart(fig_pres, use_container_width=True)

            with col2:
                fig_hh = go.Figure()
                fig_hh.add_trace(go.Bar(x=df_cap["mes"], y=df_cap["hh_usadas"], name="HH Programadas", marker_color="#10b981"))
                fig_hh.add_trace(go.Scatter(x=df_cap["mes"], y=df_cap["hh_disponibles"], name="HH Disponibles", line=dict(color="#dc2626", dash="dash")))
                fig_hh.update_layout(title="Carga de Horas-Hombre (HH)", xaxis_title="Mes del Plan", yaxis_title="Horas-Hombre")
                st.plotly_chart(fig_hh, use_container_width=True)

            st.dataframe(df_cap, use_container_width=True, hide_index=True)


# ==========================================================
# MODULO 8: EVALUACION BASELINE VS DSS (C7)
# ==========================================================

elif pagina == "📈 8. Evaluación Baseline vs DSS (C7)":
    st.title("Evaluación Contrafactual C7: Estrategia Baseline vs Programa DSS")

    if not tabla_o_vista_existe("vista_c7_evaluacion_actual"):
        st.warning("No se encontró 'vista_c7_evaluacion_actual'.")
    else:
        df_c7 = leer_sql("SELECT * FROM vista_c7_evaluacion_actual")

        def valor_ind(nombre_parcial, col="mejora_pct"):
            f = df_c7[df_c7["indicador"].str.contains(nombre_parcial, case=False, na=False)]
            return float(f[col].iloc[0]) if not f.empty and pd.notna(f[col].iloc[0]) else 0.0

        c1, c2, c3 = st.columns(3)
        c1.metric(
            "Reducción de Riesgo al Cierre",
            f"{valor_ind('Riesgo agregado'):.2f}%",
            delta=f"{valor_ind('Riesgo agregado', 'diferencia'):,.0f} USD/año",
            delta_color="inverse",
        )
        c2.metric(
            "Reducción de PoF Promedio",
            f"{valor_ind('PoF promedio'):.2f}%",
            delta=f"{valor_ind('PoF promedio', 'diferencia'):.5f}",
            delta_color="inverse",
        )
        c3.metric(
            "Ahorro en Costo Total Esperado",
            f"{valor_ind('Costo esperado total'):.2f}%",
            delta=f"{valor_ind('Costo esperado total', 'diferencia'):,.0f} USD",
            delta_color="inverse",
        )

        st.subheader("Tabla Comparativa de Indicadores C7")
        st.dataframe(df_c7, use_container_width=True, hide_index=True)

        df_comp_c7 = df_c7[df_c7["unidad"].isin(["USD/año", "USD"])].melt(
            id_vars="indicador",
            value_vars=["baseline", "dss"],
            var_name="Estrategia",
            value_name="Valor_USD",
        )
        fig_c7 = px.bar(
            df_comp_c7,
            x="indicador",
            y="Valor_USD",
            color="Estrategia",
            barmode="group",
            color_discrete_map={"baseline": "#64748b", "dss": "#2563eb"},
            title="Comparación Económica y de Riesgo: Baseline vs DSS",
        )
        st.plotly_chart(fig_c7, use_container_width=True)


# ==========================================================
# MODULO 9: VALIDACION INTEGRAL Y AUDITORIA
# ==========================================================

elif pagina == "✅ 9. Validación Integral y Auditoría":
    st.title("Auditoría y Validación Computacional Integral (C1 → C7)")

    tab_val, tab_aud = st.tabs([
        "✅ Matriz de Validación C1–C7",
        "📜 Bitácora de Auditoría",
    ])

    with tab_val:
        if tabla_o_vista_existe("vista_validacion_integral_actual"):
            df_val = leer_sql("SELECT * FROM vista_validacion_integral_actual")
            n_pass = int((df_val["estado"] == "PASS").sum())
            n_total = len(df_val)
            st.success(f"Cumplimiento de Validación Integral: {n_pass} / {n_total} pruebas en estado PASS ({100*n_pass/max(n_total,1):.1f}%)")
            st.dataframe(df_val, use_container_width=True, hide_index=True)
        else:
            st.info("Aún no se ha ejecutado la Celda 34 de validación integral.")

    with tab_aud:
        df_aud = leer_sql("SELECT * FROM auditoria ORDER BY id_evento DESC LIMIT 100")
        st.dataframe(df_aud, use_container_width=True, hide_index=True)


# ==========================================================
# DSS DRBI - IOWs - BAYES
# APP STREAMLIT
# VERSION 2.0
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
# ESTILOS
# ==========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        min-width: 250px;
        max-width: 250px;
    }

    .titulo-principal {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .subtitulo {
        color: #888888;
        margin-bottom: 1.5rem;
    }

    .panel {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.title(
        "DSS Integridad"
    )

    st.caption(
        "DRBI · IOWs · Bayes"
    )

    st.divider()


    pagina = st.radio(

        "Navegación",

        [
            "Dashboard",
            "Activos y Tramos",
            "IOW / Umbrales",
            "Bayes / PoF",
            "DRBI",
            "Inspecciones UT",
            "Fuentes de datos",
            "Configuración"
        ]

    )


    st.divider()

    st.caption(
        "Versión DSS: 2.0"
    )

    st.caption(
        "Modo: SIMULADO_ACADEMICO"
    )


# ==========================================================
# DASHBOARD
# ==========================================================

if pagina == "Dashboard":

    st.markdown(
        '<div class="titulo-principal">'
        'Dashboard de Integridad'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitulo">'
        'Monitoreo dinámico de riesgo e integridad de tuberías'
        '</div>',
        unsafe_allow_html=True
    )


    df = leer_sql(
        """
        SELECT *

        FROM vista_dss_ejecutiva
        """
    )


    if df.empty:

        st.warning(
            "No existen resultados DRBI disponibles."
        )

    else:

        c1, c2, c3, c4, c5 = st.columns(5)


        total = len(df)

        altos = int(
            (
                df[
                    "categoria_riesgo"
                ]
                == "ALTO"
            ).sum()
        )

        criticos = int(
            (
                df[
                    "categoria_riesgo"
                ]
                == "CRITICO"
            ).sum()
        )

        rul_min = float(
            df[
                "rul_anos"
            ].min()
        )

        riesgo_total = float(
            df[
                "riesgo"
            ].sum()
        )


        c1.metric(
            "Tramos",
            total
        )

        c2.metric(
            "Riesgo alto",
            altos
        )

        c3.metric(
            "Riesgo crítico",
            criticos
        )

        c4.metric(
            "RUL mínimo",
            f"{rul_min:.2f} años"
        )

        c5.metric(
            "Riesgo agregado",
            f"USD {riesgo_total:,.0f}/año"
        )


        st.subheader(
            "Priorización de tramos"
        )


        columnas = [

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

            "nivel_confianza"

        ]


        st.dataframe(

            df[
                columnas
            ],

            use_container_width=True,

            hide_index=True

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
        "**Versión:** 2.0"
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

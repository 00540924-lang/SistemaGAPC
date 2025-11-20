# modulos/prestamos.py
import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import datetime
import time

# -----------------------------
# Módulo principal: prestamos()
# -----------------------------
def prestamos():
    """
    Módulo principal para gestionar préstamos:
      - Muestra solo socios del grupo de la sesión
      - Permite crear préstamos
      - Permite agregar pagos a un préstamo seleccionado
      - Muestra la tabla de préstamos y pagos
    Requiere que st.session_state["id_grupo"] esté definido (lo hace tu login).
    """

    # 1) Validar sesión y grupo
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")

    st.markdown(f"<h2 style='text-align:center;'>💰 Préstamos - Grupo: {nombre_grupo}</h2>", unsafe_allow_html=True)

    # Opcional: mostrar imagen del formulario (si quieres)
    # st.image("/mnt/data/9f5a4869-bd34-4ee9-9d16-00cf25b9e8f1.png", use_column_width=True)

    # 2) Cargar socias del grupo
    miembros = _obtener_miembros_del_grupo(id_grupo)
    if not miembros:
        st.warning("No hay miembros registrados en este grupo.")
        return

    # Diccionario nombre -> id
    miembros_dict = {f"{m['Nombre']} (DUI: {m['DUI']})": m["ID"] for m in miembros}

    # 3) Seleccionar socia para registrar préstamo (o ver historial)
    col_a, col_b = st.columns([3,1])
    with col_a:
        socia_seleccionada = st.selectbox("Selecciona una socia:", options=list(miembros_dict.keys()))
    with col_b:
        ver_historial = st.button("Ver préstamos de socia")

    id_miembro = miembros_dict[socia_seleccionada]

    st.markdown("---")

    # 4) Formulario para crear nuevo préstamo
    st.subheader("Registrar nuevo préstamo")
    with st.form("form_prestamo"):
        fecha_desembolso = st.date_input("Fecha desembolso", value=datetime.date.today())
        fecha_vencimiento = st.date_input("Fecha vencimiento", value=(datetime.date.today() + datetime.timedelta(days=30)))
        proposito = st.text_input("Propósito")
        cantidad = st.number_input("Cantidad", min_value=0.01, step=0.01, format="%.2f")
        firma = st.text_input("Firma (nombre quien autoriza)", value="")
        guardar_prestamo = st.form_submit_button("Guardar préstamo")

    if guardar_prestamo:
        # Validaciones mínimas
        if cantidad <= 0:
            st.error("La cantidad debe ser mayor que 0.")
        else:
            id_prestamo = _crear_prestamo(id_miembro, id_grupo, fecha_desembolso, fecha_vencimiento, proposito, cantidad, firma)
            st.success(f"Préstamo registrado (ID: {id_prestamo})")
            time.sleep(0.4)
            # Al insertar, la app se vuelve a ejecutar por la interacción; los listados abajo tomarán el nuevo registro

    st.markdown("---")

    # 5) Listado de préstamos de la socia seleccionada
    st.subheader("Préstamos de la socia seleccionada")
    prestamos_df = _obtener_prestamos_por_miembro(id_miembro)

    if prestamos_df.empty:
        st.info("Esta socia no tiene préstamos registrados.")
    else:
        # Mostrar tabla sin índice extra (usamos st.table para evitar la columna índice)
        df_show = prestamos_df.copy()
        # Formato de fecha y montos
        df_show["fecha_desembolso"] = pd.to_datetime(df_show["fecha_desembolso"]).dt.date
        df_show["fecha_vencimiento"] = pd.to_datetime(df_show["fecha_vencimiento"]).dt.date
        df_show["cantidad"] = df_show["cantidad"].map(lambda x: f"{x:.2f}")
        st.table(df_show[["id_prestamo", "fecha_desembolso", "fecha_vencimiento", "proposito", "cantidad", "firma"]].rename(
            columns={
                "id_prestamo":"ID",
                "fecha_desembolso":"Desembolso",
                "fecha_vencimiento":"Vencimiento",
                "proposito":"Propósito",
                "cantidad":"Cantidad",
                "firma":"Firma"
            }
        ))

        # Seleccionar un préstamo para ver/agregar pagos
        prestamos_list = {f"ID {row['id_prestamo']} - {row['proposito']} - {row['cantidad']:.2f}": row["id_prestamo"] for _, row in prestamos_df.iterrows()}
        seleccionado_prestamo = st.selectbox("Selecciona un préstamo para ver/agregar pagos:", options=list(prestamos_list.keys()))
        id_prestamo_sel = prestamos_list[seleccionado_prestamo]

        # Mostrar detalles del préstamo seleccionado
        _mostrar_detalle_prestamo(id_prestamo_sel)

    # Si presionó ver historial, mostrar todos los préstamos del grupo (opcional)
    if ver_historial:
        st.markdown("---")
        st.subheader(f"Todos los préstamos del grupo {nombre_grupo}")
        prestamos_grupo = _obtener_prestamos_por_grupo(id_grupo)
        if prestamos_grupo.empty:
            st.info("No hay préstamos en el grupo.")
        else:
            st.table(prestamos_grupo[["id_prestamo","id_miembro","fecha_desembolso","fecha_vencimiento","proposito","cantidad"]].rename(
                columns={
                    "id_prestamo":"ID",
                    "id_miembro":"ID miembro",
                    "fecha_desembolso":"Desembolso",
                    "fecha_vencimiento":"Vencimiento",
                    "proposito":"Propósito",
                    "cantidad":"Cantidad"
                }
            ))


# -----------------------------
# FUNCIONES AUXILIARES (DB)
# -----------------------------
def _obtener_miembros_del_grupo(id_grupo):
    """Devuelve lista de dicts con ID, Nombre, DUI del grupo"""
    con = None
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT M.id_miembro, M.nombre, M.dui
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY M.nombre ASC
        """, (id_grupo,))
        rows = cursor.fetchall()
        # rows vienen como lista de tuplas -> convertir a list of dicts
        miembros = [{"ID": r[0], "Nombre": r[1], "DUI": r[2]} for r in rows]
        return miembros
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            if con:
                con.close()
        except:
            pass


def _crear_prestamo(id_miembro, id_grupo, fecha_desembolso, fecha_vencimiento, proposito, cantidad, firma):
    """Inserta un préstamo y devuelve el id_prestamo insertado"""
    con = None
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            INSERT INTO Prestamos (id_miembro, id_grupo, fecha_desembolso, fecha_vencimiento, proposito, cantidad, firma)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_miembro, id_grupo, fecha_desembolso, fecha_vencimiento, proposito, cantidad, firma))
        con.commit()
        # Obtener último id insertado
        try:
            id_prestamo = cursor.lastrowid
        except:
            # fallback si tu driver no soporta lastrowid
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_prestamo = cursor.fetchone()[0]
        return id_prestamo
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            if con:
                con.close()
        except:
            pass


def _obtener_prestamos_por_miembro(id_miembro):
    """Devuelve DataFrame con préstamos de un miembro"""
    con = None
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT id_prestamo, id_miembro, fecha_desembolso, fecha_vencimiento, proposito, cantidad, firma
            FROM Prestamos
            WHERE id_miembro = %s
            ORDER BY id_prestamo
        """, (id_miembro,))
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["id_prestamo", "id_miembro", "fecha_desembolso", "fecha_vencimiento", "proposito", "cantidad", "firma"])
        return df
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            if con:
                con.close()
        except:
            pass


def _obtener_prestamos_por_grupo(id_grupo):
    """Devuelve DataFrame con préstamos del grupo"""
    con = None
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT id_prestamo, id_miembro, fecha_desembolso, fecha_vencimiento, proposito, cantidad
            FROM Prestamos
            WHERE id_grupo = %s
            ORDER BY id_prestamo
        """, (id_grupo,))
        rows = cursor.fetchall()
        df = pd.DataFrame(rows, columns=["id_prestamo","id_miembro","fecha_desembolso","fecha_vencimiento","proposito","cantidad"])
        return df
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            if con:
                con.close()
        except:
            pass


# -----------------------------
# DETALLE PRESTAMO / PAGOS
# -----------------------------
def _mostrar_detalle_prestamo(id_prestamo):
    """Muestra detalle del préstamo, lista de pagos y formulario para agregar pagos"""
    st.markdown(f"### Detalle préstamo ID {id_prestamo}")

    # 1) Cargar préstamo
    prestamo_df = _get_prestamo(id_prestamo)
    if prestamo_df is None or prestamo_df.empty:
        st.error("No se encontró el préstamo.")
        return

    prestamo = prestamo_df.iloc[0].to_dict()
    st.write({
        "ID": prestamo["id_prestamo"],
        "Socia (ID)": prestamo["id_miembro"],
        "Desembolso": str(pd.to_datetime(prestamo["fecha_desembolso"]).date()),
        "Vencimiento": str(pd.to_datetime(prestamo["fecha_vencimiento"]).date()),
        "Propósito": prestamo["proposito"],
        "Cantidad": f"{prestamo['cantidad']:.2f}",
        "Firma": prestamo.get("firma", "")
    })

    # 2) Mostrar pagos existentes
    pagos_df = _get_pagos_por_prestamo(id_prestamo)
    if pagos_df.empty:
        st.info("Aún no hay pagos registrados para este préstamo.")
    else:
        pagos_df_display = pagos_df.copy()
        pagos_df_display["fecha"] = pd.to_datetime(pagos_df_display["fecha"]).dt.date
        pagos_df_display["capital"] = pagos_df_display["capital"].map(lambda x: f"{x:.2f}")
        pagos_df_display["interes"] = pagos_df_display["interes"].map(lambda x: f"{x:.2f}")
        pagos_df_display["total_pagado"] = pagos_df_display["total_pagado"].map(lambda x: f"{x:.2f}")
        st.table(pagos_df_display[["id_pago","fecha","capital","interes","total_pagado"]].rename(
            columns={"id_pago":"ID Pago","fecha":"Fecha","capital":"Capital","interes":"Interés","total_pagado":"Total pagado"}
        ))

    # 3) Totales
    totales = pagos_df[["capital","interes","total_pagado"]].sum() if not pagos_df.empty else pd.Series({"capital":0,"interes":0,"total_pagado":0})
    st.write(f"**Totales:** Capital: {totales.get('capital',0):.2f}  —  Interés: {totales.get('interes',0):.2f}  —  Total pagado: {totales.get('total_pagado',0):.2f}")

    st.markdown("---")

    # 4) Formulario para agregar pago
    st.subheader("Agregar pago")
    with st.form(f"form_pago_{id_prestamo}"):
        fecha_pago = st.date_input("Fecha de pago", value=datetime.date.today())
        capital = st.number_input("Capital pagado", min_value=0.0, step=0.01, format="%.2f")
        interes = st.number_input("Interés pagado", min_value=0.0, step=0.01, format="%.2f")
        total_pagado = st.number_input("Total pagado (opcional, se calculará si se deja 0)", min_value=0.0, step=0.01, format="%.2f", value=0.0)
        guardar = st.form_submit_button("Registrar pago")

    if guardar:
        if total_pagado == 0:
            total_pagado = round(float(capital) + float(interes), 2)
        _crear_pago(id_prestamo, fecha_pago, capital, interes, total_pagado)
        st.success("Pago registrado ✔️")
        time.sleep(0.3)
        # la interacción fuerza la re-ejecución y la lista se mostrará actualizada automáticamente


# -----------------------------
# OPERACIONES PAGOS / DB
# -----------------------------
def _get_prestamo(id_prestamo):
    con = None
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT id_prestamo, id_miembro, fecha_desembolso, fecha_vencimiento, proposito, cantidad, firma
            FROM Prestamos
            WHERE id_prestamo = %s
        """, (id_prestamo,))
        rows = cursor.fetchall()
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows, columns=["id_prestamo","id_miembro","fecha_desembolso","fecha_vencimiento","proposito","cantidad","firma"])
        return df
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            if con:
                con.close()
        except:
            pass


def _get_pagos_por_prestamo(id_prestamo):
    con = None
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT id_pago, id_prestamo, fecha, capital, interes, total_pagado
            FROM PrestamosPagos
            WHERE id_prestamo = %s
            ORDER BY id_pago
        """, (id_prestamo,))
        rows = cursor.fetchall()
        if not rows:
            return pd.DataFrame(columns=["id_pago","id_prestamo","fecha","capital","interes","total_pagado"])
        df = pd.DataFrame(rows, columns=["id_pago","id_prestamo","fecha","capital","interes","total_pagado"])
        return df
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            if con:
                con.close()
        except:
            pass


def _crear_pago(id_prestamo, fecha, capital, interes, total_pagado):
    con = None
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            INSERT INTO PrestamosPagos (id_prestamo, fecha, capital, interes, total_pagado)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_prestamo, fecha, capital, interes, total_pagado))
        con.commit()
        try:
            id_pago = cursor.lastrowid
        except:
            cursor.execute("SELECT LAST_INSERT_ID()")
            id_pago = cursor.fetchone()[0]
        return id_pago
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            if con:
                con.close()
        except:
            pass

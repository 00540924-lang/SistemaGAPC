# modulo_prestamo.py
import streamlit as st
import mysql.connector
from mysql.connector import Error
from datetime import date, datetime

# --------------------------
# CONFIG - cambia según tu entorno
# --------------------------
DB_CONFIG = {
    "host": "bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
    "user": "uiazxdhtd3r8o7uv",
    "password": "uGjZ9MXWemv7vPsjOdA5",
    "database": "bzn5gsi7ken7lufcglbg"
}

# --------------------------
# UTIL: conexión
# --------------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        st.error(f"Error conectando a la base de datos: {e}")
        return None

# --------------------------
# UTIL: asegurar tablas
# --------------------------
def ensure_tables(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prestamos (
        id_prestamo INT AUTO_INCREMENT PRIMARY KEY,
        id_miembro INT NOT NULL,
        monto DECIMAL(15,2) NOT NULL,
        proposito VARCHAR(255),
        fecha_desembolso DATE,
        fecha_vencimiento DATE,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prestamo_pagos (
        id_pago INT AUTO_INCREMENT PRIMARY KEY,
        id_prestamo INT NOT NULL,
        numero_pago INT NOT NULL,
        fecha_programada DATE,
        capital DECIMAL(15,2),
        interes DECIMAL(15,2),
        estado ENUM('a pagar','pagado') DEFAULT 'a pagar',
        fecha_pagado DATE NULL,
        capital_pagado DECIMAL(15,2) DEFAULT 0,
        interes_pagado DECIMAL(15,2) DEFAULT 0,
        fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (id_prestamo) REFERENCES prestamos(id_prestamo) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """)
    conn.commit()
    cursor.close()

# --------------------------
# Obtener miembros del grupo
# --------------------------
def fetch_miembros_por_grupo(conn, id_grupo):
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT m.id_miembro, m.Nombre
        FROM Miembros m
        JOIN Grupomiembros gm ON m.id_miembro = gm.id_miembro
        WHERE gm.id_grupo = %s
        ORDER BY m.Nombre
    """
    cursor.execute(query, (id_grupo,))
    rows = cursor.fetchall()
    cursor.close()
    return rows

# --------------------------
# Insertar prestamo y pagos
# --------------------------
def insertar_prestamo_y_pagos(conn, id_miembro, monto, proposito, fecha_desembolso, fecha_vencimiento, pagos):
    cursor = conn.cursor()
    insert_prestamo = """
        INSERT INTO prestamos (id_miembro, monto, proposito, fecha_desembolso, fecha_vencimiento)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_prestamo, (id_miembro, monto, proposito, fecha_desembolso, fecha_vencimiento))
    id_prestamo = cursor.lastrowid

    insert_pago = """
        INSERT INTO prestamo_pagos
        (id_prestamo, numero_pago, fecha_programada, capital, interes, estado, fecha_pagado, capital_pagado, interes_pagado)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    for p in pagos:
        cursor.execute(insert_pago, (
            id_prestamo,
            p["numero"],
            p["fecha_programada"] if p["fecha_programada"] else None,
            p["capital"] if p["capital"] is not None else 0,
            p["interes"] if p["interes"] is not None else 0,
            p["estado"],
            p["fecha_pagado"] if p.get("fecha_pagado") else None,
            p.get("capital_pagado", 0),
            p.get("interes_pagado", 0)
        ))
    conn.commit()
    cursor.close()
    return id_prestamo

# --------------------------
# INTERFAZ STREAMLIT
# --------------------------
def modulo_prestamo():

    st.header("📄 Módulo de Préstamo (con plan de pagos variable)")

    # Requiere que el sistema haya guardado el grupo del usuario en session_state
    grupo_usuario = st.session_state.get("grupo", None)
    if not grupo_usuario:
        st.error("No se detectó el grupo del usuario en session_state. Asegúrate de iniciar sesión correctamente.")
        st.stop()

    conn = get_db_connection()
    if not conn:
        st.stop()

    ensure_tables(conn)

    # Obtener lista de miembros del grupo
    miembros = fetch_miembros_por_grupo(conn, grupo_usuario)
    if not miembros:
        st.warning("No se encontraron miembros para tu grupo.")
        conn.close()
        st.stop()

    # Map id <-> nombre
    miembros_map = {m["Nombre"]: m["id_miembro"] for m in miembros}
    nombres = list(miembros_map.keys())

    # Formulario principal
    with st.form("form_prestamo_general"):
        col1, col2 = st.columns(2)
        with col1:
            socio_nombre = st.selectbox("Seleccione el socio/miembro", nombres)
            monto = st.number_input("Monto del préstamo", min_value=0.0, step=0.01, format="%.2f")
            proposito = st.text_input("Propósito")
        with col2:
            fecha_desembolso = st.date_input("Fecha de desembolso", value=date.today())
            fecha_vencimiento = st.date_input("Fecha de vencimiento", value=date.today())
            id_socio_selected = miembros_map[socio_nombre]

        # Control de número de cuotas (variable)
        st.markdown("### Configurar cuotas / pagos")
        num_default = st.session_state.get("num_pagos_default", 6)
        columnas = st.columns(3)
        numero_pagos = columnas[0].number_input("Número de pagos (filas)", min_value=1, value=num_default, step=1)
        columnas[1].button("Usar valor por defecto (6)", on_click=lambda: st.session_state.update(num_pagos_default=6))
        columnas[2].info("Puedes cambiar el número aquí y luego editar cada fila abajo.")

        submit_main = st.form_submit_button("✔️ Crear plan de pagos editable")

    # Inicializar la estructura de pagos en session_state si no existe o si cambió el número de pagos
    if "pagos" not in st.session_state or len(st.session_state["pagos"]) != int(numero_pagos):
        # crear lista de pagos con valores por defecto
        pagos_init = []
        for i in range(1, int(numero_pagos) + 1):
            pagos_init.append({
                "numero": i,
                "fecha_programada": None,
                "capital": round(monto / int(numero_pagos) if numero_pagos else 0, 2),
                "interes": 0.0,
                "estado": "a pagar",
                "fecha_pagado": None,
                "capital_pagado": 0.0,
                "interes_pagado": 0.0
            })
        st.session_state["pagos"] = pagos_init

    st.markdown("---")
    st.subheader("✏️ Edición de cada pago")

    # Mostrar y editar cada fila de pago
    pagos = st.session_state["pagos"]
    suma_total_programado = 0.0
    suma_total_pagado = 0.0

    for idx, p in enumerate(pagos):
        st.markdown(f"**Pago #{p['numero']}**")
        c1, c2, c3, c4 = st.columns([2,2,2,1])

        with c1:
            fecha_prog = st.date_input(f"Fecha programada #{p['numero']}", value=(p["fecha_programada"] or date.today()), key=f"fecha_prog_{idx}")
            pagos[idx]["fecha_programada"] = fecha_prog

        with c2:
            cap = st.number_input(f"Capital (programado) #{p['numero']}", min_value=0.0, value=float(p["capital"]), step=0.01, format="%.2f", key=f"cap_prog_{idx}")
            pagos[idx]["capital"] = cap

        with c3:
            inte = st.number_input(f"Interés (programado) #{p['numero']}", min_value=0.0, value=float(p["interes"]), step=0.01, format="%.2f", key=f"int_prog_{idx}")
            pagos[idx]["interes"] = inte

        with c4:
            estado = st.selectbox(f"Estado #{p['numero']}", options=["a pagar", "pagado"], index=0 if p["estado"] == "a pagar" else 1, key=f"estado_{idx}")
            pagos[idx]["estado"] = estado

        # Si está pagado, permitir ingresar fecha y montos pagados
        if pagos[idx]["estado"] == "pagado":
            d1, d2, d3 = st.columns(3)
            with d1:
                fecha_pag = st.date_input(f"Fecha pagado #{p['numero']}", value=(p.get("fecha_pagado") or date.today()), key=f"fecha_pag_{idx}")
                pagos[idx]["fecha_pagado"] = fecha_pag
            with d2:
                cap_pag = st.number_input(f"Capital pagado #{p['numero']}", min_value=0.0, value=float(p.get("capital_pagado", 0.0)), step=0.01, format="%.2f", key=f"cap_pag_{idx}")
                pagos[idx]["capital_pagado"] = cap_pag
            with d3:
                int_pag = st.number_input(f"Interés pagado #{p['numero']}", min_value=0.0, value=float(p.get("interes_pagado", 0.0)), step=0.01, format="%.2f", key=f"int_pag_{idx}")
                pagos[idx]["interes_pagado"] = int_pag
        else:
            # limpiar valores de pagado si vuelve a 'a pagar'
            pagos[idx]["fecha_pagado"] = None
            pagos[idx]["capital_pagado"] = 0.0
            pagos[idx]["interes_pagado"] = 0.0

        total_programado = float(pagos[idx]["capital"]) + float(pagos[idx]["interes"])
        total_pagado_row = float(pagos[idx].get("capital_pagado", 0.0)) + float(pagos[idx].get("interes_pagado", 0.0))

        st.markdown(f"- **Total programado (fila #{p['numero']}):** {total_programado:.2f}  —  **Total pagado (fila #{p['numero']}):** {total_pagado_row:.2f}")
        suma_total_programado += total_programado
        suma_total_pagado += total_pagado_row
        st.markdown("---")

    # Mostrar resumen
    st.subheader("📊 Resumen")
    st.write(f"Monto del préstamo: {monto:.2f}")
    st.write(f"Suma total programada (capital+interés): {suma_total_programado:.2f}")
    st.write(f"Suma total efectivamente pagada: {suma_total_pagado:.2f}")

    # Botones globales para guardar en BD
    if st.button("💾 Guardar préstamo y pagos en la base de datos"):
        try:
            conn = get_db_connection()
            if not conn:
                st.error("No se pudo conectar a la base de datos.")
            else:
                ensure_tables(conn)
                # preparar lista de pagos para insertar (usar valores actuales en session_state)
                pagos_para_bd = []
                for p in st.session_state["pagos"]:
                    pagos_para_bd.append({
                        "numero": p["numero"],
                        "fecha_programada": p["fecha_programada"],
                        "capital": float(p["capital"]) if p["capital"] is not None else 0.0,
                        "interes": float(p["interes"]) if p["interes"] is not None else 0.0,
                        "estado": p["estado"],
                        "fecha_pagado": p.get("fecha_pagado"),
                        "capital_pagado": float(p.get("capital_pagado", 0.0)),
                        "interes_pagado": float(p.get("interes_pagado", 0.0))
                    })

                id_prestamo = insertar_prestamo_y_pagos(
                    conn,
                    id_socio_selected,
                    float(monto),
                    proposito,
                    fecha_desembolso,
                    fecha_vencimiento,
                    pagos_para_bd
                )
                st.success(f"Préstamo guardado con éxito. ID préstamo: {id_prestamo}")
        except Exception as e:
            st.error(f"Ocurrió un error al guardar: {e}")

    # Cerrar conexión
    if conn and conn.is_connected():
        conn.close()

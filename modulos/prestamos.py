# modulos/prestamos/prestamos.py
import streamlit as st
import mysql.connector
from datetime import date
from datetime import datetime

# -------------------------
# Conexión a la base de datos
# -------------------------
def get_connection():
    return mysql.connector.connect(
        host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
        user="uiazxdhtd3r8o7uv",
        password="uGjZ9MXWemv7vPsjOdA5",
        database="bzn5gsi7ken7lufcglbg"
    )

# -------------------------
# Módulo préstamos
# -------------------------
def prestamos_modulo():
    st.title("FORMULARIO DE PRÉSTAMO")
    # mostrar imagen de referencia (opcional)
    try:
        st.image("/mnt/data/294bdc9e-e055-42b7-b445-0bed184052e8.png", use_column_width=True)
    except Exception:
        pass

    # validar grupo en sesión
    id_grupo = st.session_state.get("id_grupo", None)
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")
    if not id_grupo:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    st.markdown(f"<h3 style='text-align:center;'>📌 Grupo: {nombre_grupo}</h3>", unsafe_allow_html=True)

    # conectar y cargar miembros del grupo
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT Miembros.id_miembro, Miembros.Nombre
            FROM Grupomiembros
            JOIN Miembros ON Grupomiembros.id_miembro = Miembros.id_miembro
            WHERE Grupomiembros.id_grupo = %s
            ORDER BY Miembros.Nombre
        """, (id_grupo,))
        miembros = cursor.fetchall()  # lista de tuplas (id_miembro, Nombre)
    except mysql.connector.Error as e:
        st.error(f"❌ Error al cargar miembros: {e}")
        cursor.close()
        conn.close()
        return

    if not miembros:
        st.info("No hay miembros en este grupo para crear préstamos.")
        cursor.close()
        conn.close()
        return

    # convertir a dict nombre -> id
    miembros_dict = {row[1]: row[0] for row in miembros}

    # ===========================
    # FORMULARIO PRINCIPAL (dentro de st.form)
    # ===========================
    st.markdown("### 📄 Nuevo préstamo")
    with st.form("form_prestamo"):
        # fila superior (Fecha / Socia)
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            # Fecha del formulario (puede interpretarse como fecha de registro o desembolso)
            fecha_form = st.date_input("Fecha", value=date.today(), key="fecha_form")
        with col2:
            socio_sel = st.selectbox("Socia / Miembro", options=list(miembros_dict.keys()))
        with col3:
            # espacio auxiliar
            st.write(" ")

        # segunda fila (desemb., vencim., firma)
        col4, col5, col6 = st.columns(3)
        with col4:
            fecha_desembolso = st.date_input("desemb.", value=date.today(), key="fecha_desembolso")
        with col5:
            fecha_vencimiento = st.date_input("vencim.", value=date.today(), key="fecha_vencimiento")
        with col6:
            firma = st.text_input("Firma (opcional)", key="firma")

        # propósito y cantidad
        proposito = st.text_input("Proposito:", key="proposito")
        monto = st.number_input("Cantidad (monto):", min_value=0.0, step=0.01, format="%.2f", key="monto")

        st.markdown("#### Plan de pagos (defínelo aquí)")
        # pedir número de filas de pago (cuotas)
        num_pagos = st.number_input("Número de pagos:", min_value=1, step=1, value=1, key="num_pagos")

        # crear inputs para cada pago (dentro del form para que se envíen juntos)
        pagos_temp = []
        suma_total = 0.0
        for i in range(int(num_pagos)):
            st.markdown(f"**Pago #{i+1}**")
            p_col1, p_col2, p_col3, p_col4 = st.columns([2,2,2,1])
            with p_col1:
                fecha_pago = st.date_input(f"Fecha pago #{i+1}", value=date.today(), key=f"fecha_pago_{i}")
            with p_col2:
                capital = st.number_input(f"Capital #{i+1}", min_value=0.0, step=0.01, format="%.2f", key=f"capital_{i}")
            with p_col3:
                interes = st.number_input(f"Interés #{i+1}", min_value=0.0, step=0.01, format="%.2f", key=f"interes_{i}")
            with p_col4:
                estado = st.selectbox(f"Estado #{i+1}", options=["a pagar", "pagado"], index=0, key=f"estado_{i}")

            total_row = float(capital) + float(interes)
            suma_total += total_row
            st.write(f"- Total (fila #{i+1}): {total_row:.2f}")
            pagos_temp.append({
                "numero": i+1,
                "fecha": fecha_pago,
                "capital": float(capital),
                "interes": float(interes),
                "estado": estado
            })
            st.markdown("---")

        st.markdown(f"**Suma total programada (capital + interés): {suma_total:.2f}**")

        submitted = st.form_submit_button("💾 Crear préstamo")

    # ===========================
    # Procesar envío: insertar préstamo + pagos
    # ===========================
    if submitted:
        if monto <= 0:
            st.error("El monto del préstamo debe ser mayor que 0.")
        else:
            try:
                id_miembro = miembros_dict[socio_sel]

                # insertar préstamo
                cursor.execute("""
                    INSERT INTO prestamos (id_miembro, proposito, monto, fecha_desembolso, fecha_vencimiento, firma, fecha_creacion)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    id_miembro,
                    proposito,
                    float(monto),
                    fecha_desembolso.strftime("%Y-%m-%d"),
                    fecha_vencimiento.strftime("%Y-%m-%d"),
                    firma,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
                conn.commit()
                id_prestamo = cursor.lastrowid

                # insertar pagos
                for p in pagos_temp:
                    cursor.execute("""
                        INSERT INTO prestamo_pagos (id_prestamo, numero_pago, fecha, capital, interes, estado, fecha_creacion)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        id_prestamo,
                        int(p["numero"]),
                        p["fecha"].strftime("%Y-%m-%d"),
                        float(p["capital"]),
                        float(p["interes"]),
                        p["estado"],
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                conn.commit()

                st.success("Préstamo y plan de pagos guardados correctamente ✔️")

            except mysql.connector.Error as e:
                conn.rollback()
                st.error(f"❌ Error al guardar en la base de datos: {e}")

    # ===========================
    # Botón regresar (fuera del form)
    # ===========================
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.experimental_rerun()

    # ===========================
    # Mostrar tabla de préstamos del grupo (breve)
    # ===========================
    mostrar_tabla_prestamos(id_grupo, conn)

    # cerrar recursos (mostrar_tabla_prestamos no debe cerrar conn)
    try:
        cursor.close()
    except:
        pass
    try:
        conn.close()
    except:
        pass


# ---------------------------
# Función para listar préstamos
# ---------------------------
def mostrar_tabla_prestamos(id_grupo, external_conn=None):
    """
    Muestra préstamos del grupo. Si se pasa external_conn la función la usa;
    si no, abre/cierra su propia conexión.
    """
    close_after = False
    if external_conn is None:
        conn = get_connection()
        close_after = True
    else:
        conn = external_conn

    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT P.id_prestamo, M.Nombre, P.proposito, P.monto, P.fecha_desembolso, P.fecha_vencimiento, P.estado
            FROM prestamos P
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY P.id_prestamo DESC
        """, (id_grupo,))
        rows = cursor.fetchall()
        if not rows:
            st.info("No hay préstamos registrados en este grupo.")
            return

        import pandas as pd
        df = pd.DataFrame(rows, columns=["ID", "Miembro", "Propósito", "Monto", "Fecha desemb.", "Fecha vencim.", "Estado"])
        df_display = df.reset_index(drop=True)
        df_display.insert(0, "No.", range(1, len(df_display) + 1))
        st.markdown("<h3 style='text-align:center;'>📄 Préstamos Registrados</h3>", unsafe_allow_html=True)
        st.dataframe(df_display[["No.", "Miembro", "Propósito", "Monto", "Fecha desemb.", "Fecha vencim.", "Estado"]], use_container_width=True)

    except mysql.connector.Error as e:
        st.error(f"❌ Error al cargar préstamos: {e}")
    finally:
        try:
            cursor.close()
        except:
            pass
        if close_after:
            try:
                conn.close()
            except:
                pass



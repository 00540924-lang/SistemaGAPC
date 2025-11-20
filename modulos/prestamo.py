# modulos/prestamos/prestamos.py
import streamlit as st
import pandas as pd
import time
from datetime import date
from modulos.config.conexion import obtener_conexion

# ================================
# MÓDULO PRESTAMOS
# ================================
def prestamos_modulo():
    # ============= validar sesión y grupo =============
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")

    st.markdown(f"<h2 style='text-align:center;'>📌 Grupo: {nombre_grupo}</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🏦 Gestión de Préstamos</h1>", unsafe_allow_html=True)

    # imagen de referencia (opcional; se ignora si no existe)
    try:
        st.image("/mnt/data/2013d973-988f-4087-ad4d-c93023046c52.png", use_column_width=True)
    except Exception:
        pass

    # ============= editar préstamo (flujo) =============
    if "editar_prestamo" in st.session_state:
        editar_prestamo(st.session_state["editar_prestamo"])
        return

    # ============= asegurar tablas en BD =============
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        # tabla prestamos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prestamos (
            id_prestamo INT AUTO_INCREMENT PRIMARY KEY,
            id_miembro INT NOT NULL,
            proposito VARCHAR(255),
            monto DECIMAL(14,2) NOT NULL,
            fecha_desembolso DATE NOT NULL,
            fecha_vencimiento DATE NOT NULL,
            firma VARCHAR(255),
            estado ENUM('activo','finalizado') DEFAULT 'activo',
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
        ) ENGINE=InnoDB;
        """)
        # tabla prestamo_pagos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prestamo_pagos (
            id_pago INT AUTO_INCREMENT PRIMARY KEY,
            id_prestamo INT NOT NULL,
            numero_pago INT NOT NULL,
            fecha DATE,
            capital DECIMAL(14,2) DEFAULT 0,
            interes DECIMAL(14,2) DEFAULT 0,
            estado ENUM('a pagar','pagado') DEFAULT 'a pagar',
            fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_prestamo) REFERENCES prestamos(id_prestamo) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB;
        """)
        con.commit()
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            con.close()
        except:
            pass

    # ============= cargar miembros del grupo =============
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT M.id_miembro, M.nombre
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY M.nombre
        """, (id_grupo,))
        miembros = cursor.fetchall()  # lista de tuplas (id, nombre)
        # convertir a dict {nombre: id}
        miembro_dict = {nombre: id_miembro for id_miembro, nombre in miembros}
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            con.close()
        except:
            pass

    if not miembros:
        st.info("No hay miembros en este grupo para crear préstamos.")
        return

    # ============= formulario principal (crear préstamo) =============
    st.markdown("### 📄 Nuevo préstamo")
    with st.form("form_prestamo"):
        col1, col2 = st.columns(2)
        with col1:
            miembro_sel = st.selectbox("Selecciona un miembro", options=list(miembro_dict.keys()))
            monto = st.number_input("Monto del préstamo", min_value=0.0, step=0.01, format="%.2f")
            proposito = st.text_input("Propósito")
        with col2:
            fecha_desembolso = st.date_input("Fecha de desembolso", value=date.today())
            fecha_vencimiento = st.date_input("Fecha de vencimiento", value=date.today())
            firma = st.text_input("Firma (opcional)")

        st.markdown("#### Plan de pagos (dinámico)")
        # inicializar lista de pagos temporal en session_state si no existe
        if "prestamo_pagos_temp" not in st.session_state:
            st.session_state["prestamo_pagos_temp"] = []

        # controles para añadir/quitar filas
        c1, c2, c3 = st.columns([1,1,2])
        if c1.button("➕ Agregar fila de pago"):
            lista = st.session_state["prestamo_pagos_temp"]
            numero = len(lista) + 1
            lista.append({
                "numero": numero,
                "fecha": date.today(),
                "capital": 0.0,
                "interes": 0.0,
                "estado": "a pagar"
            })
            st.session_state["prestamo_pagos_temp"] = lista
            st.experimental_rerun()
        if c2.button("➖ Quitar última fila"):
            lista = st.session_state["prestamo_pagos_temp"]
            if lista:
                lista.pop()
                # reenumerar
                for idx, item in enumerate(lista, start=1):
                    item["numero"] = idx
                st.session_state["prestamo_pagos_temp"] = lista
            st.experimental_rerun()
        c3.info("Agrega tantas filas de pago como necesites. Luego edítalas abajo.")

        submitted = st.form_submit_button("💾 Crear préstamo")

    # mostrar edición de filas de pagos fuera del form para permitir inputs dinámicos
    if st.session_state.get("prestamo_pagos_temp"):
        st.markdown("---")
        st.subheader("✏️ Editar plan de pagos")
        pagos = st.session_state["prestamo_pagos_temp"]
        suma_prog = 0.0
        for idx, p in enumerate(pagos):
            st.markdown(f"**Pago #{p['numero']}**")
            a, b, c, d = st.columns([2,2,2,1])
            with a:
                fecha_val = st.date_input(f"Fecha #{p['numero']}", value=p.get("fecha", date.today()), key=f"fecha_pago_{idx}")
                pagos[idx]["fecha"] = fecha_val
            with b:
                cap = st.number_input(f"Capital #{p['numero']}", min_value=0.0, value=float(p.get("capital", 0.0)), step=0.01, format="%.2f", key=f"cap_{idx}")
                pagos[idx]["capital"] = cap
            with c:
                inte = st.number_input(f"Interés #{p['numero']}", min_value=0.0, value=float(p.get("interes", 0.0)), step=0.01, format="%.2f", key=f"int_{idx}")
                pagos[idx]["interes"] = inte
            with d:
                estado = st.selectbox(f"Estado #{p['numero']}", options=["a pagar","pagado"], index=0 if p.get("estado","a pagar")=="a pagar" else 1, key=f"estado_{idx}")
                pagos[idx]["estado"] = estado

            total_row = float(pagos[idx]["capital"]) + float(pagos[idx]["interes"])
            st.markdown(f"- **Total (fila #{p['numero']}):** {total_row:.2f}")
            suma_prog += total_row
            st.markdown("---")

        st.subheader("📊 Resumen del plan")
        st.write(f"Suma total programada (capital + interés): {suma_prog:.2f}")

    # ============= procesar creación =============
    if submitted:
        if monto <= 0:
            st.error("El monto del préstamo debe ser mayor que 0.")
        else:
            try:
                con = obtener_conexion()
                cursor = con.cursor()
                # insertar prestamo
                cursor.execute("""
                    INSERT INTO prestamos (id_miembro, proposito, monto, fecha_desembolso, fecha_vencimiento, firma)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (miembro_dict[miembro_sel], proposito, monto, fecha_desembolso.strftime("%Y-%m-%d"),
                      fecha_vencimiento.strftime("%Y-%m-%d"), firma))
                id_prestamo = cursor.lastrowid

                # insertar pagos
                pagos_para_bd = st.session_state.get("prestamo_pagos_temp", [])
                if pagos_para_bd:
                    for p in pagos_para_bd:
                        cursor.execute("""
                            INSERT INTO prestamo_pagos (id_prestamo, numero_pago, fecha, capital, interes, estado)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (id_prestamo, p["numero"], p["fecha"].strftime("%Y-%m-%d"),
                              float(p["capital"]), float(p["interes"]), p["estado"]))
                else:
                    # Si no hay filas creadas, crear 1 fila por defecto con todo el monto
                    cursor.execute("""
                        INSERT INTO prestamo_pagos (id_prestamo, numero_pago, fecha, capital, interes, estado)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (id_prestamo, 1, date.today().strftime("%Y-%m-%d"), float(monto), 0.0, "a pagar"))

                con.commit()
                st.success("Préstamo y plan de pagos guardados correctamente ✔️")
                # limpiar temp
                st.session_state.pop("prestamo_pagos_temp", None)
                time.sleep(0.5)
                st.experimental_rerun()
            finally:
                try:
                    cursor.close()
                except:
                    pass
                try:
                    con.close()
                except:
                    pass

    # ============= botones regresar =============
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.experimental_rerun()

    st.write("---")
    # ============= mostrar tabla de prestamos =============
    mostrar_tabla_prestamos(id_grupo)


# ============================= FUNCIONES AUXILIARES =============================
def mostrar_tabla_prestamos(id_grupo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT P.id_prestamo, M.nombre, P.proposito, P.monto, P.fecha_desembolso, P.fecha_vencimiento, P.firma, P.estado
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

        df = pd.DataFrame(rows, columns=["ID", "Miembro", "Propósito", "Monto", "Fecha desemb.", "Fecha vencim.", "Firma", "Estado"])
        df_display = df.reset_index(drop=True)
        df_display.insert(0, "No.", range(1, len(df_display) + 1))

        st.markdown("<h3 style='text-align:center;'>📄 Préstamos Registrados</h3>", unsafe_allow_html=True)
        st.dataframe(df_display[["No.", "Miembro", "Propósito", "Monto", "Fecha desemb.", "Fecha vencim.", "Estado"]].style.hide(axis="index"), use_container_width=True)

        # selección para acciones (ver detalle / editar / eliminar)
        prestamo_dict = {f"{row['Miembro']} - {row['Propósito']} - {row['Fecha desemb.']}": row for _, row in df.iterrows()}
        seleccionado = st.selectbox("Selecciona un préstamo", options=list(prestamo_dict.keys()))

        if seleccionado:
            prest = prestamo_dict[seleccionado]
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔎 Ver detalle", key=f"ver_{prest['ID']}"):
                    mostrar_detalle_prestamo(prest["ID"])
            with col2:
                if st.button("✏️ Editar", key=f"editar_{prest['ID']}"):
                    # cargar datos para editar
                    st.session_state["editar_prestamo"] = prest
                    st.experimental_rerun()
            with col3:
                if st.button("🗑️ Eliminar", key=f"eliminar_{prest['ID']}"):
                    eliminar_prestamo(prest["ID"])
                    st.success("Préstamo eliminado ✔️")
                    time.sleep(0.5)
                    st.experimental_rerun()
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            con.close()
        except:
            pass

def mostrar_detalle_prestamo(id_prestamo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("""
            SELECT P.id_prestamo, M.nombre, P.proposito, P.monto, P.fecha_desembolso, P.fecha_vencimiento, P.firma, P.estado
            FROM prestamos P
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            WHERE P.id_prestamo = %s
        """, (id_prestamo,))
        prest = cursor.fetchone()
        if not prest:
            st.error("Préstamo no encontrado.")
            return

        st.markdown(f"### 📌 Detalle préstamo ID {prest[0]}")
        st.write(f"**Miembro:** {prest[1]}")
        st.write(f"**Propósito:** {prest[2]}")
        st.write(f"**Monto:** {float(prest[3]):.2f}")
        st.write(f"**Fecha desembolso:** {prest[4]}")
        st.write(f"**Fecha vencimiento:** {prest[5]}")
        st.write(f"**Firma:** {prest[6]}")
        st.write(f"**Estado:** {prest[7]}")

        # traer pagos
        cursor.execute("""
            SELECT numero_pago, fecha, capital, interes, estado
            FROM prestamo_pagos
            WHERE id_prestamo = %s
            ORDER BY numero_pago
        """, (id_prestamo,))
        pagos = cursor.fetchall()
        if pagos:
            dfp = pd.DataFrame(pagos, columns=["No.", "Fecha", "Capital", "Interés", "Estado"])
            st.markdown("#### 📋 Plan de pagos")
            st.dataframe(dfp.style.hide(axis="index"), use_container_width=True)
        else:
            st.info("No hay pagos registrados para este préstamo.")
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            con.close()
        except:
            pass

def eliminar_prestamo(id_prestamo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("DELETE FROM prestamos WHERE id_prestamo = %s", (id_prestamo,))
        con.commit()
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            con.close()
        except:
            pass

def editar_prestamo(prest):
    # prest es una fila del df con columnas ID, Miembro, Propósito, ...
    st.markdown(f"<h3>✏️ Editando préstamo ID {prest['ID']} - {prest['Miembro']}</h3>", unsafe_allow_html=True)

    try:
        # obtener datos actuales del préstamo y sus pagos
        con = obtener_conexion()
        cursor = con.cursor()
        cursor.execute("SELECT id_miembro, proposito, monto, fecha_desembolso, fecha_vencimiento, firma, estado FROM prestamos WHERE id_prestamo = %s", (prest['ID'],))
        row = cursor.fetchone()
        if not row:
            st.error("No se encontró el préstamo.")
            return
        id_miembro, proposito, monto, fecha_desembolso, fecha_vencimiento, firma, estado = row

        # obtener pagos existentes
        cursor.execute("SELECT id_pago, numero_pago, fecha, capital, interes, estado FROM prestamo_pagos WHERE id_prestamo = %s ORDER BY numero_pago", (prest['ID'],))
        pagos_bd = cursor.fetchall()
    finally:
        try:
            cursor.close()
        except:
            pass
        try:
            con.close()
        except:
            pass

    # mostrar formulario de edición
    col1, col2 = st.columns(2)
    with col1:
        proposito_n = st.text_input("Propósito", value=proposito)
        monto_n = st.number_input("Monto", min_value=0.0, value=float(monto), step=0.01, format="%.2f")
    with col2:
        fecha_desembolso_n = st.date_input("Fecha desembolso", value=pd.to_datetime(fecha_desembolso).date())
        fecha_vencimiento_n = st.date_input("Fecha vencimiento", value=pd.to_datetime(fecha_vencimiento).date())
        firma_n = st.text_input("Firma", value=firma or "")
        estado_n = st.selectbox("Estado del préstamo", options=["activo","finalizado"], index=0 if estado=="activo" else 1)

    st.markdown("#### Pagos (edite los campos que necesite)")
    pagos_temp = []
    for p in pagos_bd:
        id_pago, numero_pago, fecha_p, capital_p, interes_p, estado_p = p
        st.markdown(f"**Pago #{numero_pago}**")
        fcol1, fcol2, fcol3, fcol4 = st.columns([2,2,2,1])
        with fcol1:
            fecha_p_n = st.date_input(f"Fecha pago #{numero_pago}", value=pd.to_datetime(fecha_p).date(), key=f"edit_fecha_{id_pago}")
        with fcol2:
            cap_p_n = st.number_input(f"Capital #{numero_pago}", min_value=0.0, value=float(capital_p), step=0.01, format="%.2f", key=f"edit_cap_{id_pago}")
        with fcol3:
            int_p_n = st.number_input(f"Interés #{numero_pago}", min_value=0.0, value=float(interes_p), step=0.01, format="%.2f", key=f"edit_int_{id_pago}")
        with fcol4:
            est_p_n = st.selectbox(f"Estado #{numero_pago}", options=["a pagar","pagado"], index=0 if estado_p=="a pagar" else 1, key=f"edit_est_{id_pago}")

        pagos_temp.append({
            "id_pago": id_pago,
            "numero_pago": numero_pago,
            "fecha": fecha_p_n,
            "capital": cap_p_n,
            "interes": int_p_n,
            "estado": est_p_n
        })
        st.markdown("---")

    if st.button("💾 Actualizar préstamo"):
        try:
            con = obtener_conexion()
            cursor = con.cursor()
            # actualizar préstamo
            cursor.execute("""
                UPDATE prestamos
                SET proposito=%s, monto=%s, fecha_desembolso=%s, fecha_vencimiento=%s, firma=%s, estado=%s
                WHERE id_prestamo=%s
            """, (proposito_n, monto_n, fecha_desembolso_n.strftime("%Y-%m-%d"), fecha_vencimiento_n.strftime("%Y-%m-%d"), firma_n, estado_n, prest['ID']))

            # actualizar pagos
            for p in pagos_temp:
                cursor.execute("""
                    UPDATE prestamo_pagos
                    SET fecha=%s, capital=%s, interes=%s, estado=%s
                    WHERE id_pago=%s
                """, (p["fecha"].strftime("%Y-%m-%d"), float(p["capital"]), float(p["interes"]), p["estado"], p["id_pago"]))

            con.commit()
            st.success("Préstamo actualizado ✔️")
            time.sleep(0.5)
            del st.session_state["editar_prestamo"]
            st.experimental_rerun()
        finally:
            try:
                cursor.close()
            except:
                pass
            try:
                con.close()
            except:
                pass

    if st.button("⬅️ Cancelar edición"):
        del st.session_state["editar_prestamo"]
        st.experimental_rerun()

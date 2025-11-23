import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import time

def registrar_miembros():
    # ================================
    # VALIDAR SESIÓN Y GRUPO
    # ================================
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")

    # ================================
    # TITULOS CENTRADOS
    # ================================
    st.markdown(f"<h2 style='text-align:center;'>📌 Grupo: {nombre_grupo}</h2>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>🧍 Registro de Miembros</h1>", unsafe_allow_html=True)

    # ================================
    # FORMULARIO NUEVO MIEMBRO
    # ================================
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Teléfono")
        enviar = st.form_submit_button("Registrar")

    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO Miembros (Nombre, DUI, Telefono) VALUES (%s, %s, %s)",
                (nombre, dui, telefono)
            )
            con.commit()
            id_miembro = cursor.lastrowid
            cursor.execute(
                "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                (id_grupo, id_miembro)
            )
            con.commit()
            st.success("Miembro registrado correctamente ✔️")
            time.sleep(1)
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            cursor.close()
            con.close()

    # ================================
    # MOSTRAR MIEMBROS CON TABLA ALINEADA
    # MOSTRAR MIEMBROS EN TABLA BONITA
    # ================================
    try:
        con = obtener_conexion()
@@ -64,53 +64,37 @@
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY M.nombre
        """, (id_grupo,))
        resultados = cursor.fetchall()
        df = pd.DataFrame(resultados, columns=["ID", "Nombre", "DUI", "Teléfono"])

        if df.empty:
            st.info("Aún no hay miembros en este grupo.")
        else:
            # -------------------------------
            # CSS para simular bordes de tabla
            # -------------------------------
            st.markdown("""
                <style>
                .fila, .cabecera {
                    border-bottom: 1px solid #ccc;
                    padding: 4px 0;
                }
                .cabecera {
                    font-weight: bold;
                    border-bottom: 2px solid #999;
                }
                </style>
            """, unsafe_allow_html=True)

            # -------------------------------
            # Cabecera
            # -------------------------------
            col_headers = st.columns([1,3,2,2,2])
            headers = ["No.", "Nombre", "DUI", "Teléfono", "Acciones"]
            for col, header in zip(col_headers, headers):
                col.markdown(f"<div class='cabecera'>{header}</div>", unsafe_allow_html=True)

            # -------------------------------
            # Filas de datos con botones
            # -------------------------------
            for idx, row in df.iterrows():
                cols = st.columns([1,3,2,2,2])
                cols[0].markdown(f"<div class='fila'>{idx+1}</div>", unsafe_allow_html=True)
                cols[1].markdown(f"<div class='fila'>{row['Nombre']}</div>", unsafe_allow_html=True)
                cols[2].markdown(f"<div class='fila'>{row['DUI']}</div>", unsafe_allow_html=True)
                cols[3].markdown(f"<div class='fila'>{row['Teléfono']}</div>", unsafe_allow_html=True)
                with cols[4]:
                    if st.button("Editar", key=f"editar_{row['ID']}"):
                        editar_miembro(row)
                        st.experimental_rerun()
                    if st.button("Eliminar", key=f"eliminar_{row['ID']}"):
                        eliminar_miembro(row["ID"], id_grupo)
                        st.experimental_rerun()
            return

        # Mostrar tabla con Streamlit nativo
        st.dataframe(df.drop(columns="ID"), use_container_width=True)

        # ================================
        # Seleccionar miembro para editar/eliminar
        # ================================
        miembro_dict = {f"{row['Nombre']} ({row['DUI']})": row for idx, row in df.iterrows()}
        seleccionado = st.selectbox("Selecciona un miembro para Editar/Eliminar", options=list(miembro_dict.keys()))

        if seleccionado:
            miembro = miembro_dict[seleccionado]

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Editar Miembro"):
                    editar_miembro(miembro)
            with col2:
                if st.button("Eliminar Miembro"):
                    eliminar_miembro(miembro["ID"], id_grupo)
                    st.success(f"Miembro '{miembro['Nombre']}' eliminado ✔️")
                    time.sleep(1)
                    st.experimental_rerun()

    finally:
        cursor.close()
@@ -134,7 +118,6 @@
            (id_miembro,)
        )
        con.commit()
        st.success("Miembro eliminado ✔️")
    finally:
        cursor.close()
        con.close()

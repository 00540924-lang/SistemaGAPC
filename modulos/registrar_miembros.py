import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion
import time

def registrar_miembros():

    # ================================
    # VALIDAR SESIÓN Y OBTENER GRUPO
    # ================================
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return
    
    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo desconocido")

    # Mostrar encabezado SOLO después de obtener la información
    st.subheader(f"📌 Grupo: **{nombre_grupo}**")
    st.title("🧍 Registro de Miembros")

    # ================================
    # FORMULARIO
    # ================================
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Telefono")
        enviar = st.form_submit_button("Registrar")

    # ------------------ BOTÓN REGRESAR ------------------
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    # ================================
    # GUARDAR MIEMBRO
    # ================================
    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            # Insertar miembro
            sql = "INSERT INTO Miembros (Nombre, DUI, Telefono) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, dui, telefono))
            con.commit()

            id_miembro = cursor.lastrowid

            # Asignarlo al grupo del usuario logeado
            cursor.execute(
                "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                (id_grupo, id_miembro)
            )
            con.commit()

            msg = st.success("Miembro registrado correctamente ✔️")

            # Hacer desaparecer el mensaje
            time.sleep(2)
            msg.empty()

        except Exception as e:
            st.error(f"Error: {e}")

        finally:
            try:
                cursor.close()
                con.close()
            except:
                pass

    # ================================
    # LISTA DE MIEMBROS DE ESTE GRUPO
    # ================================
    st.write("")
    st.subheader(f"📝 Miembros registrados en {nombre_grupo}")

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT M.nombre, M.dui, M.telefono
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
        """, (id_grupo,))

        resultados = cursor.fetchall()

        if resultados:
            df = pd.DataFrame(resultados, columns=["Nombre", "DUI", "Teléfono"])
            df.index = df.index + 1
            df.index.name = "No."
            st.dataframe(df)
        else:
            st.info("Aún no hay miembros en este grupo.")

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"Error al mostrar miembros: {e}")

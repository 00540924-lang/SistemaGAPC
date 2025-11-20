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
    st.markdown(
        f"<h2 style='text-align:center;'>📌 Grupo: {nombre_grupo}</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h1 style='text-align:center;'>🧍 Registro de Miembros</h1>",
        unsafe_allow_html=True
    )

    # ================================
    # FORMULARIO
    # ================================
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Telefono")
        enviar = st.form_submit_button("Registrar")

    # BOTÓN REGRESAR
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    # ================================
    # PROCESAR FORMULARIO
    # ================================
    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            sql = "INSERT INTO Miembros (Nombre, DUI, Telefono) VALUES (%s, %s, %s)"
            cursor.execute(sql, (nombre, dui, telefono))
            con.commit()

            id_miembro = cursor.lastrowid

            cursor.execute(
                "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                (id_grupo, id_miembro)
            )
            con.commit()

            msg = st.success("Miembro registrado correctamente ✔️")
            time.sleep(1)
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
    # MOSTRAR MIEMBROS EN TABLA HTML ESTILIZADA
    # ================================
    st.markdown(
        f"<h2 style='text-align:center;'>📝 Miembros registrados en {nombre_grupo}</h2>",
        unsafe_allow_html=True
    )

    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT M.id_miembro, M.nombre, M.dui, M.telefono
            FROM Miembros M
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
        """, (id_grupo,))

        resultados = cursor.fetchall()

        if resultados:

            # Encabezado de la tabla con estilo
            st.markdown("""
                <style>
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        margin-top: 15px;
                    }
                    th, td {
                        border: 1px solid #ccc;
                        padding: 8px;
                        text-align: center;
                    }
                    th {
                        background-color: #f2f2f2;
                        font-weight: bold;
                    }
                    tr:nth-child(even) {
                        background-color: #fafafa;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Crear encabezado manual
            st.markdown("""
                <table>
                    <tr>
                        <th>No.</th>
                        <th>Nombre</th>
                        <th>DUI</th>
                        <th>Teléfono</th>
                        <th>Acciones</th>
                    </tr>
                </table>
            """, unsafe_allow_html=True)

            # Filas con botones
            for idx, row in enumerate(resultados, start=1):
                id_miembro = row[0]
                nombre = row[1]
                dui = row[2]
                telefono = row[3]

                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])

                col1.write(f"{idx}")
                col2.write(nombre)
                col3.write(dui)
                col4.write(telefono)

                if col5.button("🗑️ Eliminar", key=f"del_{id_miembro}"):
                    eliminar_miembro(id_miembro, id_grupo)
                    st.rerun()

        else:
            st.info("Aún no hay miembros en este grupo.")

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"Error al mostrar miembros: {e}")


# ========================================================
# FUNCIÓN PARA ELIMINAR MIEMBRO
# ========================================================
def eliminar_miembro(id_miembro, id_grupo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute(
            "DELETE FROM Grupomiembros WHERE id_grupo = %s AND id_miembro = %s",
            (id_grupo, id_miembro)
        )
        con.commit()

        cursor.execute("DELETE FROM Miembros WHERE id_miembro = %s", (id_miembro,))
        con.commit()

    except Exception as e:
        st.error(f"Error al eliminar miembro: {e}")

    finally:
        try:
            cursor.close()
            con.close()
        except:
            pass


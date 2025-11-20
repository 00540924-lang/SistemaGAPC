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
    # MOSTRAR MIEMBROS DEL GRUPO
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

            df = pd.DataFrame(resultados, columns=["ID", "Nombre", "DUI", "Teléfono"])
            df.index = df.index + 1
            df.index.name = "No."

            # Mostrar tabla con botones de eliminar
            for index, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])

                with col1:
                    st.write(index)

                with col2:
                    st.write(row["Nombre"])

                with col3:
                    st.write(row["DUI"])

                with col4:
                    st.write(row["Teléfono"])

                with col5:
                    if st.button("🗑️ Eliminar", key=f"del_{row['ID']}"):
                        eliminar_miembro(row["ID"], id_grupo)
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

        # Primero elimina relación en Grupomiembros
        cursor.execute(
            "DELETE FROM Grupomiembros WHERE id_grupo = %s AND id_miembro = %s",
            (id_grupo, id_miembro)
        )
        con.commit()

        # Luego elimina el miembro
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

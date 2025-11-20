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
    # FORMULARIO NUEVO MIEMBRO
    # ================================
    with st.form("form_miembro"):
        nombre = st.text_input("Nombre completo")
        dui = st.text_input("DUI")
        telefono = st.text_input("Telefono")
        enviar = st.form_submit_button("Registrar")

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
    # MOSTRAR MIEMBROS
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

            # ================================
            # TABLA HTML PERSONALIZADA
            # ================================
            tabla_html = """
            <style>
                table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 16px;
                }
                th, td {
                    border: 1px solid #cfcfcf;
                    padding: 8px;
                    text-align: center;
                }
                th {
                    background-color: #f5f5f5;
                    font-weight: bold;
                }
                button {
                    background-color: #f0f0f5;
                    color: #444;
                    border: 1px solid #ccc;
                    padding: 6px 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    margin: 2px;
                }
                button:hover {
                    background-color: #e2e2eb;
                }
            </style>
            <table>
                <tr>
                    <th>No.</th>
                    <th>Nombre</th>
                    <th>DUI</th>
                    <th>Teléfono</th>
                    <th>Acciones</th>
                </tr>
            """

            for idx, row in df.iterrows():
                tabla_html += f"""
                <tr>
                    <td>{idx}</td>
                    <td>{row['Nombre']}</td>
                    <td>{row['DUI']}</td>
                    <td>{row['Teléfono']}</td>
                    <td>
                        <form action="" method="post">
                            <button name="editar_{row['ID']}">Editar</button>
                            <button name="eliminar_{row['ID']}">Eliminar</button>
                        </form>
                    </td>
                </tr>
                """

            tabla_html += "</table>"

            st.html(tabla_html)

            # ================================
            # DETECCIÓN DE BOTONES
            # ================================
            for idx, row in df.iterrows():
                # Botón Eliminar
                if f"eliminar_{row['ID']}" in st.session_state:
                    eliminar_miembro(row["ID"], id_grupo)
                    st.rerun()

                # Botón Editar
                if f"editar_{row['ID']}" in st.session_state:
                    editar_miembro(row)
                    st.rerun()

        else:
            st.info("Aún no hay miembros en este grupo.")

        cursor.close()
        con.close()

    except Exception as e:
        st.error(f"Error al mostrar miembros: {e}")


# ================================================
# FUNCIÓN PARA ELIMINAR MIEMBRO
# ================================================
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


# ================================================
# FUNCIÓN PARA EDITAR MIEMBRO
# ================================================
def editar_miembro(row):
    st.markdown(f"<h3>✏️ Editando miembro: {row['Nombre']}</h3>", unsafe_allow_html=True)

    with st.form(f"form_editar_{row['ID']}"):
        nombre = st.text_input("Nombre completo", value=row['Nombre'])
        dui = st.text_input("DUI", value=row['DUI'])
        telefono = st.text_input("Teléfono", value=row['Teléfono'])
        actualizar = st.form_submit_button("Actualizar")

    if actualizar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute(
                "UPDATE Miembros SET Nombre=%s, DUI=%s, Telefono=%s WHERE id_miembro=%s",
                (nombre, dui, telefono, row['ID'])
            )
            con.commit()
            st.success("Miembro actualizado correctamente ✔️")
            time.sleep(1)
            st.experimental_rerun()

        except Exception as e:
            st.error(f"Error al actualizar miembro: {e}")

        finally:
            try:
                cursor.close()
                con.close()
            except:
                pass

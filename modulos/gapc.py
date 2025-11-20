import streamlit as st
import pandas as pd
from modulos.config.conexion import obtener_conexion

def mostrar_gapc():
    # ===============================
    # 0. Verificar usuario logueado y rol
    # ===============================
    if 'usuario' not in st.session_state or 'rol' not in st.session_state:
        st.warning("Debes iniciar sesión para acceder a este módulo.")
        return

    rol = st.session_state['rol'].lower()
    if rol != "institucional":
        st.error("❌ No tienes permisos para ver este módulo.")
        return

    st.title("📋 Lista de Grupos por Distrito")

    # ===============================
    # 1. Conexión a la BD
    # ===============================
    conn = obtener_conexion()
    if not conn:
        st.error("❌ No se pudo conectar a la base de datos.")
        return
    cursor = conn.cursor(dictionary=True)

    # ===============================
    # 2. Obtener todos los grupos
    # ===============================
    cursor.execute("""
        SELECT id_grupo, distrito, Nombre_grupo
        FROM Grupos
        ORDER BY distrito, Nombre_grupo
    """)
    grupos = cursor.fetchall()

    if not grupos:
        st.info("No hay grupos registrados.")
        cursor.close()
        conn.close()
        return

    # ===============================
    # 3. Diccionario distritos -> grupos
    # ===============================
    distritos_dict = {}
    for grupo in grupos:
        distrito = grupo['distrito']
        if distrito not in distritos_dict:
            distritos_dict[distrito] = []
        distritos_dict[distrito].append(grupo)

    # ===============================
    # 4. Selectbox de distritos
    # ===============================
    distrito_seleccionado = st.selectbox(
        "Seleccione un distrito",
        options=sorted(distritos_dict.keys())
    )

    # ===============================
    # 5. Mostrar grupos del distrito seleccionado
    # ===============================
    st.subheader(f"Grupos del distrito: {distrito_seleccionado}")
    grupos_mostrar = distritos_dict.get(distrito_seleccionado, [])

    if grupos_mostrar:
        # Crear DataFrame para mostrar en tabla editable
        df = pd.DataFrame(grupos_mostrar)
        df = df.rename(columns={"Nombre_grupo": "Grupo", "distrito": "Distrito", "id_grupo": "ID"})
        df = df[["ID", "Grupo"]]  # Solo mostramos ID y Nombre
        st.data_editor(
            df,
            use_container_width=True,
            hide_index=True,
            disabled=True  # Solo lectura
        )
    else:
        st.info("No hay grupos en este distrito.")

    # ===============================
    # 6. Botón regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    # ===============================
    # 7. Cerrar conexión
    # ===============================
    cursor.close()
    conn.close()


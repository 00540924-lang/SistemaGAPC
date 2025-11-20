import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_gapc():
    # ===============================
    # 0. Verificar usuario logueado y rol
    # ===============================
    if 'usuario' not in st.session_state or 'rol' not in st.session_state:
        st.warning("Debes iniciar sesión para acceder a este módulo.")
        return

    rol = st.session_state['rol'].lower()  # convertir a minúscula para evitar problemas

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
    # 2. Obtener grupos por distrito
    # ===============================
    cursor.execute("""
        SELECT distrito, Nombre_grupo
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
    # 3. Agrupar por distrito
    # ===============================
    distritos = {}
    for grupo in grupos:
        distrito = grupo['distrito']
        if distrito not in distritos:
            distritos[distrito] = []
        distritos[distrito].append(grupo['Nombre_grupo'])

    # ===============================
    # 4. Mostrar en Streamlit
    # ===============================
    for distrito, lista_grupos in distritos.items():
        with st.expander(f"Distrito: {distrito}", expanded=True):
            for g in lista_grupos:
                st.write(f"- {g}")

    # ===============================
    # 5. Botón regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    # ===============================
    # 6. Cerrar conexión
    # ===============================
    cursor.close()
    conn.close()


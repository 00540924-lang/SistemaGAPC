import streamlit as st
from modulos.config.conexion import obtener_conexion

def mostrar_gapc():
    # ===============================
    # 0. Verificar usuario logueado y rol
    # ===============================
    if 'usuario' not in st.session_state or 'rol' not in st.session_state:
        st.warning("Debes iniciar sesión para acceder a este módulo.")
        return

    # Mostrar valor real enviado (para depuración)
    st.write("DEBUG - Rol recibido:", repr(st.session_state['rol']))

    # Normalizar rol
    rol = st.session_state['rol']
    if rol is None:
        rol = ""
    rol = rol.strip().lower()

    # Validación del rol
    if rol != "institucional":
        st.error("❌ No tienes permisos para ver este módulo.")
        return

    st.title("📋 Lista de grupos por distrito")

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
    # 3. Crear diccionario distritos -> grupos
    # ===============================
    distritos_dict = {}
    for grupo in grupos:
        distrito = grupo['distrito']
        if distrito not in distritos_dict:
            distritos_dict[distrito] = []
        distritos_dict[distrito].append(grupo['Nombre_grupo'])

    # ===============================
    # 4. Selectbox para elegir distrito
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
        for g in grupos_mostrar:
            st.write(f"- {g}")
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

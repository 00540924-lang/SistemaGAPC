import streamlit as st
from modulos.config.conexion import obtener_conexion

def verificar_usuario(Usuario, Contraseña):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None
    else:
        st.session_state["conexion_exitosa"] = True

    try:
        cursor = con.cursor()

        # Consulta corregida: columna Contraseña con backticks y sin "Contra"
        query = """
            SELECT Usuario 
            FROM Administradores 
            WHERE Usuario = %s AND `Contraseña` = %s
        """
        cursor.execute(query, (Usuario, Contraseña))
        result = cursor.fetchone()

        return result[0] if result else None

    finally:
        con.close()


def login():
    st.title("Inicio de sesión")

    # Mostrar mensaje si conexión ya fue exitosa
    if st.session_state.get("conexion_exitosa"):
        st.success("✅ Conexión a la base de datos establecida correctamente.")

    Usuario = st.text_input("Usuario", key="login_usuario_input")
    Contraseña = st.text_input("Contraseña", type="password", key="login_contraseña_input")

    if st.button("Iniciar sesión"):
        usuario_validado = verificar_usuario(Usuario, Contraseña)

        if usuario_validado:
            st.session_state["usuario"] = usuario_validado
            st.session_state["sesion_iniciada"] = True
            st.success(f"Bienvenido {usuario_validado} 👋")
            st.rerun()
        else:
            st.error("❌ Credenciales incorrectas.")

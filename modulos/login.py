# Guarda este código como `login.py` en tu carpeta `modulos` o donde lo tengas organizado.

import streamlit as st
from modulos.config.conexion import obtener_conexion

# -------------------------------------------------
# CSS PARA CAMBIAR EL FONDO (FONDO CLARO PERSONALIZADO)
# -------------------------------------------------
st.markdown("""
<style>
/* Fondo principal */
[data-testid="stAppViewContainer"] {
    background: #F7F3FA !important;  /* Morado pastel muy claro */
}

/* Fondo del sidebar */
[data-testid="stSidebar"] {
    background: #EFE8F4 !important;
}

/* Ajustar color de los inputs */
input {
    background-color: white !important;
    color: black !important;
}

/* Texto general */
body {
    color: #2A2A2A !important;
}
</style>
""", unsafe_allow_html=True)

# --- Inicialización de st.session_state para la autenticación ---
# Esto debe hacerse una vez al inicio del script en el módulo que se ejecuta primero (ej. app.py)
# o asegurar que se inicialice antes de ser accedido.
# Si login.py es importado, esta inicialización se hará una vez.
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None # Aseguramos que el rol esté siempre inicializado

# -------------------------------------------------
# FUNCIÓN PARA VERIFICAR USUARIO Y OBTENER ROL
# -------------------------------------------------
def verificar_usuario(usuario, contraseña):
    con = obtener_conexion()
    if not con:
        st.error("⚠️ No se pudo conectar a la base de datos.")
        return None, None # Retorna None para usuario y rol si hay error

    try:
        cursor = con.cursor()
        # Modificado: Asume que si está en 'Administradores', el rol es 'admin'.
        # Si tienes una columna 'Rol' en tu tabla o múltiples tablas de roles,
        # deberías ajustar esta consulta para obtener el rol dinámicamente.
        query = "SELECT Usuario FROM Administradores WHERE Usuario = %s AND Contraseña = %s"
        cursor.execute(query, (usuario, contraseña))
        result = cursor.fetchone()
        if result:
            return result[0], "admin" # Retorna el usuario y el rol 'admin'
        else:
            return None, None # No se encontró el usuario o credenciales incorrectas

    finally:
        if con: # Asegúrate de cerrar la conexión si se abrió
            con.close()

# -------------------------------------------------
# FUNCIÓN PARA CERRAR SESIÓN
# -------------------------------------------------
def logout_user():
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None
    st.success("Has cerrado sesión.")
    st.experimental_rerun() # Recargar para volver al login

# -------------------------------------------------
# PANTALLA DE LOGIN (FORMULARIO) 
# -------------------------------------------------
def login_form():
    # -------- LOGO CENTRADO ----------
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.write("")
    with col2:
        st.image("modulos/assets/logo_gapc.png", width=800) # Asegúrate de que esta ruta sea correcta
    with col3:
        st.write("")

    # -------- TÍTULO ----------
    st.markdown(
        """
        <h2 style='text-align: center; margin-top: -30px; color:#4C3A60;'>
            Sistema de Gestión – GAPC
        </h2>
        """,
        unsafe_allow_html=True,
    )

    # -------- TARJETA VISUAL (Completando el div que dejaste) ----------
    st.markdown(
    """
    <div style='
        background-color: white;
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        max-width: 400px;
        margin: 50px auto 20px auto; /* Centrar y añadir margen */
    '>
    """, unsafe_allow_html=True)

    # -------- FORMULARIO DE LOGIN DENTRO DE LA TARJETA ----------
    with st.form("login_form"): # Usamos un st.form para manejar el estado del formulario
        st.markdown("<h3 style='text-align: center; color:#4C3A60;'>Acceder</h3>", unsafe_allow_html=True)
        usuario_input = st.text_input("Usuario")
        contraseña_input = st.text_input("Contraseña", type="password")
        submit_button = st.form_submit_button("Entrar")

        if submit_button:
            found_user, found_role = verificar_usuario(usuario_input, contraseña_input)
            if found_user:
                st.session_state['authenticated'] = True
                st.session_state['username'] = found_user
                st.session_state['role'] = found_role # Guardamos el rol
                st.success(f"¡Bienvenido, {found_user}!")
                st.experimental_rerun() # Recargar la app para mostrar el contenido
            else:
                st.error("❌ Usuario o contraseña incorrectos.")

    st.markdown("</div>", unsafe_allow_html=True) # Cerrar la tarjeta visual


# -------------------------------------------------
# FUNCIÓN PRINCIPAL DE AUTENTICACIÓN PARA LLAMAR DESDE app.py
# -------------------------------------------------
def handle_authentication():
    if not st.session_state['authenticated']:
        login_form() # Muestra el formulario de login
        return False # No autenticado
    else:
        # Si está autenticado, muestra el mensaje de bienvenida y el botón de cerrar sesión en la sidebar
        st.sidebar.write(f"Bienvenido, {st.session_state['username']} ({st.session_state['role']})")
        if st.sidebar.button("Cerrar Sesión"): # Botón de logout en la sidebar
            logout_user()
        return True # Autenticado

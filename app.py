import streamlit as st
from modulos.login import handle_authentication # Importa la función de autenticación que definimos
from modulos.menu import mostrar_menu # Asumiendo que esta función ya existe y puede ser role-aware

# Configuración de la página (opcional)
st.set_page_config(layout="wide")

# --- Inicialización de st.session_state para la autenticación ---
# Estas variables deben estar siempre disponibles al inicio de la app.
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    st.session_state['role'] = None # Aseguramos que el rol esté siempre inicializado

# ---- LEER PARÁMETROS DE URL para navegación de módulos ----
query_params = st.experimental_get_query_params()
if "modulo" in query_params:
    st.session_state["modulo"] = query_params["modulo"][0]
else:
    # Asegurar un 'modulo' por defecto si no hay uno establecido, para usuarios autenticados
    if 'modulo' not in st.session_state: # Solo establecer si no está presente, para no sobrescribir parámetros de URL
        st.session_state["modulo"] = "inicio" # Una página de aterrizaje por defecto para usuarios autenticados

# ---- Manejar la Autenticación ----
# Esta función de login.py mostrará el formulario de inicio de sesión si no está autenticado,
# o el botón de cerrar sesión y la información del usuario en la barra lateral si está autenticado.
# También establecerá st.session_state['authenticated'], ['username'] y ['role'].
is_authenticated = handle_authentication()

if not is_authenticated:
    # Si handle_authentication() devuelve False, significa que se muestra el formulario de inicio de sesión.
    # Detenemos la ejecución adicional de app.py hasta que el usuario inicie sesión con éxito.
    st.stop() # ⛔ Detiene la ejecución

# ---- Si está autenticado, continuar ----

# Recuperar los detalles del usuario del estado de la sesión
# (Esto lo habría establecido handle_authentication en login.py)
username = st.session_state.get('username', 'Usuario')
user_role = st.session_state.get('role', 'guest') # Rol por defecto si no se encuentra por alguna razón

st.title(f"Sistema Principal GAPC")
st.markdown(f"**Bienvenido, {username}! Tu rol: {user_role.upper()}**")
st.markdown("---")

# ---- MOSTRAR MENÚ ----
# Tu función `modulos/menu.py`'s `mostrar_menu` puede necesitar ser actualizada
# para tomar `user_role` como argumento o acceder a `st.session_state['role']` directamente
# para mostrar elementos de menú específicos de cada rol.
mostrar_menu() # Asumiendo que es general o que lee st.session_state['role'] internamente

# ---- CARGAR EL MÓDULO SEGÚN state Y ROL ----
modulo_seleccionado = st.session_state.get("modulo")

if modulo_seleccionado == "registrar_miembros":
    if user_role == "admin":
        from modulos.registrar_miembros import registrar_miembros
        registrar_miembros()
    else:
        st.error("🚫 Acceso Denegado: No tienes permisos de administrador para 'Registrar Miembros'.")
        st.session_state["modulo"] = "inicio" # Redirigir a una página segura
elif modulo_seleccionado == "dashboard_user": # Ejemplo de un módulo solo para usuario estándar
    if user_role == "user" or user_role == "admin": # Los administradores también pueden acceder a los módulos de usuario
        # from modulos.dashboard_user import show_user_dashboard # Descomentar e importar tu módulo real
        # show_user_dashboard()
        st.write("Contenido del Dashboard de Usuario.")
    else:
        st.error("🚫 Acceso Denegado: Este módulo es solo para usuarios estándar o administradores.")
        st.session_state["modulo"] = "inicio"
elif modulo_seleccionado == "informacion_general": # Ejemplo de un módulo accesible por todos los roles autenticados
    st.write("Bienvenido al módulo de Información General. Aquí encontrarás contenido relevante para todos los usuarios autenticados.")
    # from modulos.informacion_general import show_info # Descomentar e importar tu módulo real
    # show_info()
elif modulo_seleccionado == "inicio":
    st.info("Bienvenido a la página de inicio. Por favor, selecciona una opción del menú lateral.")
    # Opcionalmente, puedes añadir contenido general del dashboard aquí basado en el rol
    if user_role == "admin":
        st.write("Resumen de actividades recientes para administradores.")
    elif user_role == "user":
        st.write("Tus tareas pendientes.")
    else:
        st.write("Información general del sistema.")
elif modulo_seleccionado:
    # Caso de respaldo para cualquier otro nombre de módulo
    st.warning(f"El módulo '{modulo_seleccionado}' no está definido o no tienes acceso.")
    st.info("Por favor, selecciona una opción válida del menú.")
    st.session_state["modulo"] = "inicio"

st.markdown("---")
st.write("Pie de página o contenido común para todos los usuarios autenticados.")

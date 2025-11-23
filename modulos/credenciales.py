import mysql.connector
import streamlit as st

# ==========================
# CONEXIÓN A BASE DE DATOS
# ==========================
def get_connection():
    return mysql.connector.connect(
        host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
        user="uiazxdhtd3r8o7uv",
        password="uGjZ9MXWemv7vPsjOdA5",
        database="bzn5gsi7ken7lufcglbg"
    )

# ==========================
# FUNCIÓN PARA VERIFICAR USUARIO EXISTENTE
# ==========================
def usuario_existe(usuario):
    """Verifica si el usuario ya existe en la base de datos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM Administradores WHERE Usuario = %s",
            (usuario,)
        )
        resultado = cursor.fetchone()
        return resultado[0] > 0
    except Exception as e:
        st.error(f"Error al verificar usuario: {e}")
        return True
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ==========================
# FUNCIÓN PARA ELIMINAR USUARIO
# ==========================
def eliminar_usuario(usuario):
    """Elimina un usuario de la base de datos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM Administradores WHERE Usuario = %s",
            (usuario,)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error al eliminar usuario: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# ==========================
# FUNCIÓN PARA OBTENER USUARIOS
# ==========================
def obtener_usuarios(filtro_rol=None):
    """Obtiene todos los usuarios, opcionalmente filtrados por rol (excluye al desarrollador)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if filtro_rol and filtro_rol != "Todos":
            cursor.execute(
                "SELECT Usuario, Rol FROM Administradores WHERE Rol = %s AND Usuario != 'Dark' ORDER BY Usuario",
                (filtro_rol,)
            )
        else:
            cursor.execute("SELECT Usuario, Rol FROM Administradores WHERE Usuario != 'Dark' ORDER BY Usuario")
            
        usuarios = cursor.fetchall()
        return usuarios
    except Exception as e:
        st.error(f"Error al cargar usuarios: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ==========================
# FUNCIÓN PARA OBTENER ESTADÍSTICAS (incluye todos los usuarios)
# ==========================
def obtener_estadisticas():
    """Obtiene estadísticas incluyendo todos los usuarios"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total de usuarios (excluyendo Dark)
        cursor.execute("SELECT COUNT(*) FROM Administradores WHERE Usuario != 'Dark'")
        total_usuarios = cursor.fetchone()[0]
        
        # Usuarios institucionales (excluyendo Dark)
        cursor.execute("SELECT COUNT(*) FROM Administradores WHERE Rol = 'Institucional' AND Usuario != 'Dark'")
        usuarios_institucionales = cursor.fetchone()[0]
        
        # Usuarios promotores (excluyendo Dark)
        cursor.execute("SELECT COUNT(*) FROM Administradores WHERE Rol = 'Promotor' AND Usuario != 'Dark'")
        usuarios_promotores = cursor.fetchone()[0]
        
        return total_usuarios, usuarios_institucionales, usuarios_promotores
    except Exception as e:
        st.error(f"Error al cargar estadísticas: {e}")
        return 0, 0, 0
    finally:
        cursor.close()
        conn.close()

# ==========================
# MÓDULO DE CREDENCIALES
# ==========================
def pagina_credenciales():
    st.title("Registro de nuevas credenciales")

    # BOTÓN PARA VOLVER AL MENÚ
    if st.button("⬅️ Regresar al menú"):
        st.session_state["page"] = "menu"
        st.rerun()

    st.write("---")
    st.subheader("➕ Registrar nueva credencial")

    # FORMULARIO DE REGISTRO
    usuario = st.text_input("Usuario").strip()
    contraseña = st.text_input("Contraseña", type="password")
    rol = st.selectbox("Rol", options=["Institucional", "Promotor"])

    # BOTÓN PARA GUARDAR
    if st.button("Guardar credencial"):
        if not usuario:
            st.error("El usuario es obligatorio.")
        elif not contraseña.strip():
            st.error("La contraseña es obligatoria.")
        elif len(contraseña) < 4:
            st.error("La contraseña debe tener al menos 4 caracteres.")
        elif usuario.lower() == "dark":
            st.error("❌ Este nombre de usuario no está permitido.")
        elif usuario_existe(usuario):
            st.error("❌ El usuario ya existe. Por favor, elige otro nombre de usuario.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO Administradores (Usuario, Contraseña, Rol) VALUES (%s, %s, %s)",
                    (usuario, contraseña, rol)
                )
                conn.commit()
                
                st.success("✅ Credencial registrada correctamente.")
                st.session_state["credencial_form_cleared"] = True
                
            except mysql.connector.IntegrityError as e:
                if "Duplicate entry" in str(e):
                    st.error("❌ Error: El usuario ya existe en la base de datos.")
                else:
                    st.error(f"❌ Error de integridad: {e}")
            except Exception as e:
                st.error(f"❌ Error inesperado: {e}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

    # Limpiar campos después de guardar exitosamente
    if st.session_state.get("credencial_form_cleared", False):
        st.session_state["credencial_form_cleared"] = False
        st.info("💡 Los campos se han limpiado. Puedes registrar otra credencial si lo deseas.")

    st.write("---")
    
    # SECCIÓN DE LISTA DE USUARIOS
    st.subheader("👥 Lista de usuarios con acceso")
    
    # FILTRO POR ROL
    col1, col2 = st.columns([1, 3])
    with col1:
        filtro_rol = st.selectbox(
            "Filtrar por rol:",
            options=["Todos", "Institucional", "Promotor"],
            key="filtro_rol"
        )
    
    # OBTENER USUARIOS (excluye Dark)
    usuarios = obtener_usuarios(filtro_rol)
    
    if usuarios:
        st.write(f"**Mostrando {len(usuarios)} usuario(s):**")
        
        # MOSTRAR USUARIOS EN TARJETAS
        for i, (usuario, rol) in enumerate(usuarios):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.write(f"**Usuario:** {usuario}")
                
                with col2:
                    st.write(f"**Rol:** {rol}")
                
                with col3:
                    # BOTÓN PARA ELIMINAR CON CONFIRMACIÓN
                    if st.button("🗑️ Eliminar", key=f"eliminar_{usuario}"):
                        st.session_state[f"confirmar_eliminar_{usuario}"] = True
                
                # CONFIRMACIÓN DE ELIMINACIÓN
                if st.session_state.get(f"confirmar_eliminar_{usuario}", False):
                    st.warning(f"¿Estás seguro de que quieres eliminar al usuario **{usuario}**?")
                    col_conf1, col_conf2 = st.columns(2)
                    
                    with col_conf1:
                        if st.button("✅ Sí, eliminar", key=f"si_eliminar_{usuario}"):
                            if eliminar_usuario(usuario):
                                st.success(f"✅ Usuario **{usuario}** eliminado correctamente.")
                                # Limpiar estado de confirmación
                                st.session_state[f"confirmar_eliminar_{usuario}"] = False
                                # Recargar la página para actualizar la lista
                                st.rerun()
                            else:
                                st.error("❌ Error al eliminar el usuario.")
                    
                    with col_conf2:
                        if st.button("❌ Cancelar", key=f"no_eliminar_{usuario}"):
                            st.session_state[f"confirmar_eliminar_{usuario}"] = False
                            st.rerun()
            
    else:
        st.info("No hay usuarios registrados con los filtros seleccionados.")
    
    # ESTADÍSTICAS CENTRADAS (excluye Dark)
    st.write("---")
    st.subheader("📊 Estadísticas")
    
    # Obtener estadísticas (excluyendo Dark)
    total_usuarios, usuarios_institucionales, usuarios_promotores = obtener_estadisticas()
    
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    
    with col_stats1:
        st.metric(
            label="Total Usuarios", 
            value=total_usuarios
        )
    
    with col_stats2:
        st.metric(
            label="Usuarios Institucionales", 
            value=usuarios_institucionales
        )
    
    with col_stats3:
        st.metric(
            label="Usuarios Promotores", 
            value=usuarios_promotores
        )
    
    # Centrar adicionalmente con CSS
    st.markdown("""
        <style>
        /* Centrar los números de las métricas */
        .stMetric {
            text-align: center;
        }
        .stMetric label {
            display: block;
            text-align: center;
            font-weight: bold;
        }
        .stMetric value {
            display: block;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

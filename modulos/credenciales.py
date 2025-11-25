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
# FUNCIÓN PARA OBTENER MIEMBROS CON CREDENCIALES (PARA PROMOTORES)
# ==========================
def obtener_miembros_con_credenciales(filtro_grupo=None):
    """Obtiene miembros que tienen credenciales de acceso (rol Miembro)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if filtro_grupo and filtro_grupo != "Todos":
            cursor.execute("""
                SELECT A.Usuario, M.Nombre, G.nombre_grupo, M.id_miembro
                FROM Administradores A
                JOIN Miembros M ON M.id_administrador = A.id_administrador
                JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
                JOIN Grupos G ON G.id_grupo = GM.id_grupo
                WHERE A.Rol = 'Miembro' AND G.id_grupo = %s
                ORDER BY M.Nombre
            """, (filtro_grupo,))
        else:
            cursor.execute("""
                SELECT A.Usuario, M.Nombre, G.nombre_grupo, M.id_miembro
                FROM Administradores A
                JOIN Miembros M ON M.id_administrador = A.id_administrador
                JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
                JOIN Grupos G ON G.id_grupo = GM.id_grupo
                WHERE A.Rol = 'Miembro'
                ORDER BY G.nombre_grupo, M.Nombre
            """)
            
        miembros = cursor.fetchall()
        return miembros
    except Exception as e:
        st.error(f"Error al cargar miembros con credenciales: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ==========================
# FUNCIÓN PARA OBTENER GRUPOS
# ==========================
def obtener_grupos():
    """Obtiene todos los grupos disponibles"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id_grupo, nombre_grupo FROM Grupos ORDER BY nombre_grupo")
        grupos = cursor.fetchall()
        return grupos
    except Exception as e:
        st.error(f"Error al cargar grupos: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ==========================
# FUNCIÓN PARA ELIMINAR CREDENCIAL DE MIEMBRO
# ==========================
def eliminar_credencial_miembro(usuario):
    """Elimina las credenciales de acceso de un miembro (solo el usuario, no el miembro completo)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 1. Obtener el id_administrador del miembro
        cursor.execute(
            "SELECT id_administrador FROM Administradores WHERE Usuario = %s AND Rol = 'Miembro'",
            (usuario,)
        )
        resultado = cursor.fetchone()
        
        if not resultado:
            st.error("No se encontró el usuario miembro.")
            return False
        
        id_administrador = resultado[0]

        # 2. Eliminar la referencia en la tabla Miembros
        cursor.execute(
            "UPDATE Miembros SET id_administrador = NULL WHERE id_administrador = %s",
            (id_administrador,)
        )

        # 3. Eliminar el usuario de Administradores
        cursor.execute(
            "DELETE FROM Administradores WHERE id_administrador = %s",
            (id_administrador,)
        )

        conn.commit()
        return True

    except Exception as e:
        st.error(f"Error al eliminar credencial del miembro: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

# ==========================
# FUNCIÓN PARA OBTENER ESTADÍSTICAS MIEMBROS CON CREDENCIALES
# ==========================
def obtener_estadisticas_miembros_con_credenciales():
    """Obtiene estadísticas de miembros con credenciales"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Total de miembros con credenciales
        cursor.execute("""
            SELECT COUNT(*) 
            FROM Administradores A
            JOIN Miembros M ON M.id_administrador = A.id_administrador
            WHERE A.Rol = 'Miembro'
        """)
        total_miembros_con_credenciales = cursor.fetchone()[0]
        
        # Total de grupos que tienen miembros con credenciales
        cursor.execute("""
            SELECT COUNT(DISTINCT G.id_grupo)
            FROM Administradores A
            JOIN Miembros M ON M.id_administrador = A.id_administrador
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            JOIN Grupos G ON G.id_grupo = GM.id_grupo
            WHERE A.Rol = 'Miembro'
        """)
        grupos_con_miembros_credenciales = cursor.fetchone()[0]
        
        # Total de grupos
        cursor.execute("SELECT COUNT(*) FROM Grupos")
        total_grupos = cursor.fetchone()[0]
        
        return total_miembros_con_credenciales, grupos_con_miembros_credenciales, total_grupos
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
    # VERIFICAR QUE EL USUARIO TENGA ROL INSTITUCIONAL O PROMOTOR
    rol_usuario_actual = st.session_state.get("rol", "").lower()
    
    if rol_usuario_actual not in ["institucional", "promotor"]:
        st.error("❌ Acceso denegado. Solo los usuarios con rol 'Institucional' o 'Promotor' pueden acceder a este módulo.")
        
        # Botón para regresar al menú
        if st.button("⬅️ Regresar al menú"):
            st.session_state["page"] = "menu"
            st.rerun()
        return

    # TÍTULO SEGÚN ROL
    if rol_usuario_actual == "institucional":
        st.markdown(
            "<h1 style='text-align: center; color:#4C3A60;'>Registro de nuevas credenciales</h1>",
            unsafe_allow_html=True
        )
    else:  # Promotor
        st.markdown(
            "<h1 style='text-align: center; color:#4C3A60;'>Gestión de Credenciales de Miembros</h1>",
            unsafe_allow_html=True
        )

    # BOTÓN PARA VOLVER AL MENÚ
    if st.button("⬅️ Regresar al menú"):
        st.session_state["page"] = "menu"
        st.rerun()
    
    st.write("---")

    # ==========================
    # SECCIÓN PARA ROL INSTITUCIONAL
    # ==========================
    if rol_usuario_actual == "institucional":
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
        
        # SECCIÓN DE LISTA DE USUARIOS ADMINISTRATIVOS
        st.subheader("👥 Lista de usuarios con acceso")
        
        # FILTRO POR ROL (solo Institucional y Promotor)
        col1, col2 = st.columns([1, 3])
        with col1:
            filtro_rol = st.selectbox(
                "Filtrar por rol:",
                options=["Todos", "Institucional", "Promotor"],
                key="filtro_rol_admin"
            )
        
        # OBTENER USUARIOS ADMINISTRATIVOS (excluye Miembro y Dark)
        def obtener_usuarios_administradores(filtro_rol=None):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                if filtro_rol and filtro_rol != "Todos":
                    cursor.execute(
                        "SELECT Usuario, Rol FROM Administradores WHERE Rol = %s AND Usuario != 'Dark' AND Rol != 'Miembro' ORDER BY Usuario",
                        (filtro_rol,)
                    )
                else:
                    cursor.execute(
                        "SELECT Usuario, Rol FROM Administradores WHERE Usuario != 'Dark' AND Rol != 'Miembro' ORDER BY Usuario"
                    )
                    
                usuarios = cursor.fetchall()
                return usuarios
            except Exception as e:
                st.error(f"Error al cargar usuarios: {e}")
                return []
            finally:
                cursor.close()
                conn.close()

        usuarios = obtener_usuarios_administradores(filtro_rol)
        
        if usuarios:
            st.write(f"**Mostrando {len(usuarios)} usuario(s):**")
            
            # MOSTRAR USUARIOS EN TARJETAS COMPACTAS
            for i, (usuario, rol) in enumerate(usuarios):
                with st.container():
                    # UNA SOLA LÍNEA CON TRES COLUMNAS
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**👤 {usuario}**")
                    
                    with col2:
                        st.write(f"**🎯 {rol}**")
                    
                    with col3:
                        # BOTÓN MÁS COMPACTO
                        if st.button("🗑️", key=f"eliminar_admin_{usuario}", help=f"Eliminar a {usuario}"):
                            st.session_state[f"confirmar_eliminar_admin_{usuario}"] = True
                    
                    # CONFIRMACIÓN DE ELIMINACIÓN (debajo de la línea)
                    if st.session_state.get(f"confirmar_eliminar_admin_{usuario}", False):
                        st.warning(f"¿Estás seguro de que quieres eliminar al usuario **{usuario}**?")
                        col_conf1, col_conf2 = st.columns(2)
                        
                        with col_conf1:
                            if st.button("✅ Sí, eliminar", key=f"si_eliminar_admin_{usuario}"):
                                if eliminar_usuario(usuario):
                                    st.success(f"✅ Usuario **{usuario}** eliminado correctamente.")
                                    # Limpiar estado de confirmación
                                    st.session_state[f"confirmar_eliminar_admin_{usuario}"] = False
                                    # Recargar la página para actualizar la lista
                                    st.rerun()
                                else:
                                    st.error("❌ Error al eliminar el usuario.")
                        
                        with col_conf2:
                            if st.button("❌ Cancelar", key=f"no_eliminar_admin_{usuario}"):
                                st.session_state[f"confirmar_eliminar_admin_{usuario}"] = False
                                st.rerun()
                
                # LÍNEA SEPARADORA ENTRE USUARIOS (opcional)
                if i < len(usuarios) - 1:
                    st.markdown("---")

        else:
            st.info("No hay usuarios registrados con los filtros seleccionados.")

    # ==========================
    # SECCIÓN PARA ROL PROMOTOR
    # ==========================
    else:  # rol_usuario_actual == "promotor"
        st.subheader("👥 Lista de miembros con credenciales de acceso")
        
        # OBTENER GRUPOS PARA FILTRO
        grupos = obtener_grupos()
        opciones_grupos = ["Todos"] + [grupo[1] for grupo in grupos]
        mapa_grupos = {grupo[1]: grupo[0] for grupo in grupos}
        
        # FILTRO POR GRUPO
        col1, col2 = st.columns([1, 3])
        with col1:
            filtro_grupo_nombre = st.selectbox(
                "Filtrar por grupo:",
                options=opciones_grupos,
                key="filtro_grupo"
            )
        
        # CONVERTIR NOMBRE DE GRUPO A ID
        filtro_grupo_id = None
        if filtro_grupo_nombre != "Todos":
            filtro_grupo_id = mapa_grupos.get(filtro_grupo_nombre)
        
        # OBTENER MIEMBROS CON CREDENCIALES
        miembros = obtener_miembros_con_credenciales(filtro_grupo_id)
        
        if miembros:
            st.write(f"**Mostrando {len(miembros)} miembro(s) con credenciales:**")
            
            # MOSTRAR MIEMBROS EN TARJETAS COMPACTAS
            for i, (usuario, nombre, grupo, id_miembro) in enumerate(miembros):
                with st.container():
                    # UNA SOLA LÍNEA CON TRES COLUMNAS
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**👤 {nombre}**")
                        st.write(f"*Usuario: {usuario}*")
                    
                    with col2:
                        st.write(f"**🏘️ {grupo}**")
                    
                    with col3:
                        # BOTÓN MÁS COMPACTO
                        if st.button("🗑️", key=f"eliminar_credencial_{usuario}", help=f"Eliminar credencial de {nombre}"):
                            st.session_state[f"confirmar_eliminar_credencial_{usuario}"] = True
                    
                    # CONFIRMACIÓN DE ELIMINACIÓN (debajo de la línea)
                    if st.session_state.get(f"confirmar_eliminar_credencial_{usuario}", False):
                        st.warning(f"¿Estás seguro de que quieres eliminar las credenciales de **{nombre}**?")
                        st.info("ℹ️ Esta acción solo eliminará el acceso al sistema, el miembro seguirá existiendo en el grupo.")
                        col_conf1, col_conf2 = st.columns(2)
                        
                        with col_conf1:
                            if st.button("✅ Sí, eliminar", key=f"si_eliminar_credencial_{usuario}"):
                                if eliminar_credencial_miembro(usuario):
                                    st.success(f"✅ Credenciales de **{nombre}** eliminadas correctamente.")
                                    # Limpiar estado de confirmación
                                    st.session_state[f"confirmar_eliminar_credencial_{usuario}"] = False
                                    # Recargar la página para actualizar la lista
                                    st.rerun()
                                else:
                                    st.error("❌ Error al eliminar las credenciales.")
                        
                        with col_conf2:
                            if st.button("❌ Cancelar", key=f"no_eliminar_credencial_{usuario}"):
                                st.session_state[f"confirmar_eliminar_credencial_{usuario}"] = False
                                st.rerun()
                
                # LÍNEA SEPARADORA ENTRE MIEMBROS (opcional)
                if i < len(miembros) - 1:
                    st.markdown("---")

        else:
            st.info("No hay miembros con credenciales de acceso con los filtros seleccionados.")

    # ==========================
    # ESTADÍSTICAS
    # ==========================
    st.write("---")
    st.subheader("📊 Estadísticas")
    
    if rol_usuario_actual == "institucional":
        # Obtener estadísticas para Institucional
        def obtener_estadisticas_administradores():
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Total de usuarios (excluyendo Dark y Miembro)
                cursor.execute("SELECT COUNT(*) FROM Administradores WHERE Usuario != 'Dark' AND Rol != 'Miembro'")
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

        total_usuarios, usuarios_institucionales, usuarios_promotores = obtener_estadisticas_administradores()
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        
        with col_stats1:
            st.metric(label="Total Usuarios", value=total_usuarios)
        
        with col_stats2:
            st.metric(label="Usuarios Institucionales", value=usuarios_institucionales)
        
        with col_stats3:
            st.metric(label="Usuarios Promotores", value=usuarios_promotores)
    
    else:  # Promotor
        # Obtener estadísticas para Promotor
        total_miembros_con_credenciales, grupos_con_miembros_credenciales, total_grupos = obtener_estadisticas_miembros_con_credenciales()
        
        col_stats1, col_stats2, col_stats3 = st.columns(3)
        
        with col_stats1:
            st.metric(label="Miembros con Credenciales", value=total_miembros_con_credenciales)
        
        with col_stats2:
            st.metric(label="Grupos con Acceso", value=grupos_con_miembros_credenciales)
        
        with col_stats3:
            st.metric(label="Total Grupos", value=total_grupos)
    
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

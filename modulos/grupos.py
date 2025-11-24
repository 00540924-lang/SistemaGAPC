import streamlit as st
import time
from modulos.config.conexion import obtener_conexion
import re

def pagina_grupos():
    st.title("Gestión de Grupos")
    
    # ================================
    # INICIALIZAR SESSION STATE PARA VALIDACIÓN
    # ================================
    if 'telefono_valido' not in st.session_state:
        st.session_state.telefono_valido = True
    if 'telefono_value' not in st.session_state:
        st.session_state.telefono_value = ""

    # ------------------ BOTÓN REGRESAR ------------------
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        # Limpiar estados al regresar
        st.session_state.telefono_value = ""
        st.session_state.telefono_valido = True
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")

    # ================= FORMULARIO NUEVO GRUPO =================
    st.subheader("➕ Registrar nuevo grupo")
    nombre = st.text_input("Nombre del Grupo", key="nombre_grupo")
    distrito = st.text_input("Distrito", key="distrito")
    inicio_ciclo = st.date_input("Inicio del Ciclo", key="inicio_ciclo")

    if st.button("Guardar grupo"):
        mensaje = st.empty()
        if not nombre.strip():
            mensaje.error("El nombre del grupo es obligatorio.")
            time.sleep(3)
            mensaje.empty()
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO Grupos (nombre_grupo, distrito, inicio_ciclo) VALUES (%s, %s, %s)",
                    (nombre, distrito, inicio_ciclo)
                )
                conn.commit()
                mensaje.success("Grupo creado correctamente.")
                time.sleep(3)
                mensaje.empty()
            except Exception as e:
                mensaje.error(f"Error al crear grupo: {e}")
                time.sleep(3)
                mensaje.empty()
            finally:
                cursor.close()
                conn.close()

    st.write("---")

    # ================= LISTAR GRUPOS =================
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_grupo, nombre_grupo FROM Grupos")
        grupos = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    if not grupos:
        st.info("No hay grupos registrados aún.")
        return

    # ================= FORMULARIO NUEVO MIEMBRO =================
    st.subheader("➕ Registrar nuevo miembro")

    # Campos normales fuera de form
    nombre_m = st.text_input("Nombre completo")
    dui = st.text_input("DUI")
    
    # CAMPO DE TELÉFONO CON VALIDACIÓN
    telefono = st.text_input(
        "Teléfono",
        value=st.session_state.telefono_value,
        key="telefono_input",
        help="Ingrese solo números"
    )

    grupo_asignado = st.selectbox(
        "Asignar al grupo",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x)
    )

    # Checkbox que aparece en tiempo real
    es_admin = st.checkbox("Este miembro forma parte de la directiva")

    # Campos del admin dinámicos
    if es_admin:
        usuario_admin = st.text_input("Usuario")
        contraseña_admin = st.text_input("Contraseña", type="password")
        rol_admin = st.selectbox(
            "Rol del administrador",
            options=["Miembro"],
            index=0
        )
    else:
        usuario_admin = None
        contraseña_admin = None
        rol_admin = None

    # VARIABLE PARA CONTROLAR MENSAJES DE ERROR
    mostrar_error_telefono = False
    mensaje_telefono = ""

    # VALIDACIÓN DEL TELÉFONO (se ejecuta siempre)
    if telefono:  # Solo validar si hay contenido
        if not re.match(r'^[0-9]*$', telefono):
            st.session_state.telefono_valido = False
            mostrar_error_telefono = True
            mensaje_telefono = "❌ Solo se permiten números en el campo de teléfono"
        else:
            st.session_state.telefono_valido = True
            st.session_state.telefono_value = re.sub(r'[^0-9]', '', telefono)

    # Botón para registrar miembro (único submit)
    if st.button("Registrar miembro"):
        mensaje = st.empty()
        
        # Reiniciar flags de error
        error_nombre = False
        error_telefono = False
        error_admin = False
        
        mensajes_error = []
        
        # VALIDACIONES ANTES DE GUARDAR
        if not nombre_m.strip():
            error_nombre = True
            mensajes_error.append("El nombre del miembro es obligatorio.")
        
        if not st.session_state.telefono_valido:
            error_telefono = True
            mensajes_error.append("Solo se permiten números en el campo de teléfono")
        
        if es_admin and (not usuario_admin or not contraseña_admin):
            error_admin = True
            mensajes_error.append("Debe ingresar usuario y contraseña para administrador.")
        
        # Si hay errores, mostrarlos todos juntos
        if mensajes_error:
            mensaje_error_final = "❌ " + " | ".join(mensajes_error)
            mensaje.error(mensaje_error_final)
            time.sleep(3)
            mensaje.empty()
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor(dictionary=True)

                # Usar el valor limpio del teléfono
                telefono_limpio = re.sub(r'[^0-9]', '', telefono) if telefono else ""

                # Insertar miembro
                cursor.execute(
                    "INSERT INTO Miembros (nombre, dui, telefono) VALUES (%s, %s, %s)",
                    (nombre_m, dui, telefono_limpio)
                )
                conn.commit()
                miembro_id = cursor.lastrowid

                # Crear relación con grupo
                cursor.execute(
                    "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                    (grupo_asignado, miembro_id)
                )
                conn.commit()

                # Si es administrador
                if es_admin:
                    cursor.execute(
                        "INSERT INTO Administradores (Usuario, Contraseña, Rol) VALUES (%s, %s, %s)",
                        (usuario_admin, contraseña_admin, rol_admin)
                    )
                    conn.commit()
                    id_adm = cursor.lastrowid

                    cursor.execute(
                        "UPDATE Miembros SET id_administrador=%s WHERE id_miembro=%s",
                        (id_adm, miembro_id)
                    )
                    conn.commit()

                mensaje.success(f"{nombre_m} registrado correctamente en el grupo.")
                
                # LIMPIAR ESTADOS DESPUÉS DE REGISTRAR EXITOSAMENTE
                st.session_state.telefono_value = ""
                st.session_state.telefono_valido = True
                
                time.sleep(3)
                mensaje.empty()

            except Exception as e:
                conn.rollback()
                mensaje.error(f"Error al registrar miembro: {e}")
                time.sleep(3)
                mensaje.empty()
            finally:
                cursor.close()
                conn.close()

    # MOSTRAR MENSAJE DE ERROR DEL TELÉFONO (si aplica)
    if mostrar_error_telefono:
        st.error(mensaje_telefono)

    st.write("---")

    # ================= ELIMINAR GRUPO =================
    st.subheader("🗑️ Eliminar un grupo completo")
    st.warning("⚠️ ADVERTENCIA: Esta acción es irreversible. Se eliminarán:")
    st.warning("• El grupo seleccionado")
    st.warning("• Las relaciones del grupo con miembros")
    st.warning("• Solo se eliminarán miembros que NO tengan registros en otras tablas (multas, préstamos, etc.)")

    grupo_eliminar = st.selectbox(
        "Selecciona el grupo a eliminar",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x),
        key="grupo_eliminar"
    )

    # Mostrar información del grupo seleccionado
    if grupo_eliminar:
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            
            # Contar miembros en el grupo
            cursor.execute("SELECT COUNT(*) FROM Grupomiembros WHERE id_grupo = %s", (grupo_eliminar,))
            total_miembros = cursor.fetchone()[0]
            
            # Contar miembros que solo están en este grupo
            cursor.execute("""
                SELECT COUNT(*) 
                FROM Grupomiembros GM 
                WHERE GM.id_grupo = %s 
                AND GM.id_miembro NOT IN (
                    SELECT id_miembro 
                    FROM Grupomiembros 
                    WHERE id_grupo != %s
                )
            """, (grupo_eliminar, grupo_eliminar))
            miembros_exclusivos = cursor.fetchone()[0]
            
            st.info(f"📊 Grupo seleccionado: {next(g['nombre_grupo'] for g in grupos if g['id_grupo'] == grupo_eliminar)}")
            st.info(f"👥 Total de miembros en el grupo: {total_miembros}")
            st.info(f"🎯 Miembros que solo están en este grupo: {miembros_exclusivos}")
            
        except Exception as e:
            st.error(f"Error al obtener información del grupo: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    if st.button("Eliminar grupo seleccionado", type="primary"):
        mensaje = st.empty()
        conn = None
        cursor = None
        
        # Confirmación adicional
        if not st.session_state.get('confirmar_eliminacion', False):
            st.session_state.confirmar_eliminacion = True
            st.warning("¿Estás seguro de que quieres eliminar este grupo? Esta acción no se puede deshacer.")
            if st.button("✅ Sí, eliminar definitivamente"):
                eliminar_grupo_definitivo(grupo_eliminar, mensaje)
        else:
            eliminar_grupo_definitivo(grupo_eliminar, mensaje)

def eliminar_grupo_definitivo(grupo_id, mensaje):
    """Función para eliminar el grupo de forma segura"""
    conn = None
    cursor = None
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        # PRIMERO: Identificar miembros que SOLO pertenecen a este grupo y NO tienen registros en otras tablas
        cursor.execute("""
            SELECT GM.id_miembro 
            FROM Grupomiembros GM 
            WHERE GM.id_grupo = %s 
            AND GM.id_miembro NOT IN (
                SELECT id_miembro 
                FROM Grupomiembros 
                WHERE id_grupo != %s
            )
            AND GM.id_miembro NOT IN (
                SELECT DISTINCT id_miembro FROM Multas WHERE id_miembro IS NOT NULL
                UNION
                SELECT DISTINCT id_miembro FROM prestamos WHERE id_miembro IS NOT NULL
                UNION
                SELECT DISTINCT id_miembro FROM ahorro_final WHERE id_miembro IS NOT NULL
                UNION
                SELECT DISTINCT id_miembro FROM prestamo_pagos WHERE id_miembro IS NOT NULL
            )
        """, (grupo_id, grupo_id))
        
        miembros_seguros_eliminar = [row[0] for row in cursor.fetchall()]
        
        # SEGUNDO: Eliminar relaciones en Grupomiembros
        cursor.execute("DELETE FROM Grupomiembros WHERE id_grupo = %s", (grupo_id,))
        
        # TERCERO: Eliminar solo miembros que son seguros de eliminar
        miembros_eliminados = 0
        if miembros_seguros_eliminar:
            placeholders = ','.join(['%s'] * len(miembros_seguros_eliminar))
            cursor.execute(f"DELETE FROM Miembros WHERE id_miembro IN ({placeholders})", miembros_seguros_eliminar)
            miembros_eliminados = len(miembros_seguros_eliminar)
        
        # CUARTO: Finalmente eliminar el grupo
        cursor.execute("DELETE FROM Grupos WHERE id_grupo = %s", (grupo_id,))
        
        conn.commit()
        
        # Mensaje de resultado
        if miembros_eliminados > 0:
            mensaje.success(f"✅ Grupo eliminado correctamente. Se eliminaron {miembros_eliminados} miembros que solo pertenecían a este grupo.")
        else:
            mensaje.success("✅ Grupo eliminado correctamente. Los miembros se mantuvieron porque tienen registros en otras tablas o pertenecen a otros grupos.")
        
        # Limpiar confirmación
        st.session_state.confirmar_eliminacion = False
        time.sleep(3)
        st.rerun()
        
    except Exception as e:
        if conn:
            conn.rollback()
        mensaje.error(f"❌ Error al eliminar grupo: {str(e)}")
        st.error("💡 No se pudo eliminar el grupo porque los miembros tienen registros relacionados en otras tablas (multas, préstamos, etc.).")
        st.session_state.confirmar_eliminacion = False
        time.sleep(5)
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

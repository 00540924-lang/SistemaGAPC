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
    
    # ADVERTENCIA EN UN SOLO BLOQUE
    st.error("""
    ⚠️ **ELIMINACIÓN COMPLETA - ADVERTENCIA CRÍTICA**

    **Esta acción eliminará PERMANENTEMENTE:**
    - El grupo completo  
    - Todos los miembros del grupo  
    - Todas las multas de los miembros  
    - Todos los préstamos de los miembros  
    - Todos los ahorros de los miembros  
    - Todos los pagos de préstamos  
    - Todos los registros relacionados  

    **🚨 ESTA ACCIÓN NO SE PUEDE DESHACER**
    """)

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
            
            # Obtener información del grupo
            grupo_nombre = next(g['nombre_grupo'] for g in grupos if g['id_grupo'] == grupo_eliminar)
            
            # Contar miembros en el grupo
            cursor.execute("SELECT COUNT(*) FROM Grupomiembros WHERE id_grupo = %s", (grupo_eliminar,))
            total_miembros = cursor.fetchone()[0]
            
            # Contar registros relacionados
            cursor.execute("SELECT COUNT(*) FROM Multas WHERE id_miembro IN (SELECT id_miembro FROM Grupomiembros WHERE id_grupo = %s)", (grupo_eliminar,))
            total_multas = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM prestamos WHERE id_miembro IN (SELECT id_miembro FROM Grupomiembros WHERE id_grupo = %s)", (grupo_eliminar,))
            total_prestamos = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ahorro_final WHERE id_miembro IN (SELECT id_miembro FROM Grupomiembros WHERE id_grupo = %s)", (grupo_eliminar,))
            total_ahorros = cursor.fetchone()[0]
            
            st.info(f"📊 Grupo seleccionado: {grupo_nombre}")
            st.info(f"👥 Miembros a eliminar: {total_miembros}")
            st.info(f"💰 Multas a eliminar: {total_multas}")
            st.info(f"💸 Préstamos a eliminar: {total_prestamos}")
            st.info(f"🏦 Ahorros a eliminar: {total_ahorros}")
            
        except Exception as e:
            st.error(f"Error al obtener información del grupo: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    # Usar un key único para el botón de eliminación
    if st.button("🚨 ELIMINAR COMPLETAMENTE", key="btn_eliminar_grupo"):
        eliminar_grupo_completo(grupo_eliminar)

def eliminar_grupo_completo(grupo_id):
    """Función para eliminar COMPLETAMENTE el grupo y todo lo relacionado"""
    conn = None
    cursor = None
    
    # Crear un contenedor para mensajes
    mensaje_container = st.empty()
    
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        mensaje_container.info("🔄 Iniciando eliminación completa...")
        
        # 1. PRIMERO: Obtener todos los miembros del grupo
        cursor.execute("SELECT id_miembro FROM Grupomiembros WHERE id_grupo = %s", (grupo_id,))
        miembros_ids = [row[0] for row in cursor.fetchall()]
        
        if not miembros_ids:
            mensaje_container.warning("No hay miembros en este grupo. Eliminando solo el grupo...")
            cursor.execute("DELETE FROM Grupos WHERE id_grupo = %s", (grupo_id,))
            conn.commit()
            mensaje_container.success("✅ Grupo eliminado correctamente")
            time.sleep(2)
            st.rerun()
            return
        
        placeholders = ','.join(['%s'] * len(miembros_ids))
        
        # 2. DESACTIVAR RESTRICCIONES DE CLAVE FORÁNEA TEMPORALMENTE
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        mensaje_container.info("🗑️ Eliminando registros relacionados...")
        
        # 3. ELIMINAR EN ORDEN CORRECTO (de más específico a más general)
        
        # Primero: Eliminar pagos de préstamos
        try:
            cursor.execute(f"""
                DELETE FROM prestamo_pagos 
                WHERE id_prestamo IN (
                    SELECT id_prestamo FROM prestamos 
                    WHERE id_miembro IN ({placeholders})
                )
            """, miembros_ids)
            mensaje_container.info("✅ Pagos de préstamos eliminados")
        except Exception as e:
            mensaje_container.warning(f"⚠️ No se pudieron eliminar pagos de préstamos: {e}")
        
        # Segundo: Eliminar préstamos
        try:
            cursor.execute(f"DELETE FROM prestamos WHERE id_miembro IN ({placeholders})", miembros_ids)
            mensaje_container.info("✅ Préstamos eliminados")
        except Exception as e:
            mensaje_container.warning(f"⚠️ No se pudieron eliminar préstamos: {e}")
        
        # Tercero: Eliminar multas
        try:
            cursor.execute(f"DELETE FROM Multas WHERE id_miembro IN ({placeholders})", miembros_ids)
            mensaje_container.info("✅ Multas eliminadas")
        except Exception as e:
            mensaje_container.warning(f"⚠️ No se pudieron eliminar multas: {e}")
        
        # Cuarto: Eliminar ahorros
        try:
            cursor.execute(f"DELETE FROM ahorro_final WHERE id_miembro IN ({placeholders})", miembros_ids)
            mensaje_container.info("✅ Ahorros eliminados")
        except Exception as e:
            mensaje_container.warning(f"⚠️ No se pudieron eliminar ahorros: {e}")
        
        # Quinto: Eliminar registros de caja del grupo
        try:
            cursor.execute("DELETE FROM Caja WHERE id_grupo = %s", (grupo_id,))
            mensaje_container.info("✅ Registros de caja eliminados")
        except Exception as e:
            mensaje_container.warning(f"⚠️ No se pudieron eliminar registros de caja: {e}")
        
        # Sexto: Eliminar relaciones grupo-miembro
        try:
            cursor.execute("DELETE FROM Grupomiembros WHERE id_grupo = %s", (grupo_id,))
            mensaje_container.info("✅ Relaciones grupo-miembro eliminadas")
        except Exception as e:
            mensaje_container.warning(f"⚠️ No se pudieron eliminar relaciones: {e}")
        
        # Séptimo: Eliminar miembros
        try:
            # Primero eliminar referencias a administradores si existen
            cursor.execute(f"""
                UPDATE Miembros 
                SET id_administrador = NULL 
                WHERE id_miembro IN ({placeholders})
            """, miembros_ids)
            
            # Luego eliminar los miembros
            cursor.execute(f"DELETE FROM Miembros WHERE id_miembro IN ({placeholders})", miembros_ids)
            mensaje_container.info("✅ Miembros eliminados")
        except Exception as e:
            mensaje_container.warning(f"⚠️ No se pudieron eliminar miembros: {e}")
        
        # Octavo: Eliminar el grupo
        try:
            cursor.execute("DELETE FROM Grupos WHERE id_grupo = %s", (grupo_id,))
            mensaje_container.info("✅ Grupo eliminado")
        except Exception as e:
            mensaje_container.warning(f"⚠️ No se pudo eliminar el grupo: {e}")
        
        # 4. REACTIVAR RESTRICCIONES DE CLAVE FORÁNEA
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        conn.commit()
        
        mensaje_container.success("🎉 ELIMINACIÓN COMPLETA EXITOSA")
        mensaje_container.success("Todos los registros han sido eliminados permanentemente")
        
        time.sleep(3)
        st.rerun()
        
    except Exception as e:
        if conn:
            conn.rollback()
            # Asegurarse de reactivar las restricciones incluso en caso de error
            try:
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            except:
                pass
        
        mensaje_container.error(f"❌ Error durante la eliminación: {str(e)}")
        st.error("💡 Si el error persiste, puede que haya tablas adicionales relacionadas.")
        
        # Mostrar información de depuración
        st.info("🔍 Información para depuración:")
        st.write(f"- Grupo ID: {grupo_id}")
        st.write(f"- Miembros encontrados: {len(miembros_ids) if 'miembros_ids' in locals() else 0}")
        
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

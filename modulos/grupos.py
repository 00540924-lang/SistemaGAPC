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

    # VALIDACIÓN DEL TELÉFONO (se ejecuta siempre)
    if telefono:  # Solo validar si hay contenido
        if not re.match(r'^[0-9]*$', telefono):
            st.session_state.telefono_valido = False
            st.error("❌ Solo se permiten números en el campo de teléfono")
        else:
            st.session_state.telefono_valido = True
            st.session_state.telefono_value = re.sub(r'[^0-9]', '', telefono)

    # Botón para registrar miembro (único submit)
    if st.button("Registrar miembro"):
        mensaje = st.empty()
        
        # VALIDACIONES ANTES DE GUARDAR
        if not nombre_m.strip():
            mensaje.error("El nombre del miembro es obligatorio.")
            time.sleep(3)
            mensaje.empty()
        elif not st.session_state.telefono_valido:
            mensaje.error("❌ Por favor corrija el campo de teléfono (solo números permitidos)")
            time.sleep(3)
            mensaje.empty()
        elif es_admin and (not usuario_admin or not contraseña_admin):
            mensaje.warning("Debe ingresar usuario y contraseña para administrador.")
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

    st.write("---")

    # ================= ELIMINAR GRUPO =================
    st.subheader("🗑️ Eliminar un grupo completo")
    st.warning("⚠️ Al eliminar un grupo, también se eliminarán los miembros que solo pertenecen a este grupo. Hazlo con cuidado.")

    grupo_eliminar = st.selectbox(
        "Selecciona el grupo a eliminar",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x),
        key="grupo_eliminar"
    )

    if st.button("Eliminar grupo seleccionado"):
        mensaje = st.empty()
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Grupomiembros WHERE id_grupo=%s", (grupo_eliminar,))
            cursor.execute("""
                DELETE FROM Miembros
                WHERE id_miembro NOT IN (SELECT id_miembro FROM Grupomiembros)
            """)
            cursor.execute("DELETE FROM Grupos WHERE id_grupo=%s", (grupo_eliminar,))
            conn.commit()
            mensaje.success("Grupo y miembros asociados eliminados correctamente.")
            time.sleep(3)
            mensaje.empty()
        finally:
            cursor.close()
            conn.close()

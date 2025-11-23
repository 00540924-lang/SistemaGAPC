import streamlit as st
import time
import re
from modulos.config.conexion import obtener_conexion

# -------------------- Funciones de validación --------------------
def validar_telefono(telefono):
    """Solo permite números y un '+' opcional al inicio."""
    return re.fullmatch(r'\+?\d+', telefono) is not None

# -------------------- Función principal --------------------
def pagina_grupos():
    st.title("Gestión de Grupos")

    # ------------------ BOTÓN REGRESAR ------------------
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
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
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()

    st.write("---")

    # ================= LISTAR GRUPOS =================
    try:
        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_grupo, nombre_grupo FROM Grupos")
        grupos = cursor.fetchall()
    except Exception as e:
        st.error(f"Error al cargar grupos: {e}")
        grupos = []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    if not grupos:
        st.info("No hay grupos registrados aún.")
        return

    # ================= FORMULARIO NUEVO MIEMBRO =================
    st.subheader("➕ Registrar nuevo miembro")

    nombre_m = st.text_input("Nombre completo")
    dui = st.text_input("DUI")

    # ------------------ SOLUCIÓN DEFINITIVA PARA TELÉFONO ------------------
    st.markdown("""
    <style>
    .telefono-input {
        font-size: 16px;
        padding: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Inicializar estado
    if "telefono_seguro" not in st.session_state:
        st.session_state.telefono_seguro = ""

    # Componente personalizado con JavaScript
    st.markdown("**Teléfono ***")
    
    # Input con JavaScript que bloquea caracteres no numéricos
    telefono_html = f"""
    <input type="text" 
           id="telefonoInput" 
           class="telefono-input"
           value="{st.session_state.telefono_seguro}" 
           placeholder="Solo números y + al inicio"
           onkeydown="return validarTecla(event)"
           oninput="filtrarTelefono(this)"
           style="width: 100%; padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px;">
    
    <script>
    function validarTecla(event) {{
        const tecla = event.key;
        const valorActual = event.target.value;
        
        // Permitir teclas de control (backspace, delete, tab, etc.)
        if (event.ctrlKey || event.altKey || tecla === 'Backspace' || tecla === 'Delete' || 
            tecla === 'Tab' || tecla === 'Escape' || tecla === 'Enter') {{
            return true;
        }}
        
        // Permitir '+' solo al inicio
        if (tecla === '+' && valorActual === '') {{
            return true;
        }}
        
        // Permitir solo números
        if (!/^[0-9]$/.test(tecla)) {{
            event.preventDefault();
            return false;
        }}
        
        return true;
    }}
    
    function filtrarTelefono(input) {{
        let valor = input.value;
        
        // Si empieza con +, permitir solo números después
        if (valor.startsWith('+')) {{
            input.value = '+' + valor.substring(1).replace(/[^0-9]/g, '');
        }} else {{
            // Si no empieza con +, permitir solo números
            input.value = valor.replace(/[^0-9]/g, '');
        }}
        
        // Actualizar el estado de Streamlit
        window.parent.postMessage({{
            type: 'streamlit:setComponentValue',
            value: input.value
        }}, '*');
    }}
    
    // Actualizar el input al cargar la página
    document.addEventListener('DOMContentLoaded', function() {{
        const input = document.getElementById('telefonoInput');
        if (input) {{
            filtrarTelefono(input);
        }}
    }});
    </script>
    """
    
    st.components.v1.html(telefono_html, height=80)

    # Input oculto para capturar el valor del JavaScript
    telefono_value = st.text_input(
        "Teléfono (valor real)",
        value=st.session_state.telefono_seguro,
        key="telefono_hidden",
        label_visibility="collapsed"
    )

    # Actualizar el estado cuando cambia el valor
    if telefono_value != st.session_state.telefono_seguro:
        st.session_state.telefono_seguro = telefono_value

    # Mostrar el valor actual
    if st.session_state.telefono_seguro:
        st.caption(f"📞 Teléfono ingresado: {st.session_state.telefono_seguro}")

    grupo_asignado = st.selectbox(
        "Asignar al grupo",
        options=[g["id_grupo"] for g in grupos],
        format_func=lambda x: next(g["nombre_grupo"] for g in grupos if g["id_grupo"] == x)
    )

    es_admin = st.checkbox("Este miembro forma parte de la directiva")

    if es_admin:
        usuario_admin = st.text_input("Usuario")
        contraseña_admin = st.text_input("Contraseña", type="password")
        rol_admin = st.selectbox("Rol", options=["Miembro"], index=0)
    else:
        usuario_admin = None
        contraseña_admin = None
        rol_admin = None

    # ------------------- Botón registrar miembro -------------------
    if st.button("Registrar miembro"):
        mensaje = st.empty()

        # Usar SIEMPRE la versión segura del teléfono
        telefono_final = st.session_state.telefono_seguro
        
        # Validaciones estrictas antes del INSERT
        if not nombre_m.strip():
            mensaje.error("❌ El nombre del miembro es obligatorio.")
            time.sleep(3)
            mensaje.empty()
        elif not telefono_final.strip():
            mensaje.error("❌ El teléfono es obligatorio.")
            time.sleep(3)
            mensaje.empty()
        elif not validar_telefono(telefono_final):
            mensaje.error("❌ Teléfono inválido. Solo se permiten números y un '+' opcional al inicio.")
            time.sleep(3)
            mensaje.empty()
        else:
            try:
                conn = obtener_conexion()
                cursor = conn.cursor(dictionary=True)

                # INSERT usando la versión segura del teléfono
                cursor.execute(
                    "INSERT INTO Miembros (Nombre, DUI, Telefono) VALUES (%s, %s, %s)",
                    (nombre_m, dui, telefono_final)
                )
                conn.commit()
                miembro_id = cursor.lastrowid

                # Relación con grupo
                cursor.execute(
                    "INSERT INTO Grupomiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                    (grupo_asignado, miembro_id)
                )
                conn.commit()

                # Si es administrador
                if es_admin:
                    if not usuario_admin or not contraseña_admin:
                        mensaje.warning("Debe ingresar usuario y contraseña para administrador.")
                    else:
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

                mensaje.success(f"✅ {nombre_m} registrado correctamente en el grupo.")
                time.sleep(3)
                mensaje.empty()
                
                # Limpiar campos después de guardar exitosamente
                st.session_state.telefono_seguro = ""
                st.rerun()

            except Exception as e:
                if 'conn' in locals():
                    conn.rollback()
                mensaje.error(f"❌ Error al registrar miembro: {e}")
                time.sleep(3)
                mensaje.empty()
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
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
        except Exception as e:
            if 'conn' in locals():
                conn.rollback()
            mensaje.error(f"Error al eliminar grupo: {e}")
            time.sleep(3)
            mensaje.empty()
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

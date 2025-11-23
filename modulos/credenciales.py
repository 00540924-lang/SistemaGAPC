def pagina_credenciales():
    st.title("Registro de nuevas credenciales")

    # BOTÓN PARA VOLVER AL MENÚ
    if st.button("⬅️ Regresar al menú"):
        st.session_state["page"] = "menu"
        st.rerun()

    st.write("---")
    st.subheader("➕ Registrar nueva credencial")

    # Usar session_state para mantener los valores del formulario
    if 'usuario' not in st.session_state:
        st.session_state.usuario = ""
    if 'contraseña' not in st.session_state:
        st.session_state.contraseña = ""
    if 'rol' not in st.session_state:
        st.session_state.rol = "Institucional"

    # FORMULARIO con valores del session_state
    usuario = st.text_input("Usuario", value=st.session_state.usuario).strip()
    contraseña = st.text_input("Contraseña", type="password", value=st.session_state.contraseña)
    rol = st.selectbox("Rol", options=["Institucional", "Promotor"], index=0 if st.session_state.rol == "Institucional" else 1)

    # BOTÓN PARA GUARDAR
    if st.button("Guardar credencial"):
        # VALIDACIONES
        if not usuario:
            st.error("El usuario es obligatorio.")
        elif not contraseña.strip():
            st.error("La contraseña es obligatoria.")
        elif len(contraseña) < 4:
            st.error("La contraseña debe tener al menos 4 caracteres.")
        elif usuario_existe(usuario):
            st.error("❌ El usuario ya existe. Por favor, elige otro nombre de usuario.")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # INSERTAR NUEVO USUARIO
                cursor.execute(
                    "INSERT INTO Administradores (Usuario, Contraseña, Rol) VALUES (%s, %s, %s)",
                    (usuario, contraseña, rol)
                )
                conn.commit()
                
                st.success("✅ Credencial registrada correctamente.")
                
                # Limpiar los campos del formulario sin recargar la página
                st.session_state.usuario = ""
                st.session_state.contraseña = ""
                st.session_state.rol = "Institucional"
                
                # Mostrar mensaje de éxito que permanecerá visible
                st.balloons()  # Efecto visual opcional
                
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

    # Actualizar session_state con los valores actuales
    st.session_state.usuario = usuario
    st.session_state.contraseña = contraseña
    st.session_state.rol = rol

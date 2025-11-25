def mostrar_ahorro_final(id_grupo):
    """Función principal del módulo Ahorro Final - Versión reorganizada"""
    
    # Obtener nombre del grupo desde la sesión
    nombre_grupo = st.session_state.get("nombre_grupo", "Grupo Desconocido")
    
    # Título principal con nombre del grupo
    st.markdown(f"""
    <div style='text-align: center;'>
        <h1>💰 Módulo de ahorro</h1>
        <h3 style='color: #4C3A60; margin-top: -10px;'>Grupo: {nombre_grupo}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Verificar conexión primero
    conn = get_db_connection()
    if conn is None:
        st.error("No se pudo conectar a la base de datos. Verifica la configuración.")
        return
    else:
        conn.close()
    
    # Obtener datos
    miembros = obtener_miembros_grupo(id_grupo)
    
    if not miembros:
        st.warning("No se encontraron miembros en este grupo.")
        st.info("💡 **Solución:** Asegúrate de que los miembros estén asignados al grupo en el módulo 'Gestión de Miembros'")
        if st.button("👥 Ir a Gestión de Miembros"):
            st.session_state.page = "registrar_miembros"
            st.rerun()
        return
    
    registros = obtener_registros_ahorro_final(id_grupo)
    
    # SECCIÓN 1: REGISTRO DE AHORROS POR PERSONA
    st.subheader("💰 Registrar Ahorro por Persona")
    with st.form("form_ahorro", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Crear diccionario para mapear id a nombre
            opciones_miembros = {m['id_miembro']: m['Nombre'] for m in miembros}
            miembro_ahorro = st.selectbox(
                "Seleccionar Miembro:",
                options=list(opciones_miembros.keys()),
                format_func=lambda x: opciones_miembros[x],
                key="ahorro_miembro"
            )
        
        with col2:
            fecha_ahorro = st.date_input("Fecha:", value=datetime.now(), key="fecha_ahorro")
        
        with col3:
            monto_ahorro = st.number_input("Monto de Ahorro ($):", min_value=0.0, step=0.01, value=0.0, key="monto_ahorro")
        
        submitted_ahorro = st.form_submit_button("💾 Guardar Ahorro")
        if submitted_ahorro and monto_ahorro > 0:
            success, message = guardar_registro_ahorro(
                miembro_ahorro, id_grupo, fecha_ahorro, 
                monto_ahorro, 0.0, 0.0  # Solo ahorro, actividades=0, retiros=0
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        elif submitted_ahorro:
            st.warning("Por favor ingresa un monto de ahorro mayor a 0")
    
    st.write("---")
    
    # SECCIÓN 2: REGISTRO DE RETIROS POR PERSONA
    st.subheader("💸 Registrar Retiro por Persona")
    with st.form("form_retiro", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            opciones_miembros = {m['id_miembro']: m['Nombre'] for m in miembros}
            miembro_retiro = st.selectbox(
                "Seleccionar Miembro:",
                options=list(opciones_miembros.keys()),
                format_func=lambda x: opciones_miembros[x],
                key="retiro_miembro"
            )
        
        with col2:
            fecha_retiro = st.date_input("Fecha:", value=datetime.now(), key="fecha_retiro")
        
        with col3:
            monto_retiro = st.number_input("Monto de Retiro ($):", min_value=0.0, step=0.01, value=0.0, key="monto_retiro")
        
        submitted_retiro = st.form_submit_button("💾 Guardar Retiro")
        if submitted_retiro and monto_retiro > 0:
            success, message = guardar_registro_ahorro(
                miembro_retiro, id_grupo, fecha_retiro, 
                0.0, 0.0, monto_retiro  # Solo retiro, ahorros=0, actividades=0
            )
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        elif submitted_retiro:
            st.warning("Por favor ingresa un monto de retiro mayor a 0")
    
    st.write("---")
    
    # SECCIÓN 3: REGISTRO DE ACTIVIDADES (GRUPO COMPLETO)
    st.subheader("🎯 Registrar Actividad del Grupo")
    with st.form("form_actividad", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            fecha_actividad = st.date_input("Fecha:", value=datetime.now(), key="fecha_actividad")
        
        with col2:
            monto_actividad = st.number_input("Monto de Actividad ($):", min_value=0.0, step=0.01, value=0.0, key="monto_actividad")
        
        st.info("💡 **Nota:** Las actividades se aplican a TODOS los miembros del grupo por igual")
        
        submitted_actividad = st.form_submit_button("💾 Guardar Actividad para Todos")
        if submitted_actividad and monto_actividad > 0:
            # Guardar la actividad para cada miembro del grupo
            success_count = 0
            error_messages = []
            
            for miembro in miembros:
                success, message = guardar_registro_ahorro(
                    miembro['id_miembro'], id_grupo, fecha_actividad, 
                    0.0, monto_actividad, 0.0  # Solo actividad, ahorros=0, retiros=0
                )
                if success:
                    success_count += 1
                else:
                    error_messages.append(f"{miembro['Nombre']}: {message}")
            
            if success_count == len(miembros):
                st.success(f"✅ Actividad registrada exitosamente para todos los {success_count} miembros")
            elif success_count > 0:
                st.warning(f"⚠️ Actividad registrada para {success_count} de {len(miembros)} miembros")
                for error in error_messages:
                    st.error(error)
            else:
                st.error("❌ No se pudo registrar la actividad para ningún miembro")
                for error in error_messages:
                    st.error(error)
            
            if success_count > 0:
                st.rerun()
                
        elif submitted_actividad:
            st.warning("Por favor ingresa un monto de actividad mayor a 0")
    
    # BOTÓN REGRESAR
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")
    
    # Mostrar registros existentes en TABLA (se mantiene igual)
    st.subheader("📊 Registros Existentes")
    
    if registros:
        # Preparar datos para la tabla
        datos_tabla = []
        for registro in registros:
            datos_tabla.append({
                "Fecha": registro['fecha_registro'],
                "Miembro": registro['Nombre'],
                "Ahorros": f"${registro['ahorros']:,.2f}",
                "Actividades": f"${registro['actividades']:,.2f}",
                "Retiros": f"${registro['retiros']:,.2f}",
                "Saldo Final": f"${registro['saldo_final']:,.2f}",
                "ID": registro['id_ahorro']  # Oculto pero necesario para borrar
            })
        
        # Mostrar tabla
        st.dataframe(
            datos_tabla,
            use_container_width=True,
            column_config={
                "Fecha": st.column_config.DateColumn("Fecha", format="YYYY-MM-DD"),
                "Miembro": "Miembro",
                "Ahorros": "Ahorros",
                "Actividades": "Actividades", 
                "Retiros": "Retiros",
                "Saldo Final": st.column_config.TextColumn("Saldo Final"),
                "ID": None  # Ocultar columna ID
            },
            hide_index=True
        )
        
        # SECCIÓN PARA BORRAR REGISTROS (se mantiene igual)
        st.subheader("🗑️ Gestión de Registros")
        
        # Selector para elegir qué registro borrar
        opciones_borrar = {r['id_ahorro']: f"{r['Nombre']} - {r['fecha_registro']} - ${r['saldo_final']:,.2f}" for r in registros}
        
        if opciones_borrar:
            registro_a_borrar = st.selectbox(
                "Seleccionar registro para borrar:",
                options=list(opciones_borrar.keys()),
                format_func=lambda x: opciones_borrar[x]
            )
            
            col1, col2 = st.columns([1, 4])
            with col1:
                # Botón para borrar con confirmación
                if st.button("Borrar Registro", type="secondary"):
                    if st.session_state.get("confirmar_borrado", False):
                        success, message = borrar_registro_ahorro(registro_a_borrar)
                        if success:
                            st.success(message)
                            st.session_state.confirmar_borrado = False
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.session_state.confirmar_borrado = True
                        st.warning("⚠️ ¿Estás seguro de borrar este registro? Haz clic nuevamente en 'Borrar Registro' para confirmar.")
            
            with col2:
                if st.session_state.get("confirmar_borrado", False):
                    st.error("**Confirmación pendiente:** Haz clic nuevamente en 'Borrar Registro' para confirmar la eliminación.")
        
        # ESTADÍSTICAS (se mantiene igual)
        st.subheader("📈 Estadísticas")
        
        # Selector para estadísticas (grupo o individual)
        opcion_estadisticas = st.selectbox(
            "Ver estadísticas de:",
            ["Todo el Grupo", "Miembro Específico"]
        )
        
        if opcion_estadisticas == "Todo el Grupo":
            # Estadísticas del grupo completo
            col1, col2, col3 = st.columns(3)
            
            total_ahorros = sum(r['ahorros'] for r in registros)
            total_retiros = sum(r['retiros'] for r in registros)
            saldo_total = sum(r['saldo_final'] for r in registros)
            
            with col1:
                st.metric("Total Ahorros", f"${total_ahorros:,.2f}")
            with col2:
                st.metric("Total Retiros", f"${total_retiros:,.2f}")
            with col3:
                st.metric("Saldo Total Grupo", f"${saldo_total:,.2f}")
                
        else:
            # Estadísticas por miembro
            opciones_miembros_estadisticas = {m['id_miembro']: m['Nombre'] for m in miembros}
            miembro_estadisticas = st.selectbox(
                "Seleccionar miembro para estadísticas:",
                options=list(opciones_miembros_estadisticas.keys()),
                format_func=lambda x: opciones_miembros_estadisticas[x],
                key="estadisticas_miembro"
            )
            
            if miembro_estadisticas:
                estadisticas_personales = obtener_estadisticas_personales(miembro_estadisticas, id_grupo)
                
                if estadisticas_personales:
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Total Ahorros", f"${estadisticas_personales['total_ahorros']:,.2f}")
                    with col2:
                        st.metric("Total Actividades", f"${estadisticas_personales['total_actividades']:,.2f}")
                    with col3:
                        st.metric("Total Retiros", f"${estadisticas_personales['total_retiros']:,.2f}")
                    with col4:
                        st.metric("Saldo Final Personal", f"${estadisticas_personales['total_saldo_final']:,.2f}")
                    
                    # Información adicional
                    st.info(f"**Total Registros:** {estadisticas_personales['total_registros']}")
                else:
                    st.info(f"No hay registros para {opciones_miembros_estadisticas[miembro_estadisticas]}")
            
    else:
        st.info("No hay registros de ahorro final para mostrar.")

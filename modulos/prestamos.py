# =====================================================
#   MÓDULO PRINCIPAL DE PRÉSTAMOS - CON LÍMITES
# =====================================================
def prestamos_modulo():

    # --------------------------------------
    # Validar sesión y grupo
    # --------------------------------------
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]

    # TÍTULO
    st.markdown("<h1 style='text-align:center;'>💲 Gestión de Préstamos</h1>", unsafe_allow_html=True)

    # --------------------------------------
    # Obtener nombre del grupo
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("SELECT Nombre_grupo FROM Grupos WHERE id_grupo = %s", (id_grupo,))
    grupo = cursor.fetchone()
    con.close()

    nombre_grupo = grupo[0] if grupo else "Grupo desconocido"

    # Mostrar nombre debajo del título
    st.markdown(
        f"<h3 style='text-align:center; color:#555;'>Grupo: {nombre_grupo}</h3>",
        unsafe_allow_html=True
    )

    # --------------------------------------
    # Obtener valores del reglamento - ACTUALIZADO CON NOMBRES CORRECTOS
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT interes_por_10, max_prestamo, max_plazo
        FROM Reglamento
        WHERE id_grupo = %s
        LIMIT 1
    """, (id_grupo,))
    reglamento = cursor.fetchone()
    con.close()

    interes_por_10 = float(reglamento[0]) if reglamento and reglamento[0] is not None else 0.0
    monto_maximo = float(reglamento[1]) if reglamento and reglamento[1] is not None else 0.0
    plazo_maximo = int(reglamento[2]) if reglamento and reglamento[2] is not None else 0

    # --------------------------------------
    # Obtener miembros del grupo
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT M.id_miembro, M.nombre, M.dui
        FROM Miembros M
        JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
    """, (id_grupo,))
    miembros = cursor.fetchall()
    con.close()

    if not miembros:
        st.warning("⚠ No hay miembros registrados en este grupo.")
        return

    miembros_dict = {m[1]: m[0] for m in miembros}

    # =====================================================
    #   FORMULARIO: REGISTRAR NUEVO PRÉSTAMO - CON LÍMITES
    # =====================================================
    with st.form("form_nuevo_prestamo"):
        st.subheader("📄 Nuevo Préstamo")

        miembro_seleccionado = st.selectbox("Selecciona un miembro", list(miembros_dict.keys()))
        proposito = st.text_input("Propósito del préstamo")
        
        # MONTO CON LÍMITE MÁXIMO
        monto = st.number_input(
            "Monto del préstamo", 
            min_value=0.01, 
            max_value=float(monto_maximo) if monto_maximo > 0 else None,
            step=0.01,
            help=f"Monto máximo permitido: ${monto_maximo:,.2f}" if monto_maximo > 0 else "Sin límite establecido"
        )
        
        fecha_desembolso = st.date_input("Fecha de desembolso", datetime.date.today())
        
        # FECHA DE VENCIMIENTO CON LÍMITE DE PLAZO MÁXIMO
        if plazo_maximo > 0:
            fecha_maxima = fecha_desembolso + datetime.timedelta(days=plazo_maximo)
            fecha_vencimiento = st.date_input(
                "Fecha de vencimiento", 
                min_value=fecha_desembolso,
                max_value=fecha_maxima,
                value=fecha_maxima
            )
            st.info(f"📅 Plazo máximo: {plazo_maximo} días (Vence: {fecha_maxima.strftime('%d/%m/%Y')})")
        else:
            fecha_vencimiento = st.date_input(
                "Fecha de vencimiento", 
                min_value=fecha_desembolso
            )

        # ⚠️ CAMPOS DE REGLAMENTO - SOLO LECTURA
        st.markdown("**Configuración del Reglamento:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.number_input(
                "Interés por cada $10 (%)",
                value=interes_por_10,
                step=0.01,
                disabled=True,
                key="interes_reglamento"
            )
        with col2:
            st.number_input(
                "Monto máximo permitido",
                value=monto_maximo,
                disabled=True,
                key="monto_maximo_reglamento"
            )
        with col3:
            st.number_input(
                "Plazo máximo (días)",
                value=plazo_maximo,
                disabled=True,
                key="plazo_maximo_reglamento"
            )

        # Calcular interés automáticamente
        interes_total = (monto / 10) * interes_por_10
        monto_total = monto + interes_total

        # Mostrar resumen del préstamo
        st.markdown("**Resumen del Préstamo:**")
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.info(f"💰 **Capital:** ${monto:,.2f}")
            st.info(f"📈 **Interés:** ${interes_total:,.2f}")
        with col_res2:
            st.success(f"💵 **Total a pagar:** ${monto_total:,.2f}")

        enviar = st.form_submit_button("💾 Guardar Préstamo")

    # BOTÓN REGRESAR - FUERA DEL FORMULARIO
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")

    if enviar:
        # VALIDACIONES ADICIONALES
        if monto_maximo > 0 and monto > monto_maximo:
            st.error(f"❌ El monto no puede exceder el límite máximo de ${monto_maximo:,.2f}")
            return
            
        if plazo_maximo > 0:
            dias_prestamo = (fecha_vencimiento - fecha_desembolso).days
            if dias_prestamo > plazo_maximo:
                st.error(f"❌ El plazo no puede exceder {plazo_maximo} días")
                return
        
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            # INSERT del préstamo - automáticamente como "activo"
            cursor.execute("""
                INSERT INTO prestamos (id_miembro, proposito, monto, fecha_desembolso, 
                                     fecha_vencimiento, estado, interes_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                miembros_dict[miembro_seleccionado],
                proposito,
                monto,
                fecha_desembolso,
                fecha_vencimiento,
                "activo",  # Estado fijo como "activo"
                interes_total
            ))

            con.commit()
            st.success("✅ Préstamo registrado correctamente")
            st.info(f"💰 Total a pagar: ${monto_total:,.2f} (Capital: ${monto:,.2f} + Interés: ${interes_total:,.2f})")
            time.sleep(2)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Error al registrar préstamo: {str(e)}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'con' in locals() and con.is_connected():
                con.close()

    # Mostrar lista de préstamos y formulario de pagos
    mostrar_lista_prestamos(id_grupo)

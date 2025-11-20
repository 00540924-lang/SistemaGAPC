def prestamos_modulo():

    # --------------------------------------
    # Validar sesión y grupo
    # --------------------------------------
    if "id_grupo" not in st.session_state or st.session_state["id_grupo"] is None:
        st.error("⚠️ No tienes un grupo asignado. Contacta al administrador.")
        return

    id_grupo = st.session_state["id_grupo"]

    st.markdown("<h1 style='text-align:center;'>💲 Registro de Préstamos</h1>", unsafe_allow_html=True)

    # --------------------------------------
    # OBTENER VALORES DE REGLAMENTO
    # --------------------------------------
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT interes_por_10
        FROM Reglamento
        WHERE id_grupo = %s
        LIMIT 1
    """, (id_grupo,))
    reglamento = cursor.fetchone()
    con.close()

    # Si no hay reglamento, asignamos un valor por defecto
    interes_por_10 = float(reglamento[0]) if reglamento else 0.0

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

    miembros_dict = {f"{m[1]} - {m[2]}": m[0] for m in miembros}

    # =====================================================
    #   FORMULARIO: REGISTRAR NUEVO PRÉSTAMO
    # =====================================================
    with st.form("form_nuevo_prestamo"):
        st.subheader("📄 Datos del Préstamo")

        miembro_seleccionado = st.selectbox("Selecciona un miembro", list(miembros_dict.keys()))
        proposito = st.text_input("Propósito del préstamo")
        monto = st.number_input("Monto", min_value=0.01, step=0.01)
        fecha_desembolso = st.date_input("Fecha de desembolso", datetime.date.today())
        fecha_vencimiento = st.date_input("Fecha de vencimiento", datetime.date.today())
        firma = st.text_input("Firma del solicitante")

        # Campo de interés se llena AUTOMÁTICAMENTE desde reglamento
        st.markdown("### Interés del préstamo (desde reglamento)")
        interes = st.number_input(
            "Interés aplicado por cada $10 (%)",
            value=float(interes_por_10),
            step=0.01
        )

        estado = st.selectbox("Estado del préstamo", ["Pendiente", "Activo", "Finalizado"])

        enviar = st.form_submit_button("💾 Guardar Préstamo")

    if enviar:
        try:
            con = obtener_conexion()
            cursor = con.cursor()

            cursor.execute("""
                INSERT INTO prestamos (id_miembro, proposito, monto, fecha_desembolso, fecha_vencimiento, firma, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                miembros_dict[miembro_seleccionado],
                proposito,
                monto,
                fecha_desembolso,
                fecha_vencimiento,
                firma,
                estado
            ))

            con.commit()
            st.success("✅ Préstamo registrado correctamente")
            time.sleep(0.5)
            st.experimental_rerun()

        finally:
            cursor.close()
            con.close()

    # =====================================================
    #   MOSTRAR LISTA DE PRÉSTAMOS
    # =====================================================
    mostrar_lista_prestamos(id_grupo)

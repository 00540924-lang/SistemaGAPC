import streamlit as st

def prestamos_modulo():
    st.title("📄 Módulo de Préstamos")

    st.write("Aquí puedes registrar un préstamo sencillo.")

    # -------------------------------
    # FORMULARIO DE PRÉSTAMO
    # -------------------------------
    with st.form("form_prestamo"):
        nombre = st.text_input("Nombre del solicitante")
        monto = st.number_input("Monto del préstamo", min_value=0.0)
        tasa = st.number_input("Tasa de interés (%)", min_value=0.0)
        meses = st.number_input("Plazo en meses", min_value=1, step=1)

        enviado = st.form_submit_button("Guardar préstamo")

    # -------------------------------
    # PROCESAR FORMULARIO
    # -------------------------------
    if enviado:
        if not nombre or monto <= 0 or tasa < 0 or meses <= 0:
            st.error("⚠️ Debes completar todos los campos correctamente.")
            return
        
        interes_mensual = tasa / 100 / 12
        pago_mensual = (monto * interes_mensual) / (1 - (1 + interes_mensual) ** (-meses))

        st.success("✅ Préstamo registrado con éxito")

        st.subheader("📌 Resumen del préstamo")
        st.write(f"**Solicitante:** {nombre}")
        st.write(f"**Monto:** ${monto:,.2f}")
        st.write(f"**Tasa anual:** {tasa}%")
        st.write(f"**Plazo:** {meses} meses")
        st.write(f"**Pago mensual estimado:** ${pago_mensual:,.2f}")

        # -------------------------------
        # PLAN DE PAGOS SENCILLO
        # -------------------------------
        st.subheader("📘 Plan de pagos (simple)")

        saldo = monto
        interes_mensual_real = tasa / 100 / 12
        plan = []

        for i in range(1, meses + 1):
            interes = saldo * interes_mensual_real
            abono_capital = pago_mensual - interes
            saldo -= abono_capital
            if saldo < 0:
                saldo = 0

            plan.append({
                "Mes": i,
                "Pago": round(pago_mensual, 2),
                "Interés": round(interes, 2),
                "Capital": round(abono_capital, 2),
                "Saldo": round(saldo, 2)
            })

        st.table(plan)

import streamlit as st

def caja():
    st.title("📦 Formulario de Caja")

    st.write("Complete los datos correspondientes al movimiento de caja del día.")

    # ----- Datos de encabezado -----
    st.subheader("Encabezado")
    col1, col2 = st.columns(2)
    with col1:
        firma = st.text_input("Firma:")
        t = st.text_input("T:")
    with col2:
        saldo_apertura = st.number_input("Saldo de apertura:", min_value=0.0, step=0.01)

    st.markdown("---")

    # ----- DINERO QUE ENTRA -----
    st.subheader("Dinero que entra")

    multa = st.number_input("Multas pagadas:", min_value=0.0, step=0.01)
    ahorros = st.number_input("Ahorros:", min_value=0.0, step=0.01)
    otras_actividades = st.number_input("Otras actividades:", min_value=0.0, step=0.01)
    pagos_prestamos = st.number_input("Pago de préstamos (capital e interés):", min_value=0.0, step=0.01)
    otros_ingresos = st.number_input("Otros ingresos del grupo:", min_value=0.0, step=0.01)

    total_entra = multa + ahorros + otras_actividades + pagos_prestamos + otros_ingresos
    st.number_input("Total dinero que entra:", value=total_entra, disabled=True)

    saldo_despues_entrada = saldo_apertura + total_entra
    st.number_input("Saldo después de entrada:", value=saldo_despues_entrada, disabled=True)

    st.markdown("---")

    # ----- DINERO QUE SALE -----
    st.subheader("Dinero que sale")

    retiro_ahorros = st.number_input("Retiro de ahorros:", min_value=0.0, step=0.01)
    desembolso = st.number_input("Desembolso de préstamos:", min_value=0.0, step=0.01)
    gastos_grupo = st.number_input("Otros gastos del grupo:", min_value=0.0, step=0.01)

    total_sale = retiro_ahorros + desembolso + gastos_grupo
    st.number_input("Total dinero que sale:", value=total_sale, disabled=True)

    saldo_cierre = saldo_despues_entrada - total_sale
    st.number_input("Saldo de cierre:", value=saldo_cierre, disabled=True)

    st.markdown("---")

    if st.button("Guardar Movimiento"):
        st.success("Movimiento de caja guardado correctamente (placeholder).")


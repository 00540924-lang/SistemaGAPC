def mostrar_reglamento_guardado(reglamento):
    import pandas as pd

    # Si no hay reglamento guardado
    if not reglamento:
        st.info("Aún no hay un reglamento registrado para este grupo.")
        return

    # Convertir valores especiales Decimal / datetime a str
    reglamento_limpio = {}
    for k, v in reglamento.items():
        reglamento_limpio[k] = str(v)  # convierte Decimals, fechas, etc.

    st.subheader("Vista previa del reglamento")

    # ---- OPCIÓN 1: tabla limpia ----
    df = pd.DataFrame(reglamento_limpio.items(), columns=["Campo", "Valor"])
    st.table(df)

    # ---- OPCIÓN 2: vista elegante en texto ----
    with st.expander("Ver versión estilo documento"):
        texto = ""
        for campo, valor in reglamento_limpio.items():
            texto += f"**{campo.replace('_',' ').title()}**: {valor}\n\n"
        st.markdown(texto)

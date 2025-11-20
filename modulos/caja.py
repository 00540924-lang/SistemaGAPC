import streamlit as st
import pandas as pd
from datetime import date
from modulos.db import (
    registrar_movimiento_caja,
    obtener_historial_caja,
    obtener_saldo_caja
)

# ------------------------------------------------------
#     MÓDULO PRINCIPAL – CAJA
# ------------------------------------------------------
def mostrar_caja(id_grupo):

    # ------------------------------------------------------
    #   VALIDACIÓN DE PERMISOS
    # ------------------------------------------------------
    if st.session_state["rol"] != "miembro" and st.session_state["usuario"] != "Dark":
        st.error("🚫 No tienes permisos para acceder al módulo de Caja.")
        return

    st.title("💵 Módulo de Caja")

    menu = ["Registrar Movimiento", "Historial"]
    opcion = st.sidebar.radio("Menú Caja", menu)

    if opcion == "Registrar Movimiento":
        mostrar_registro_caja(id_grupo)
    elif opcion == "Historial":
        mostrar_historial_caja(id_grupo)



# ------------------------------------------------------
#     REGISTRAR MOVIMIENTO
# ------------------------------------------------------
def mostrar_registro_caja(id_grupo):

    st.subheader("➕ Registrar Movimiento en Caja")

    tipo = st.selectbox("Tipo de movimiento", ["Ingreso", "Egreso"])
    monto = st.number_input("Monto ($)", min_value=0.01, format="%.2f")
    descripcion = st.text_area("Descripción")

    if st.button("Guardar Movimiento", use_container_width=True):
        if monto <= 0:
            st.error("❌ El monto debe ser mayor a 0.")
            return

        registrar_movimiento_caja(
            id_grupo=id_grupo,
            tipo=tipo,
            monto=monto,
            descripcion=descripcion,
            registrado_por=st.session_state["usuario"]
        )

        st.success("✅ Movimiento registrado correctamente.")



# ------------------------------------------------------
#     HISTORIAL DE CAJA
# ------------------------------------------------------
def mostrar_historial_caja(id_grupo):

    st.title("📊 Historial de Caja")

    st.info("Si deseas ver todos los registros, deja la fecha vacía.")

    # ---------------------------
    # FILTRO DE FECHA
    # ---------------------------
    fecha_filtro = st.date_input(
        "📅 Filtrar por fecha (opcional)",
        value=None,
        key="filtro_historial_caja"
    )

    # Obtener movimientos de BD
    movimientos = obtener_historial_caja(id_grupo)

    if not movimientos:
        st.warning("No hay movimientos registrados.")
        return

    # Convertir a DataFrame
    df = pd.DataFrame(movimientos)

    # Normalizar fecha
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.date

    # Si el usuario elige una fecha, filtramos
    if fecha_filtro:
        df = df[df["fecha"] == fecha_filtro]

    if df.empty:
        st.warning("No hay movimientos para la fecha seleccionada.")
        return

    # Ordenar por fecha
    df = df.sort_values(by="fecha", ascending=False)

    # Renombrar columnas para visualización bonita
    df = df.rename(columns={
        "fecha": "Fecha",
        "tipo": "Tipo",
        "monto": "Monto ($)",
        "descripcion": "Descripción",
        "registrado_por": "Registrado por"
    })

    st.subheader("📄 Movimientos encontrados")

    # Mostrar tabla elegante
    st.dataframe(
        df,
        use_container_width=True,
        height=450
    )

    # Mostrar saldo final
    saldo = obtener_saldo_caja(id_grupo)
    st.info(f"💰 **Saldo actual en caja: ${saldo:.2f}**")

    # ===============================
    # 8. Regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    cursor.close()
    conn.close()

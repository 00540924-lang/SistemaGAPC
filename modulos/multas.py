import streamlit as st
import pandas as pd
import time
from conexion.py import obtener_conexion


# ------------------------------------------------------------
# 📌 FUNCIÓN PARA GUARDAR MULTA
# ------------------------------------------------------------
def guardar_multa(id_miembro, fecha, monto):
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute(
        "INSERT INTO Multas (id_miembro, fecha, monto_a_pagar) VALUES (%s, %s, %s)",
        (id_miembro, fecha, monto)
    )
    con.commit()
    cursor.close()
    con.close()


# ------------------------------------------------------------
# 📌 FUNCIÓN PARA ELIMINAR MULTA
# ------------------------------------------------------------
def eliminar_multa(id_multa):
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("DELETE FROM Multas WHERE id_multa = %s", (id_multa,))
    con.commit()
    cursor.close()
    con.close()


# ------------------------------------------------------------
# 📌 FUNCIÓN PARA MOSTRAR TABLA DE MULTAS (sin pagada)
# ------------------------------------------------------------
def mostrar_tabla_multas(id_grupo):
    try:
        con = obtener_conexion()
        cursor = con.cursor()

        cursor.execute("""
            SELECT MT.id_multa, M.nombre, MT.fecha, MT.monto_a_pagar
            FROM Multas MT
            JOIN Miembros M ON MT.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            ORDER BY MT.id_multa
        """, (id_grupo,))

        resultados = cursor.fetchall()

        # 👇 DataFrame CORRECTO (4 columnas)
        df = pd.DataFrame(resultados, columns=["ID", "Miembro", "Fecha", "Monto"])

        if df.empty:
            st.info("No hay multas registradas en este grupo.")
            return

        df_display = df.reset_index(drop=True)
        df_display.insert(0, "No.", range(1, len(df_display) + 1))

        st.markdown(
            "<h3 style='text-align:center;'>📄 Multas Registradas</h3>", 
            unsafe_allow_html=True
        )

        st.dataframe(
            df_display[["No.", "Miembro", "Fecha", "Monto"]].style.hide(axis="index"),
            use_container_width=True
        )

        # Lista de selección para editar-eliminar
        multa_dict = {
            f"{row['Miembro']} - {row['Fecha']}": row 
            for _, row in df.iterrows()
        }

        seleccionado = st.selectbox(
            "Selecciona una multa:",
            options=list(multa_dict.keys())
        )

        if seleccionado:
            multa = multa_dict[seleccionado]
            col1, col2 = st.columns(2)

            with col1:
                if st.button("✏️ Editar", key=f"editar_{multa['ID']}"):
                    st.session_state["editar_multa"] = multa
                    st.rerun()

            with col2:
                if st.button("🗑️ Eliminar", key=f"eliminar_{multa['ID']}"):
                    eliminar_multa(multa["ID"])
                    st.success("Multa eliminada correctamente ✔️")
                    time.sleep(0.5)
                    st.rerun()

    finally:
        cursor.close()
        con.close()


# ------------------------------------------------------------
# 📌 FUNCIÓN PRINCIPAL DEL MÓDULO MULTAS
# ------------------------------------------------------------
def mostrar_multas(id_grupo):
    st.title("📕 Registro de Multas")

    # ✔ Cargar miembros del grupo
    con = obtener_conexion()
    cursor = con.cursor()
    cursor.execute("""
        SELECT M.id_miembro, M.nombre 
        FROM Miembros M 
        JOIN Grupomiembros G ON G.id_miembro = M.id_miembro
        WHERE G.id_grupo = %s
        ORDER BY M.nombre
    """, (id_grupo,))
    miembros = cursor.fetchall()
    cursor.close()
    con.close()

    nombres = {nombre: mid for mid, nombre in miembros}

    st.subheader("➕ Registrar nueva multa")

    col1, col2 = st.columns(2)

    with col1:
        nombre_sel = st.selectbox("Miembro:", list(nombres.keys()))

    with col2:
        fecha = st.date_input("Fecha de multa")

    monto = st.number_input("Monto a pagar ($):", min_value=0.00, step=0.25)

    if st.button("Guardar multa"):
        guardar_multa(nombres[nombre_sel], fecha, monto)
        st.success("Multa registrada con éxito ✔️")
        time.sleep(0.5)
        st.rerun()

    st.write("---")

    mostrar_tabla_multas(id_grupo)

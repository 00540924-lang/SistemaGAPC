import streamlit as st
from datetime import datetime
from modulos.config.conexion import obtener_conexion
import pandas as pd

def mostrar_reuniones(id_grupo):
    
    rol = st.session_state.get("rol", "").lower()
    if rol != "miembro":
        st.error("❌ Solo los miembros pueden acceder a este módulo.")
        return

    if not id_grupo:
        st.error("❌ No se encontró el grupo del usuario. Contacte al administrador.")
        return

    nombre_grupo = st.session_state.get("nombre_grupo", "Sin Grupo")

    st.markdown(
        f"<h1 style='text-align:center; color:#4C3A60;'>📋 Registro de reuniones grupo {nombre_grupo}</h1>",
        unsafe_allow_html=True
    )

    conn = obtener_conexion()
    if not conn:
        st.error("❌ Error al conectar a la base de datos.")
        return

    cursor = conn.cursor(dictionary=True)

    # ===============================
    # Datos de la reunión
    # ===============================
    st.subheader("Información de la reunión")
    fecha = st.date_input("📅 Fecha de la reunión", datetime.now().date())
    hora = st.time_input("⏰ Hora de inicio", datetime.now().time())

    # ===============================
    # ASISTENCIA INTEGRADA (Antes de agenda)
    # ===============================
    st.subheader("🧑‍🤝‍🧑 Asistencia de miembros del grupo")

    # Obtener miembros del grupo
    cursor.execute("""
        SELECT M.id_miembro, M.Nombre
        FROM Miembros M
        JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
        WHERE GM.id_grupo = %s
        ORDER BY M.Nombre
    """, (id_grupo,))
    miembros = cursor.fetchall()

    if not miembros:
        st.warning("⚠️ No hay miembros registrados en este grupo.")
        cursor.close()
        conn.close()
        return

    # Crear tabla editable
    df_asistencia = pd.DataFrame(miembros)
    df_asistencia = df_asistencia.rename(columns={"Nombre": "Miembro"})
    df_asistencia["Asistencia"] = "Presente"

    tabla_asistencia = st.data_editor(
        df_asistencia,
        column_config={
            "Asistencia": st.column_config.SelectboxColumn(
                "Asistencia",
                options=["Presente", "Ausente"],
                required=True
            ),
            "id_miembro": None
        },
        hide_index=True,
        use_container_width=True,
    )

    # ===============================
    # Agenda de la reunión
    # ===============================
    st.subheader("📝 Agenda de actividades")

    secciones = {
        "Empezar la reunión": [
            "La presidenta abre formalmente la reunión.",
            "La secretaria registra asistencia y multas.",
            "La secretaria lee las reglas internas."
        ],
        "Dinero que entra": [
            "La tesorera cuenta el dinero de la caja.",
            "Las socias depositan ahorros.",
            "Las socias depositan dinero de otras actividades.",
            "La secretaria calcula el total de dinero que entra.",
            "La tesorera verifica el monto total."
        ],
        "Dinero que sale": [
            "Las socias solicitan y evalúan préstamos.",
            "La tesorera desembolsa préstamos aprobados.",
            "La secretaria registra desembolsos e intereses.",
            "La secretaria calcula total de dinero que sale.",
            "La tesorera verifica el dinero y anuncia el saldo.",
            "La presidenta cierra la caja y entrega llaves."
        ],
        "Cerrar la reunión": [
            "La presidenta pregunta si hay asuntos pendientes.",
            "La presidenta cierra formalmente la reunión."
        ]
    }

    colores = ["#E3F2FD", "#FFF3E0", "#E8F5E9", "#FCE4EC"]
    agenda_completa = ""

    for i, (titulo, items) in enumerate(secciones.items()):
        st.markdown(
            f"""
            <div style='background-color:{colores[i]}; padding:15px; border-radius:12px; 
                        margin-bottom:12px; box-shadow: 0 4px 10px rgba(0,0,0,0.08);'>
                <h4 style='color:#4C3A60;'>{titulo}</h4>
                <ul>
                    {''.join([f"<li>{item}</li>" for item in items])}
                </ul>
            </div>
            """,
            unsafe_allow_html=True
        )
        agenda_completa += f"**{titulo.upper()}**\n" + "\n".join(f"- {x}" for x in items) + "\n\n"

    # ===============================
    # Observaciones
    # ===============================
    st.subheader("🗒 Observaciones")
    observaciones = st.text_area("Escriba aquí las observaciones de la reunión", height=150)

    # ===============================
    # GUARDAR TODO (Reunión + Asistencia)
    # ===============================
    if st.button("💾 Guardar reunión"):
        
        # Guardar reunión
        cursor.execute("""
            INSERT INTO Reuniones (id_grupo, fecha, hora, agenda, observaciones)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_grupo, fecha, hora, agenda_completa, observaciones))
        conn.commit()

        # Guardar asistencia
        for _, row in tabla_asistencia.iterrows():
            cursor.execute("""
                INSERT INTO Asistencia (id_grupo, fecha, id_miembro, asistencia)
                VALUES (%s, %s, %s, %s)
            """, (id_grupo, fecha, row["id_miembro"], row["Asistencia"]))

        conn.commit()
        st.success("✅ Reunión y asistencia guardadas con éxito.")
        st.rerun()

    # ===============================
    # Historial de observaciones
    # ===============================
    st.markdown("<br><h2 style='color:#4C3A60;'>📚 Historial de observaciones</h2>", unsafe_allow_html=True)

    with st.expander("Filtrar por fecha"):
        fecha_seleccionada = st.date_input("Seleccione la fecha", value=datetime.now().date())

    cursor.execute("""
        SELECT id, fecha, observaciones
        FROM Reuniones
        WHERE id_grupo = %s AND fecha = %s
        ORDER BY fecha DESC
    """, (id_grupo, fecha_seleccionada))

    registros = cursor.fetchall()

    if registros:
        colores_tarjeta = ["#E3F2FD", "#FFF3E0", "#E8F5E9", "#FCE4EC"]

        for i, r in enumerate(registros):
            color = colores_tarjeta[i % 4]
            fecha_str = r["fecha"].strftime("%d/%m/%Y")

            st.markdown(
                f"""
                <div style="
                    background-color:{color};
                    padding:18px;
                    border-radius:12px;
                    margin-bottom:18px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.10);
                ">
                    <strong>📅 Fecha:</strong> {fecha_str}<br><br>
                    <strong>🗒 Observaciones:</strong><br>
                    <p style="margin-top:5px; white-space:pre-wrap;">{r['observaciones']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("🗑 Borrar observación", key=f"del_{r['id']}"):
                cursor.execute("DELETE FROM Reuniones WHERE id=%s", (r["id"],))
                conn.commit()
                st.success("❌ Observación eliminada.")
                st.rerun()

    else:
        st.info("No hay observaciones registradas para esta fecha.")

    # ===============================
    # Regresar
    # ===============================
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    cursor.close()
    conn.close()


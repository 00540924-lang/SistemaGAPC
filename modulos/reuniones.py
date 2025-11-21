import streamlit as st
from datetime import datetime
import mysql.connector
from modulos.config.conexion import obtener_conexion
import pandas as pd

def mostrar_reuniones(id_grupo):

    # ===============================
    # Validación de usuario
    # ===============================
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
    # Crear nueva reunión
    # ===============================
    with st.container():
        st.subheader("Información de la reunión")
        fecha = st.date_input("📅 Fecha de la reunión", datetime.now().date())
        hora = st.time_input("⏰ Hora de inicio", datetime.now().time())

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

        st.subheader("🗒 Observaciones")
        observaciones = st.text_area("Escriba aquí las observaciones de la reunión", height=150)

        if st.button("💾 Guardar reunión"):
            cursor.execute("""
                INSERT INTO Reuniones (id_grupo, fecha, hora, agenda, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_grupo, fecha, hora, agenda_completa, observaciones))
            conn.commit()
            st.success("✅ Reunión guardada con éxito.")
            st.rerun()

    # ===============================
    # Historial de observaciones (solo mostrar + borrar)
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
                    padding:20px;
                    border-radius:12px;
                    margin-bottom:10px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.10);
                ">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong>📅 Fecha:</strong> {fecha_str}<br>
                            <strong>🗒 Observaciones:</strong><br>
                        </div>
                        <form action="" method="post">
                            <button style="
                                background-color:#D32F2F;
                                color:white;
                                border:none;
                                padding:8px 14px;
                                border-radius:8px;
                                cursor:pointer;
                            ">
                                🗑 Borrar
                            </button>
                        </form>
                    </div>
                    <p style="margin-top:10px; white-space:pre-wrap;">{r['observaciones']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Botón borrar con key único
            if st.button(f"🗑 Confirmar borrado", key=f"del_{r['id']}"):
                cursor.execute("DELETE FROM Reuniones WHERE id=%s", (r["id"],))
                conn.commit()
                st.success("❌ Observación eliminada.")
                st.rerun()

    else:
        st.info("No hay observaciones registradas para esta fecha.")

    # ===============================
    # Regresar al menú
    # ===============================
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    cursor.close()
    conn.close()

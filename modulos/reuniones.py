import streamlit as st
from datetime import datetime
import mysql.connector
from modulos.config.conexion import obtener_conexion
import pandas as pd

def mostrar_reuniones(id_grupo):
    """
    Módulo de Reuniones.
    Solo accesible por usuarios con rol 'miembro'.
    """

    rol = st.session_state.get("rol", "").lower()
    usuario = st.session_state.get("usuario", "").lower()

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
        st.markdown(
            """
            <div style='background-color:#D1C4E9; padding:5px; border-radius:15px; 
                        box-shadow: 0 6px 15px rgba(0,0,0,0.12);'>
            """,
            unsafe_allow_html=True
        )

        st.subheader("Información de la reunión")
        fecha = st.date_input("📅 Fecha de la reunión", datetime.now().date())
        hora = st.time_input("⏰ Hora de inicio", datetime.now().time())

        st.markdown("<hr style='border:1px solid #D1C4E9;'>", unsafe_allow_html=True)
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

        st.markdown("<hr style='border:1px solid #D1C4E9;'>", unsafe_allow_html=True)
        st.subheader("🗒 Observaciones")
        observaciones = st.text_area("Escriba aquí las observaciones de la reunión", height=150)

        st.markdown("<hr style='border:1px solid #D1C4E9;'>", unsafe_allow_html=True)
        if st.button("💾 Guardar reunión", help="Guarda la reunión en la base de datos"):
            cursor.execute("""
                INSERT INTO Reuniones (id_grupo, fecha, hora, agenda, observaciones)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_grupo, fecha, hora, agenda_completa, observaciones))
            conn.commit()
            st.success("✅ Reunión guardada con éxito.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ===============================
    # Historial de observaciones con editar y borrar
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
        st.markdown("<div style='display:flex; flex-direction:column; gap:12px;'>", unsafe_allow_html=True)
        
        colores_tarjeta = ["#E3F2FD", "#FFF3E0", "#E8F5E9", "#FCE4EC"]
        for i, registro in enumerate(registros):
            color = colores_tarjeta[i % len(colores_tarjeta)]
            fecha_str = registro['fecha'].strftime("%d/%m/%Y") if isinstance(registro['fecha'], datetime) else str(registro['fecha'])
            
            st.markdown(
                f"""
                <div style='background-color:{color}; padding:15px; border-radius:12px; 
                            box-shadow: 0 4px 10px rgba(0,0,0,0.08);'>
                    <strong>📅 Fecha:</strong> {fecha_str}<br>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            edit_key = f"edit_{registro['id']}"
            borrar_key = f"delete_{registro['id']}"
            texto_editable = st.text_area("", value=registro['observaciones'], key=edit_key, height=100)
            
            col1, col2 = st.columns([1,1])
            with col1:
                if st.button("💾 Guardar cambios", key=f"save_{registro['id']}"):
                    cursor.execute("UPDATE Reuniones SET observaciones=%s WHERE id=%s", (texto_editable, registro['id']))
                    conn.commit()
                    st.success("✅ Observación actualizada.")
                    st.experimental_rerun()
            with col2:
                if st.button("🗑 Borrar", key=borrar_key):
                    cursor.execute("DELETE FROM Reuniones WHERE id=%s", (registro['id'],))
                    conn.commit()
                    st.success("❌ Observación eliminada.")
                    st.experimental_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("No hay observaciones registradas para la fecha seleccionada.")

    # ===============================
    # Botón regresar
    # ===============================
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    cursor.close()
    conn.close()

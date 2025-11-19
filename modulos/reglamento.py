import streamlit as st
from modulos.config.conexion import obtener_conexion
import datetime

def mostrar_reglamento():

    st.markdown("<h2 style='text-align:center; color:#4C3A60;'>📜 Reglamento Interno del Grupo</h2>", unsafe_allow_html=True)

    st.write("Complete o actualice el reglamento interno de su grupo.")

    con = obtener_conexion()
    cursor = con.cursor()

    # ---------------------------------------
    # FORMULARIO DEL REGLAMENTO
    # ---------------------------------------
    with st.form("form_reglamento"):

        st.subheader("Información del grupo")
        nombre_grupo = st.text_input("Nombre del grupo")
        comunidad = st.text_input("Comunidad")
        fecha_formacion = st.date_input("Fecha de formación", datetime.date.today())

        st.subheader("Reuniones")
        dia_reunion = st.text_input("Día de reunión")
        hora_reunion = st.text_input("Hora de reunión")
        lugar_reunion = st.text_input("Lugar")
        frecuencia_reunion = st.text_input("Frecuencia")

        st.subheader("Comité de dirección")
        presidenta = st.text_input("Presidenta")
        secretaria = st.text_input("Secretaria")
        tesorera = st.text_input("Tesorera")
        responsable_llave = st.text_input("Responsable de llave")

        st.subheader("Asistencia")
        multa_ausencia = st.number_input("Multa por ausencia ($)", min_value=0.0, step=0.5)
        razones_sin_multa = st.text_area("Razones válidas de ausencia sin multa")
        deposito_minimo = st.number_input("Depósito mínimo por reunión ($)", min_value=0.0, step=0.5)

        st.subheader("Préstamos")
        interes_por_10 = st.number_input("Interés por cada $10 (%)", min_value=0.0, step=0.5)
        max_prestamo = st.number_input("Monto máximo de préstamo ($)", min_value=0.0, step=1.0)
        max_plazo = st.text_input("Plazo máximo permitido")
        un_solo_prestamo = st.checkbox("Solo un préstamo activo a la vez")
        evaluacion_monto_plazo = st.checkbox("Evaluar según monto y plazo")

        st.subheader("Ciclo")
        fecha_inicio_ciclo = st.date_input("Inicio del ciclo", datetime.date.today())
        fecha_fin_ciclo = st.date_input("Fin del ciclo", datetime.date.today())

        st.subheader("Meta social")
        meta_social = st.text_area("Meta social del grupo")

        st.subheader("Otras reglas")
        otras_reglas = st.text_area("Otras reglas del grupo")

        enviar = st.form_submit_button("💾 Guardar Reglamento")

    # ---------------------------------------
    # GUARDAR REGLAMENTO EN LA BASE DE DATOS
    # ---------------------------------------
    if enviar:

        query = """
        INSERT INTO Reglamento (
            id_grupo, comunidad, fecha_formacion,
            dia_reunion, hora_reunion, lugar_reunion, frecuencia_reunion,
            presidenta, secretaria, tesorera, responsable_llave,
            multa_ausencia, razones_sin_multa, deposito_minimo,
            interes_por_10, max_prestamo, max_plazo,
            un_solo_prestamo, evaluacion_monto_plazo,
            fecha_inicio_ciclo, fecha_fin_ciclo,
            meta_social, otras_reglas
        )
        VALUES (
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s,
            %s, %s, %s,
            %s, %s,
            %s, %s,
            %s, %s
        )
        """

        datos = (
            st.session_state.get("id_grupo", 1),  # <--- Por ahora usa 1
            comunidad, fecha_formacion,
            dia_reunion, hora_reunion, lugar_reunion, frecuencia_reunion,
            presidenta, secretaria, tesorera, responsable_llave,
            multa_ausencia, razones_sin_multa, deposito_minimo,
            interes_por_10, max_prestamo, max_plazo,
            un_solo_prestamo, evaluacion_monto_plazo,
            fecha_inicio_ciclo, fecha_fin_ciclo,
            meta_social, otras_reglas
        )

        cursor.execute(query, datos)
        con.commit()

        st.success("✅ Reglamento guardado correctamente.")

        cursor.close()
        con.close()

    # ------------------ BOTÓN REGRESAR ------------------
    st.write("")  # espaciado
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

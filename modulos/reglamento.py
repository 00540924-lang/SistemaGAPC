import streamlit as st
from modulos.config.conexion import obtener_conexion
import datetime

def mostrar_reglamento():

    st.markdown("<h2 style='text-align:center; color:#4C3A60;'>📜 Reglamento Interno del Grupo</h2>", 
                unsafe_allow_html=True)

    id_grupo = st.session_state.get("id_grupo", 1)  # ← Cambiar cuando agregues multi-grupo

    # -------------------------------------------------------------------------
    #         📌 1. VERIFICAR SI YA HAY REGLAMENTO GUARDADO EN MYSQL
    # -------------------------------------------------------------------------
    con = obtener_conexion()
    cursor = con.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Reglamento WHERE id_grupo = %s LIMIT 1", (id_grupo,))
    reglamento_existente = cursor.fetchone()

    cursor.close()
    con.close()

    st.write("Complete o actualice el reglamento interno del grupo.")

    # -------------------------------------------------------------------------
    #         📌 2. PRELLENAR CAMPOS SI YA EXISTE REGLAMENTO
    # -------------------------------------------------------------------------
    def get_val(campo, defecto=""):
        if reglamento_existente and campo in reglamento_existente:
            return reglamento_existente[campo]
        return defecto

    # -------------------------------------------------------------------------
    #     📋 3. FORMULARIO — SE RELLENA AUTOMÁTICAMENTE SI YA EXISTE
    # -------------------------------------------------------------------------
    with st.form("form_reglamento"):

        st.subheader("Información del grupo")
        comunidad = st.text_input("Comunidad", get_val("comunidad"))
        fecha_formacion = st.date_input("Fecha de formación", get_val("fecha_formacion", datetime.date.today()))

        st.subheader("Reuniones")
        dia_reunion = st.text_input("Día de reunión", get_val("dia_reunion"))
        hora_reunion = st.text_input("Hora de reunión", get_val("hora_reunion"))
        lugar_reunion = st.text_input("Lugar", get_val("lugar_reunion"))
        frecuencia_reunion = st.text_input("Frecuencia", get_val("frecuencia_reunion"))

        st.subheader("Comité de dirección")
        presidenta = st.text_input("Presidenta", get_val("presidenta"))
        secretaria = st.text_input("Secretaria", get_val("secretaria"))
        tesorera = st.text_input("Tesorera", get_val("tesorera"))
        responsable_llave = st.text_input("Responsable de llave", get_val("responsable_llave"))

        st.subheader("Asistencia")
        multa_ausencia = st.number_input("Multa por ausencia ($)", min_value=0.0, step=0.5, value=get_val("multa_ausencia", 0.0))
        razones_sin_multa = st.text_area("Razones válidas de ausencia sin multa", get_val("razones_sin_multa"))
        deposito_minimo = st.number_input("Depósito mínimo por reunión ($)", min_value=0.0, step=0.5, value=get_val("deposito_minimo", 0.0))

        st.subheader("Préstamos")
        interes_por_10 = st.number_input("Interés por cada $10 (%)", min_value=0.0, step=0.5, value=get_val("interes_por_10", 0.0))
        max_prestamo = st.number_input("Monto máximo de préstamo ($)", min_value=0.0, step=1.0, value=get_val("max_prestamo", 0.0))
        max_plazo = st.text_input("Plazo máximo permitido", get_val("max_plazo"))
        un_solo_prestamo = st.checkbox("Solo un préstamo activo a la vez", value=bool(get_val("un_solo_prestamo", 0)))
        evaluacion_monto_plazo = st.checkbox("Evaluar según monto y plazo", value=bool(get_val("evaluacion_monto_plazo", 0)))

        st.subheader("Ciclo")
        fecha_inicio_ciclo = st.date_input("Inicio del ciclo", get_val("fecha_inicio_ciclo", datetime.date.today()))
        fecha_fin_ciclo = st.date_input("Fin del ciclo", get_val("fecha_fin_ciclo", datetime.date.today()))

        st.subheader("Meta social")
        meta_social = st.text_area("Meta social del grupo", get_val("meta_social"))

        st.subheader("Otras reglas")
        otras_reglas = st.text_area("Otras reglas del grupo", get_val("otras_reglas"))

        guardar = st.form_submit_button("💾 Guardar Cambios")

    # -------------------------------------------------------------------------
    #         💾 4. GUARDAR O ACTUALIZAR EN MYSQL
    # -------------------------------------------------------------------------
    if guardar:

        con = obtener_conexion()
        cursor = con.cursor()

        if reglamento_existente:
            # -----------------------------------------
            # ⭐ ACTUALIZAR REGLAMENTO EXISTENTE
            # -----------------------------------------
            query = """
            UPDATE Reglamento SET
                comunidad=%s, fecha_formacion=%s,
                dia_reunion=%s, hora_reunion=%s, lugar_reunion=%s, frecuencia_reunion=%s,
                presidenta=%s, secretaria=%s, tesorera=%s, responsable_llave=%s,
                multa_ausencia=%s, razones_sin_multa=%s, deposito_minimo=%s,
                interes_por_10=%s, max_prestamo=%s, max_plazo=%s,
                un_solo_prestamo=%s, evaluacion_monto_plazo=%s,
                fecha_inicio_ciclo=%s, fecha_fin_ciclo=%s,
                meta_social=%s, otras_reglas=%s
            WHERE id_grupo = %s
            """
            datos = (
                comunidad, fecha_formacion,
                dia_reunion, hora_reunion, lugar_reunion, frecuencia_reunion,
                presidenta, secretaria, tesorera, responsable_llave,
                multa_ausencia, razones_sin_multa, deposito_minimo,
                interes_por_10, max_prestamo, max_plazo,
                un_solo_prestamo, evaluacion_monto_plazo,
                fecha_inicio_ciclo, fecha_fin_ciclo,
                meta_social, otras_reglas,
                id_grupo
            )

            cursor.execute(query, datos)
            con.commit()
            st.success("✅ Reglamento actualizado correctamente.")

        else:
            # -----------------------------------------
            # ⭐ INSERTAR NUEVO REGLAMENTO
            # -----------------------------------------
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
                id_grupo, comunidad, fecha_formacion,
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
            st.success("✅ Reglamento creado correctamente.")

        cursor.close()
        con.close()
        st.rerun()

    # -------------------------------------------------------------------------
    #  ⬅️ BOTÓN PARA VOLVER AL MENÚ
    # -------------------------------------------------------------------------
    if st.button("⬅️ Regresar al menú"):
        st.session_state["page"] = "menu"
        st.rerun()


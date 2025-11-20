import streamlit as st
import mysql.connector

def mostrar_reglamento():

    # ============================
    # VALIDACIÓN DE SESIÓN
    # ============================
    if "usuario" not in st.session_state:
        st.error("Debes iniciar sesión.")
        return

    id_grupo = st.session_state.get("id_grupo", None)
    nombre_grupo = st.session_state.get("nombre_grupo", None)

    if id_grupo is None:
        st.error("Este usuario no pertenece a ningún grupo.")
        return

    # ============================
    # TÍTULO PRINCIPAL
    # ============================
    st.markdown(
        f"<h2 style='text-align:center;'>📘 Reglamento interno del grupo <b>{nombre_grupo}</b></h2>",
        unsafe_allow_html=True
    )

    # ============================
    # CONEXIÓN A LA BD
    # ============================
    conn = mysql.connector.connect(
        host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
        user="u1ok2gqomnp9hrku",
        password="VWvN6Pw7wKdfDU9uINZT",
        database="bzn5gsi7ken7lufcglbg"
    )
    cursor = conn.cursor(dictionary=True)

    # ============================
    # OBTENER REGLAMENTO DEL GRUPO
    # ============================
    cursor.execute("SELECT * FROM Reglamento WHERE id_grupo = %s", (id_grupo,))
    reglamento = cursor.fetchone()

    # ============================
    # FORMULARIO
    # ============================

    with st.form("form_reglamento"):
        comunidad = st.text_input("Comunidad:", reglamento["comunidad"] if reglamento else "")
        fecha_formacion = st.date_input("Fecha de formación:", reglamento["fecha_formacion"] if reglamento else None)
        dia_reunion = st.text_input("Día de reunión:", reglamento["dia_reunion"] if reglamento else "")
        hora_reunion = st.text_input("Hora de reunión:", reglamento["hora_reunion"] if reglamento else "")
        lugar_reunion = st.text_input("Lugar de reunión:", reglamento["lugar_reunion"] if reglamento else "")
        frecuencia_reunion = st.text_input("Frecuencia de reuniones:", reglamento["frecuencia_reunion"] if reglamento else "")
        presidenta = st.text_input("Presidenta:", reglamento["presidenta"] if reglamento else "")
        secretaria = st.text_input("Secretaria:", reglamento["secretaria"] if reglamento else "")
        tesorera = st.text_input("Tesorera:", reglamento["tesorera"] if reglamento else "")
        responsable_llave = st.text_input("Responsable de la llave:", reglamento["responsable_llave"] if reglamento else "")
        multa_ausencia = st.number_input("Multa por ausencia:", value=float(reglamento["multa_ausencia"]) if reglamento and reglamento["multa_ausencia"] else 0.00)
        razones_sin_multa = st.text_area("Razones válidas sin multa:", reglamento["razones_sin_multa"] if reglamento else "")
        deposito_minimo = st.number_input("Depósito mínimo:", value=float(reglamento["deposito_minimo"]) if reglamento and reglamento["deposito_minimo"] else 0.00)
        interes_por_10 = st.number_input("Interés por 10 semanas (%):", value=float(reglamento["interes_por_10"]) if reglamento and reglamento["interes_por_10"] else 0.00)
        max_prestamo = st.number_input("Monto máximo de préstamo:", value=float(reglamento["max_prestamo"]) if reglamento and reglamento["max_prestamo"] else 0.00)
        max_plazo = st.text_input("Plazo máximo de préstamo:", reglamento["max_plazo"] if reglamento else "")
        un_solo_prestamo = st.checkbox("Solo un préstamo por miembro", value=bool(reglamento["un_solo_prestamo"]) if reglamento else False)
        evaluacion_monto_plazo = st.checkbox("Evaluación previa del monto y plazo", value=bool(reglamento["evaluacion_monto_plazo"]) if reglamento else False)
        fecha_inicio_ciclo = st.date_input("Fecha inicio del ciclo:", reglamento["fecha_inicio_ciclo"] if reglamento else None)
        fecha_fin_ciclo = st.date_input("Fecha fin del ciclo:", reglamento["fecha_fin_ciclo"] if reglamento else None)
        meta_social = st.text_area("Meta social del grupo:", reglamento["meta_social"] if reglamento else "")
        otras_reglas = st.text_area("Otras reglas:", reglamento["otras_reglas"] if reglamento else "")

        submitted = st.form_submit_button("💾 Guardar reglamento")

    # ============================
    # GUARDAR CAMBIOS
    # ============================
    if submitted:
        if reglamento:  
            # === ACTUALIZAR ===
            cursor.execute("""
                UPDATE Reglamento SET
                    comunidad=%s, fecha_formacion=%s, dia_reunion=%s, hora_reunion=%s,
                    lugar_reunion=%s, frecuencia_reunion=%s, presidenta=%s, secretaria=%s,
                    tesorera=%s, responsable_llave=%s, multa_ausencia=%s, razones_sin_multa=%s,
                    deposito_minimo=%s, interes_por_10=%s, max_prestamo=%s, max_plazo=%s,
                    un_solo_prestamo=%s, evaluacion_monto_plazo=%s, fecha_inicio_ciclo=%s,
                    fecha_fin_ciclo=%s, meta_social=%s, otras_reglas=%s
                WHERE id=%s
            """, (
                comunidad, fecha_formacion, dia_reunion, hora_reunion,
                lugar_reunion, frecuencia_reunion, presidenta, secretaria,
                tesorera, responsable_llave, multa_ausencia, razones_sin_multa,
                deposito_minimo, interes_por_10, max_prestamo, max_plazo,
                un_solo_prestamo, evaluacion_monto_plazo, fecha_inicio_ciclo,
                fecha_fin_ciclo, meta_social, otras_reglas, reglamento["id"]
            ))

        else:
            # === INSERTAR ===
            cursor.execute("""
                INSERT INTO Reglamento (
                    id_grupo, comunidad, fecha_formacion, dia_reunion, hora_reunion,
                    lugar_reunion, frecuencia_reunion, presidenta, secretaria, tesorera,
                    responsable_llave, multa_ausencia, razones_sin_multa, deposito_minimo,
                    interes_por_10, max_prestamo, max_plazo, un_solo_prestamo,
                    evaluacion_monto_plazo, fecha_inicio_ciclo, fecha_fin_ciclo, meta_social,
                    otras_reglas
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                          %s, %s, %s, %s, %s, %s, %s)
            """, (
                id_grupo, comunidad, fecha_formacion, dia_reunion, hora_reunion,
                lugar_reunion, frecuencia_reunion, presidenta, secretaria, tesorera,
                responsable_llave, multa_ausencia, razones_sin_multa, deposito_minimo,
                interes_por_10, max_prestamo, max_plazo, un_solo_prestamo,
                evaluacion_monto_plazo, fecha_inicio_ciclo, fecha_fin_ciclo, meta_social,
                otras_reglas
            ))

        conn.commit()
        st.success("Reglamento guardado correctamente 🎉")
        st.rerun()

    conn.close()

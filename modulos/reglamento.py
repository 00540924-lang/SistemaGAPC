import streamlit as st
import mysql.connector
from datetime import datetime
from reportlab.pdfgen import canvas
import pandas as pd
import os

# ========== CONFIGURACIÓN DB ==========
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="uiazxdhtd3r8o7uv",
            password="uGjZ9MXWemv7vPsjOdA5",
            database="bzn5gsi7ken7lufcglbg"
        )
        return conn
    except mysql.connector.Error as e:
        st.error(f"❌ Error al conectar con MySQL: {e}")
        return None


# ========== GENERAR PDF ==========
def generar_pdf(reglamento, nombre_grupo):

    nombre_archivo = f"Reglamento_{nombre_grupo}.pdf"
    ruta_pdf = os.path.join("/tmp", nombre_archivo)

    c = canvas.Canvas(ruta_pdf)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"Reglamento interno del grupo {nombre_grupo}")
    c.setFont("Helvetica", 12)

    y = 770
    for campo, valor in reglamento.items():
        if y < 50:
            c.showPage()
            y = 800
        c.drawString(50, y, f"{campo.replace('_',' ').title()}: {valor}")
        y -= 20

    c.save()
    return ruta_pdf


# ========== VISTA ==========
def mostrar_reglamento_guardado(reglamento):
    st.subheader("Vista previa del reglamento")

    if not reglamento:
        st.info("Aún no hay un reglamento registrado para este grupo.")
        return

    limpieza = {}
    for k, v in reglamento.items():
        limpieza[k] = str(v)

    df = pd.DataFrame(limpieza.items(), columns=["Campo", "Valor"])
    st.table(df)

    with st.expander("Ver versión estilo documento"):
        texto = ""
        for campo, valor in limpieza.items():
            texto += f"**{campo.replace('_',' ').title()}**: {valor}\n\n"
        st.markdown(texto)


# ========== PRINCIPAL ==========
def mostrar_reglamento():

    if "id_grupo" not in st.session_state:
        st.error("No se ha establecido el grupo del usuario.")
        return

    id_grupo = st.session_state["id_grupo"]
    nombre_grupo = st.session_state.get("nombre_grupo", "SinNombre")

    st.title(f"Reglamento interno del grupo {nombre_grupo}")

    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor(dictionary=True)

    # =================== CONSULTA ===================
    cursor.execute("SELECT * FROM Reglamento WHERE id_grupo = %s", (id_grupo,))
    reglamento = cursor.fetchone()

    # =================== FORMULARIO ===================
    st.subheader("Formulario del reglamento")

    dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
    dia_reunion = st.multiselect("Días de reunión", dias_semana,
                                 default=(reglamento["dia_reunion"].split(",") if reglamento else []))

    hora_reunion = st.time_input(
        "Hora de reunión",
        value=datetime.strptime(reglamento["hora_reunion"], "%H:%M").time() if reglamento else datetime.now().time()
    )

    comunidad = st.text_input("Comunidad", reglamento["comunidad"] if reglamento else "")
    lugar_reunion = st.text_input("Lugar de reunión", reglamento["lugar_reunion"] if reglamento else "")
    frecuencia = st.text_input("Frecuencia de reunión", reglamento["frecuencia_reunion"] if reglamento else "")

    presidenta = st.text_input("Presidenta", reglamento["presidenta"] if reglamento else "")
    secretaria = st.text_input("Secretaria", reglamento["secretaria"] if reglamento else "")
    tesorera = st.text_input("Tesorera", reglamento["tesorera"] if reglamento else "")
    responsable_llave = st.text_input("Responsable de llave", reglamento["responsable_llave"] if reglamento else "")

    multa_ausencia = st.number_input("Multa por ausencia", min_value=0.0,
                                     value=float(reglamento["multa_ausencia"]) if reglamento else 0.0)

    razones_sin_multa = st.text_input("Razones sin multa", reglamento["razones_sin_multa"] if reglamento else "")
    deposito_minimo = st.number_input("Depósito mínimo", min_value=0.0,
                                      value=float(reglamento["deposito_minimo"]) if reglamento else 0.0)
    interes_por_10 = st.number_input("Interés por 10", min_value=0.0,
                                     value=float(reglamento["interes_por_10"]) if reglamento else 0.0)

    max_prestamo = st.number_input("Monto máximo de préstamo", min_value=0.0,
                                   value=float(reglamento["max_prestamo"]) if reglamento else 0.0)

    max_plazo = st.text_input("Plazo máximo", reglamento["max_plazo"] if reglamento else "")

    un_solo_prestamo = st.checkbox("Solo un préstamo activo", value=bool(reglamento["un_solo_prestamo"]) if reglamento else False)
    evaluacion_monto = st.checkbox("Evaluar monto según plazo", value=bool(reglamento["evaluacion_monto_plazo"]) if reglamento else False)

    fecha_formacion = st.date_input("Fecha de formación",
                                    value=reglamento["fecha_formacion"] if reglamento else datetime.now())

    fecha_inicio_ciclo = st.date_input("Fecha de inicio de ciclo",
                                       value=reglamento["fecha_inicio_ciclo"] if reglamento else datetime.now())

    # =================== GUARDAR ===================
    if st.button("Guardar reglamento"):
        datos = (
            id_grupo,
            comunidad,
            fecha_formacion,
            ",".join(dia_reunion),
            hora_reunion.strftime("%H:%M"),
            lugar_reunion,
            frecuencia,
            presidenta,
            secretaria,
            tesorera,
            responsable_llave,
            multa_ausencia,
            razones_sin_multa,
            deposito_minimo,
            interes_por_10,
            max_prestamo,
            max_plazo,
            un_solo_prestamo,
            evaluacion_monto,
            fecha_inicio_ciclo
        )

        if reglamento:
            cursor.execute("""
                UPDATE Reglamento SET 
                comunidad=%s, fecha_formacion=%s, dia_reunion=%s, hora_reunion=%s, lugar_reunion=%s,
                frecuencia_reunion=%s, presidenta=%s, secretaria=%s, tesorera=%s, responsable_llave=%s,
                multa_ausencia=%s, razones_sin_multa=%s, deposito_minimo=%s, interes_por_10=%s,
                max_prestamo=%s, max_plazo=%s, un_solo_prestamo=%s, evaluacion_monto_plazo=%s,
                fecha_inicio_ciclo=%s
                WHERE id_grupo=%s
            """, (*datos[1:], id_grupo))
        else:
            cursor.execute("""
                INSERT INTO Reglamento (
                    id_grupo, comunidad, fecha_formacion, dia_reunion, hora_reunion, lugar_reunion,
                    frecuencia_reunion, presidenta, secretaria, tesorera, responsable_llave,
                    multa_ausencia, razones_sin_multa, deposito_minimo, interes_por_10,
                    max_prestamo, max_plazo, un_solo_prestamo, evaluacion_monto_plazo,
                    fecha_inicio_ciclo
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, datos)

        conn.commit()
        st.success("Reglamento guardado correctamente.")
        st.rerun()

    # =================== PREVIEW ===================
    if reglamento:
        mostrar_reglamento_guardado(reglamento)

        if st.button("Descargar reglamento en PDF"):
            ruta_pdf = generar_pdf(reglamento, nombre_grupo)
            with open(ruta_pdf, "rb") as f:
                st.download_button(
                    label="Descargar PDF",
                    data=f,
                    file_name=f"Reglamento_{nombre_grupo}.pdf",
                    mime="application/pdf"
                )


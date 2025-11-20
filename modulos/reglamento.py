import streamlit as st
import mysql.connector
import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


# ============================
# FUNCIÓN PARA GENERAR PDF EN MEMORIA
# ============================
def generar_pdf(reglamento, nombre_grupo):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"Reglamento interno del grupo {nombre_grupo}")

    c.setFont("Helvetica", 11)

    y = 720
    for campo, valor in reglamento.items():
        if valor is None:
            valor = ""
        texto = f"{campo.replace('_', ' ').capitalize()}: {valor}"
        c.drawString(50, y, texto)
        y -= 18

        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = 750

    c.save()
    buffer.seek(0)
    return buffer


# ============================
# FUNCIÓN PRINCIPAL
# ============================
def mostrar_reglamento():

    # Validación de sesión
    if "usuario" not in st.session_state:
        st.error("Debes iniciar sesión.")
        return

    id_grupo = st.session_state.get("id_grupo", None)
    nombre_grupo = st.session_state.get("nombre_grupo", None)

    if id_grupo is None:
        st.error("Este usuario no pertenece a ningún grupo.")
        return

    st.markdown(
        f"<h2 style='text-align:center;'>📘 Reglamento interno del grupo <b>{nombre_grupo}</b></h2>",
        unsafe_allow_html=True
    )

    # ============================
    # CONEXIÓN A BD
    # ============================
    try:
        conn = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="u1ok2gqomnp9hrku",
            password="VWvN6Pw7wKdfDU9uINZT",
            database="bzn5gsi7ken7lufcglbg"
        )
        cursor = conn.cursor(dictionary=True)
    except Exception as e:
        st.error(f"❌ Error al conectar con MySQL: {e}")
        return

    # Obtener reglamento actual
    cursor.execute("SELECT * FROM Reglamento WHERE id_grupo = %s LIMIT 1", (id_grupo,))
    reglamento = cursor.fetchone()

    def val(campo, defecto=""):
        if reglamento and reglamento.get(campo) not in (None, ""):
            return reglamento[campo]
        return defecto

    def fecha_valida(campo):
        try:
            if reglamento and reglamento.get(campo):
                return reglamento[campo]
        except:
            pass
        return datetime.date.today()

    # ============================
    # FORMULARIO
    # ============================
    with st.form("form_reglamento"):

        st.subheader("📍 Información general")
        comunidad = st.text_input("Comunidad:", val("comunidad"))
        fecha_formacion = st.date_input("Fecha de formación:", fecha_valida("fecha_formacion"))

        st.subheader("📅 Reuniones")
        # Lista desplegable de días
        dias_opciones = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dia_reunion = st.selectbox("Día(s) de reunión:", dias_opciones, index=dias_opciones.index(val("dia_reunion")) if val("dia_reunion") in dias_opciones else 0)

        # Selector de hora
        hora_reunion = st.time_input("Hora de reunión:", datetime.time.fromisoformat(val("hora_reunion")) if val("hora_reunion") else datetime.time(8, 0))

        lugar_reunion = st.text_input("Lugar:", val("lugar_reunion"))
        frecuencia_reunion = st.text_input("Frecuencia:", val("frecuencia_reunion"))

        st.subheader("🏛 Comité")
        presidenta = st.text_input("Presidenta:", val("presidenta"))
        secretaria = st.text_input("Secretaria:", val("secretaria"))
        tesorera = st.text_input("Tesorera:", val("tesorera"))
        responsable_llave = st.text_input("Responsable de llave:", val("responsable_llave"))

        st.subheader("🧾 Asistencia")
        multa_ausencia = st.number_input("Multa por ausencia:", value=float(val("multa_ausencia", 0)))
        razones_sin_multa = st.text_area("Razones sin multa:", val("razones_sin_multa"))
        deposito_minimo = st.number_input("Depósito mínimo:", value=float(val("deposito_minimo", 0)))

        st.subheader("💰 Préstamos")
        interes_por_10 = st.number_input("Interés por cada $10 (%):", value=float(val("interes_por_10", 0)))
        max_prestamo = st.number_input("Monto máximo:", value=float(val("max_prestamo", 0)))
        max_plazo = st.text_input("Plazo máximo:", val("max_plazo"))
        un_solo_prestamo = st.checkbox("Un solo préstamo activo", value=bool(val("un_solo_prestamo", 0)))
        evaluacion_monto_plazo = st.checkbox("Evaluar monto y plazo", value=bool(val("evaluacion_monto_plazo", 0)))

        st.subheader("🔄 Ciclo")
        fecha_inicio_ciclo = st.date_input("Inicio del ciclo:", fecha_valida("fecha_inicio_ciclo"))
        fecha_fin_ciclo = st.date_input("Fin del ciclo:", fecha_valida("fecha_fin_ciclo"))

        st.subheader("⭐ Meta social")
        meta_social = st.text_area("Meta social:", val("meta_social"))

        st.subheader("📌 Otras reglas")
        otras_reglas = st.text_area("Otras reglas:", val("otras_reglas"))

        submitted = st.form_submit_button("💾 Guardar reglamento")

    # ============================
    # GUARDAR EN BD
    # ============================
    if submitted:
        try:
            if reglamento:
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
                    comunidad, fecha_formacion, dia_reunion, hora_reunion.strftime("%H:%M"),
                    lugar_reunion, frecuencia_reunion, presidenta, secretaria,
                    tesorera, responsable_llave, multa_ausencia, razones_sin_multa,
                    deposito_minimo, interes_por_10, max_prestamo, max_plazo,
                    un_solo_prestamo, evaluacion_monto_plazo, fecha_inicio_ciclo,
                    fecha_fin_ciclo, meta_social, otras_reglas, reglamento["id"]
                ))
            else:
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
                    id_grupo, comunidad, fecha_formacion, dia_reunion, hora_reunion.strftime("%H:%M"),
                    lugar_reunion, frecuencia_reunion, presidenta, secretaria, tesorera,
                    responsable_llave, multa_ausencia, razones_sin_multa, deposito_minimo,
                    interes_por_10, max_prestamo, max_plazo, un_solo_prestamo,
                    evaluacion_monto_plazo, fecha_inicio_ciclo, fecha_fin_ciclo, meta_social,
                    otras_reglas
                ))

            conn.commit()
            st.success("Reglamento guardado correctamente 🎉")
            st.rerun()

        except Exception as e:
            st.error(f"Error al guardar: {e}")

    # ============================
    # VISTA PREVIA DEL REGLAMENTO
    # ============================
    st.subheader("📄 Vista previa del reglamento")

    cursor.execute("SELECT * FROM Reglamento WHERE id_grupo = %s LIMIT 1", (id_grupo,))
    reglamento = cursor.fetchone()

    if reglamento:
        st.json(reglamento)

        pdf_buffer = generar_pdf(reglamento, nombre_grupo)

        st.download_button(
            label="📥 Descargar Reglamento en PDF",
            data=pdf_buffer,
            file_name=f"Reglamento_{nombre_grupo}.pdf",
            mime="application/pdf"
        )
    else:
        st.info("No hay reglamento guardado todavía.")

    conn.close()

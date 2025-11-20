import streamlit as st
import mysql.connector
import datetime


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
    # CONEXIÓN A BD
    # ============================
    try:
        conn = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="uiazxdhtd3r8o7uv",
            password="uGjZ9MXWemv7vPsjOdA5",
            database="bzn5gsi7ken7lufcglbg"
        )
        cursor = conn.cursor(dictionary=True)

    except Exception as e:
        st.error(f"❌ Error al conectar con MySQL: {e}")
        return

    # ============================
    # OBTENER REGLAMENTO
    # ============================
    cursor.execute("SELECT * FROM Reglamento WHERE id_grupo = %s LIMIT 1", (id_grupo,))
    reglamento = cursor.fetchone()

    # Función segura para obtener valores
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

        # ========= Días de reunión (multiselect) =========
        dias_lista = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

        dias_guardados = val("dia_reunion").split(",") if val("dia_reunion") else []

        dia_reunion = st.multiselect(
            "Día(s) de reunión:",
            dias_lista,
            default=dias_guardados
        )

        # ========= Hora de reunión =========
        try:
            hora_guardada = datetime.datetime.strptime(val("hora_reunion"), "%H:%M").time()
        except:
            hora_guardada = datetime.datetime.now().time()

        hora_reunion_time = st.time_input("Hora:", value=hora_guardada)
        hora_reunion = hora_reunion_time.strftime("%H:%M")

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
    # GUARDAR
    # ============================
    if submitted:
        try:
            # Convertir lista -> string
            dias_texto = ",".join(dia_reunion)

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
                    comunidad, fecha_formacion, dias_texto, hora_reunion,
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
                    id_grupo, comunidad, fecha_formacion, dias_texto, hora_reunion,
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

    conn.close()

    # ------------------ BOTÓN REGRESAR ------------------
    st.write("")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()
    st.write("---")

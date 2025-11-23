import streamlit as st
import mysql.connector
import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

# ============================================================
# FUNCIÓN PARA OBTENER MIEMBROS DEL GRUPO
# ============================================================
def obtener_miembros_grupo(id_grupo):
    """Obtiene la lista de miembros del grupo desde la base de datos"""
    try:
        conn = mysql.connector.connect(
            host="bzn5gsi7ken7lufcglbg-mysql.services.clever-cloud.com",
            user="uiazxdhtd3r8o7uv",
            password="uGjZ9MXWemv7vPsjOdA5",
            database="bzn5gsi7ken7lufcglbg"
        )
        cursor = conn.cursor()
        
        # CONSULTA AJUSTADA PARA TU ESTRUCTURA
        cursor.execute("""
            SELECT m.nombre 
            FROM Miembros m
            INNER JOIN Grupomiembros gm ON m.id = gm.id_miembro
            WHERE gm.id_grupo = %s 
            ORDER BY m.nombre
        """, (id_grupo,))
        
        miembros = [fila[0] for fila in cursor.fetchall()]
        return miembros
        
    except Exception as e:
        st.error(f"Error al cargar miembros: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# ============================================================
# FUNCIÓN PARA GENERAR PDF
# ============================================================
def generar_pdf(reglamento, nombre_grupo):
    ruta_pdf = "/tmp/reglamento.pdf"  # ruta válida en Streamlit Cloud

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"<b>Reglamento Interno - {nombre_grupo}</b>", styles["Title"]))
    story.append(Paragraph("<br/>", styles["Normal"]))

    # Convertir campos booleanos a "Sí"/"No" para PDF
    def format_val(k, v):
        if k in ("un_solo_prestamo", "evaluacion_monto_plazo"):
            return "Sí" if v else "No"
        return v

    for k, v in reglamento.items():
        if k in ("id", "id_grupo"):  # Excluir campos internos
            continue
        story.append(Paragraph(f"<b>{k.replace('_', ' ').title()}:</b> {format_val(k, v)}", styles["Normal"]))

    doc = SimpleDocTemplate(ruta_pdf, pagesize=letter)
    doc.build(story)

    return ruta_pdf

# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================
def mostrar_reglamento():

    # -------------------------
    # VALIDACIÓN DE SESIÓN
    # -------------------------
    if "usuario" not in st.session_state:
        st.error("Debes iniciar sesión.")
        return

    id_grupo = st.session_state.get("id_grupo")
    nombre_grupo = st.session_state.get("nombre_grupo")

    if id_grupo is None:
        st.error("Este usuario no pertenece a ningún grupo.")
        return

    st.markdown(
        f"<h2 style='text-align:center;'>📘 Reglamento interno del grupo <b>{nombre_grupo}</b></h2>",
        unsafe_allow_html=True
    )

    # -------------------------
    # CONEXIÓN A MYSQL
    # -------------------------
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

    # -------------------------
    # CARGAR REGLAMENTO EXISTENTE
    # -------------------------
    cursor.execute("SELECT * FROM Reglamento WHERE id_grupo = %s LIMIT 1", (id_grupo,))
    reglamento = cursor.fetchone()

    def val(campo, defecto=""):
        if reglamento and reglamento.get(campo) not in (None, ""):
            return reglamento[campo]
        return defecto

    def fecha_valida(campo):
        if reglamento and reglamento.get(campo):
            return reglamento[campo]
        return datetime.date.today()

    # ============================================================
    # FORMULARIO
    # ============================================================
    with st.form("form_reglamento"):

        st.subheader("📍 Información general")
        comunidad = st.text_input("Comunidad:", val("comunidad"))
        fecha_formacion = st.date_input("Fecha de formación:", fecha_valida("fecha_formacion"))

        st.subheader("📅 Reuniones")
        dias_lista = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        dias_guardados = val("dia_reunion").split(",") if val("dia_reunion") else []
        dia_reunion = st.multiselect("Día(s) de reunión:", dias_lista, default=dias_guardados)

        try:
            hora_guardada = datetime.datetime.strptime(val("hora_reunion"), "%H:%M").time()
        except:
            hora_guardada = datetime.datetime.now().time()
        hora_reunion_obj = st.time_input("Hora:", value=hora_guardada)
        hora_reunion = hora_reunion_obj.strftime("%H:%M")

        lugar_reunion = st.text_input("Lugar:", val("lugar_reunion"))
        frecuencia_reunion = st.text_input("Frecuencia:", val("frecuencia_reunion"))

        st.subheader("🏛 Comité")
        
        # OBTENER MIEMBROS DEL GRUPO
        miembros = obtener_miembros_grupo(id_grupo)
        
        if miembros:
            st.info(f"📋 Miembros disponibles: {len(miembros)}")
            
            # Encontrar índices actuales para preseleccionar
            def encontrar_indice(valor_actual):
                if valor_actual and valor_actual in miembros:
                    return miembros.index(valor_actual)
                return 0
            
            presidenta_actual = val("presidenta")
            secretaria_actual = val("secretaria")
            tesorera_actual = val("tesorera")
            responsable_llave_actual = val("responsable_llave")
            
            col1, col2 = st.columns(2)
            
            with col1:
                presidenta = st.selectbox(
                    "Presidenta:",
                    options=miembros,
                    index=encontrar_indice(presidenta_actual),
                    key="presidenta_select"
                )
                
                secretaria = st.selectbox(
                    "Secretaria:",
                    options=miembros,
                    index=encontrar_indice(secretaria_actual),
                    key="secretaria_select"
                )
            
            with col2:
                tesorera = st.selectbox(
                    "Tesorera:",
                    options=miembros,
                    index=encontrar_indice(tesorera_actual),
                    key="tesorera_select"
                )
                
                responsable_llave = st.selectbox(
                    "Responsable de llave:",
                    options=miembros,
                    index=encontrar_indice(responsable_llave_actual),
                    key="responsable_llave_select"
                )
            
            # Validar que no se repitan miembros
            roles_seleccionados = [presidenta, secretaria, tesorera, responsable_llave]
            miembros_repetidos = set([x for x in roles_seleccionados if roles_seleccionados.count(x) > 1])
            
            if miembros_repetidos:
                st.error(f"❌ Error: {', '.join(miembros_repetidos)} está asignado a múltiples roles.")
        
        else:
            st.warning("No hay miembros registrados en el grupo. Use campos de texto temporalmente.")
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

    # ============================================================
    # GUARDAR EN BD
    # ============================================================
    if submitted:
        # Validar miembros repetidos antes de guardar
        if miembros and len(set([presidenta, secretaria, tesorera, responsable_llave])) != 4:
            st.error("❌ No se puede guardar: hay miembros asignados a múltiples roles.")
        else:
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
                        comunidad, fecha_formacion, ",".join(dia_reunion), hora_reunion,
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
                        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (
                        id_grupo, comunidad, fecha_formacion, ",".join(dia_reunion), hora_reunion,
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

    # ============================================================
    # MOSTRAR REGLAMENTO DEBAJO DEL FORMULARIO
    # ============================================================
    st.write("---")
    st.subheader("📄 Vista previa del reglamento")

    cursor.execute("SELECT * FROM Reglamento WHERE id_grupo = %s LIMIT 1", (id_grupo,))
    reglamento = cursor.fetchone()

    if reglamento:

        # -------------------------
        # ESTILOS
        # -------------------------
        st.markdown(
            """
            <style>
                .regla-box {
                    background: #fdfdfd;
                    padding: 20px;
                    border-radius: 12px;
                    border: 1px solid #ddd;
                    margin-bottom: 25px;
                }
                .regla-titulo {
                    font-size: 20px;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }
                .regla-item {
                    margin-bottom: 8px;
                    font-size: 16px;
                }
                .regla-label {
                    font-weight: 600;
                    color: #34495e;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"<div class='regla-box'>"
            f"<div class='regla-titulo'>📘 Reglamento del grupo <b>{nombre_grupo}</b></div>",
            unsafe_allow_html=True
        )

        # -------------------------
        # FUNCIÓN PARA IMPRIMIR BONITO
        # -------------------------
        def mostrar_item(label, valor):
            if valor not in (None, "", "0", "Decimal('0')"):
                if "Decimal" in str(valor):
                    valor = float(str(valor).replace("Decimal('", "").replace("')", ""))
                if isinstance(valor, int) and label in ("Un solo préstamo activo", "Evaluación de monto y plazo"):
                    valor = "Sí" if valor else "No"
                st.markdown(
                    f"<div class='regla-item'><span class='regla-label'>{label}:</span> {valor}</div>",
                    unsafe_allow_html=True
                )

        # ======================
        # SECCIONES
        # ======================
        mostrar_item("Comunidad", reglamento.get("comunidad"))
        mostrar_item("Fecha de formación", reglamento.get("fecha_formacion"))
        mostrar_item("Días de reunión", reglamento.get("dia_reunion"))
        mostrar_item("Hora", reglamento.get("hora_reunion"))
        mostrar_item("Lugar", reglamento.get("lugar_reunion"))
        mostrar_item("Frecuencia", reglamento.get("frecuencia_reunion"))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='regla-titulo'>🏛 Comité</div>", unsafe_allow_html=True)
        mostrar_item("Presidenta", reglamento.get("presidenta"))
        mostrar_item("Secretaria", reglamento.get("secretaria"))
        mostrar_item("Tesorera", reglamento.get("tesorera"))
        mostrar_item("Responsable de llave", reglamento.get("responsable_llave"))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='regla-titulo'>🧾 Asistencia</div>", unsafe_allow_html=True)
        mostrar_item("Multa por ausencia", reglamento.get("multa_ausencia"))
        mostrar_item("Razones sin multa", reglamento.get("razones_sin_multa"))
        mostrar_item("Depósito mínimo", reglamento.get("deposito_minimo"))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='regla-titulo'>💰 Préstamos</div>", unsafe_allow_html=True)
        mostrar_item("Interés por cada $10", reglamento.get("interes_por_10"))
        mostrar_item("Monto máximo", reglamento.get("max_prestamo"))
        mostrar_item("Plazo máximo", reglamento.get("max_plazo"))
        mostrar_item("Un solo préstamo activo", reglamento.get("un_solo_prestamo"))
        mostrar_item("Evaluación de monto y plazo", reglamento.get("evaluacion_monto_plazo"))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='regla-titulo'>🔄 Ciclo</div>", unsafe_allow_html=True)
        mostrar_item("Inicio del ciclo", reglamento.get("fecha_inicio_ciclo"))
        mostrar_item("Fin del ciclo", reglamento.get("fecha_fin_ciclo"))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='regla-titulo'>⭐ Meta social</div>", unsafe_allow_html=True)
        mostrar_item("Meta social", reglamento.get("meta_social"))

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("<div class='regla-titulo'>📌 Otras reglas</div>", unsafe_allow_html=True)
        mostrar_item("Otras reglas", reglamento.get("otras_reglas"))

        st.markdown("</div>", unsafe_allow_html=True)

        # -------------------------
        # DESCARGAR PDF
        # -------------------------
        ruta_pdf = generar_pdf(reglamento, nombre_grupo)
        with open(ruta_pdf, "rb") as f:
            st.download_button(
                label="⬇️ Descargar reglamento en PDF",
                data=f,
                file_name="Reglamento.pdf",
                mime="application/pdf"
            )

        # ============================================================
        # BOTÓN PARA BORRAR EL REGLAMENTO
        # ============================================================
        st.write("---")
        st.subheader("⚠️ Opciones avanzadas")
        if st.button("🗑️ Borrar reglamento"):
            try:
                cursor.execute("DELETE FROM Reglamento WHERE id_grupo = %s", (id_grupo,))
                conn.commit()
                st.success("Reglamento eliminado correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al eliminar: {e}")

    # -------------------------
    # BOTÓN REGRESAR
    # -------------------------
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

    conn.close()

import streamlit as st

def mostrar_menu():
    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        st.stop()

    # 🚨 SOLUCIÓN: Inicializar 'modulos' antes del bloque condicional
    modulos = [] 

    # ---------------------------------------
    # CONFIGURAR MÓDULOS Y COLORES
    # ---------------------------------------
    # Estructura de módulos: (Icono, Texto, Modulo Key, Color_Inicio, Color_Fin)
    modulos_base = [
        ("📁", "Gestión de Proyectos", "proyectos", "#AEDFF7", "#C9B2D9"),
        ("👥", "Gestión de Usuarios", "registrar_miembros", "#F7DCC4", "#F4CDB3"),
        ("🧾", "Inspecciones y Evaluaciones", "inspecciones", "#BEE4DD", "#A6D9D0"),
        ("📄", "Gestión Documental", "documentos", "#C9B2D9", "#F7DCC4"),
        ("📊", "Reportes", "reportes", "#A6D9D0", "#DCC8E3"),
        ("⚙️", "Configuración", "configuracion", "#F4CDB3", "#BEE4DD"),
    ]
    
    # Lógica para asignar módulos según el rol
    if rol == "institucional":
        modulos = modulos_base
    elif rol == "promotor":
        modulos = [m for m in modulos_base if m[2] in ["proyectos", "inspecciones"]]
    elif rol == "miembro":
        modulos = [m for m in modulos_base if m[2] in ["documentos"]]
    
    # ---------------------------------------
    # (El resto del código Streamlit, CSS y la lógica de los botones sigue aquí)
    # ---------------------------------------
    
    # ... (código de st.markdown para CSS) ...

    # ---------------------------------------
    # GRID DE BOTONES (donde ocurría el error)
    # ---------------------------------------
    if not modulos: # Opcional: Manejar si no hay módulos definidos para ese rol
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados en este momento.")
        return

    cols = st.columns(3)

    for i, (icono, texto, modulo, color1, color2) in enumerate(modulos):
        # ... (código de inyección de HTML y CSS por módulo) ...
        # ... (código de st.button) ...
        pass
        
    # ... (resto de la función, incluyendo el botón Cerrar Sesión) ...

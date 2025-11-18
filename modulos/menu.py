import streamlit as st

def mostrar_menu():
    # Establecer un rol de prueba si no existe (para que el código sea ejecutable fuera de un login)
    if "rol" not in st.session_state:
        st.session_state["rol"] = "institucional" # Ejemplo de rol

    rol = st.session_state.get("rol", None)

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    #       🎨 CSS - Botones con animación + colores
    # -----------------------------------------------------
    st.markdown("""
    <style>
    
    /* 🔴 CORRECCIÓN CLAVE PARA EL TAMAÑO UNIFORME: 
       Forzamos al contenedor del botón a ocupar todo el espacio de la columna.
       Esto anula cualquier cálculo de ancho basado en el texto del botón. 
    */
    div[data-testid="stButton"] {
        width: 100% !important; 
    }
    
    /* ESTILO GENERAL DE BOTONES DEL MENÚ */
    div.stButton > button {
        color: #4C3A60 !important;
        border-radius: 12px !important;
        padding: 20px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        
        /* LA CLAVE PARA EL MISMO TAMAÑO ES ESTABLECER AMBOS: */
        width: 100% !important; /* Ocupa todo el ancho del contenedor forzado arriba */
        height: 110px !important; /* Altura fija para todos */
        
        border: none !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18) !important;
        
        /* Alineación y envoltura de texto */
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        white-space: normal !important; 
        word-break: break-word;
    }

    /* ANIMACIÓN */
    div.stButton > button:hover {
        transform: scale(1.07) !important;
        box-shadow: 0 10px 22px rgba(0, 0, 0, 0.30) !important;
    }

    /* 🎨 COLORES POR MÓDULO - Usamos los KEYs de los botones como IDs en el CSS */
    
    /* Gestión de Proyectos */
    div[data-testid="stButton"] button[key="btn_proyectos"] { 
        background-color: #F4B400 !important; /* Amarillo */ 
    }
    /* Gestión de Usuarios */
    div[data-testid="stButton"] button[key="btn_registrar_miembros"] { 
        background-color: #8E24AA !important; /* Morado */
    }
    /* Inspecciones y Evaluaciones */
    div[data-testid="stButton"] button[key="btn_inspecciones"] { 
        background-color: #E53935 !important; /* Rojo */
    }
    /* Gestión Documental */
    div[data-testid="stButton"] button[key="btn_documentos"] { 
        background-color: #1E88E5 !important; /* Azul */
    }
    /* Reportes */
    div[data-testid="stButton"] button[key="btn_reportes"] { 
        background-color: #43A047 !important; /* Verde */
    }
    /* Configuración */
    div[data-testid="stButton"] button[key="btn_configuracion"] { 
        background-color: #6D4C41 !important; /* Café */
    }
    
    /* BOTÓN CERRAR SESIÓN */
    div[data-testid="stButton"] button[key="logout"] {
        background-color: #424242 !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 12px 22px !important;
        font-size: 16px !important;
        /* Establecer un ancho específico para que no sea 100% */
        width: 200px !important; 
        height: auto !important; /* Permitir que la altura se ajuste */
        transition: transform 0.2s ease !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2) !important;
    }
    div[data-testid="stButton"] button[key="logout"]:hover {
        transform: scale(1.05) !important;
        background-color: #000000 !important;
        box-shadow: 0 5px 10px rgba(0, 0, 0, 0.3) !important;
    }

    </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------
    #                       TÍTULO
    # -----------------------------------------------------
    st.markdown("<h1 style='text-align:center;'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)

    # -----------------------------------------------------
    #                   MÓDULOS BASE
    # -----------------------------------------------------
    modulos_base = [
        ("📁 Gestión de Proyectos", "proyectos"),
        ("👥 Gestión de Usuarios", "registrar_miembros"),
        ("📝 Inspecciones y Evaluaciones", "inspecciones"),
        ("📄 Gestión Documental", "documentos"),
        ("📊 Reportes", "reportes"),
        ("⚙️ Configuración", "configuracion"),
    ]

    # -----------------------------------------------------
    #                   FILTRO POR ROL
    # -----------------------------------------------------
    if rol == "institucional":
        modulos = modulos_base

    elif rol == "promotor":
        modulos = [
            m for m in modulos_base if m[1] in ["proyectos", "inspecciones"]
        ]

    elif rol == "miembro":
        modulos = [
            m for m in modulos_base if m[1] == "documentos"
        ]

    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    #                   GRID DE BOTONES
    # -----------------------------------------------------
    # Usamos st.columns(3) para una distribución estándar.
    cols = st.columns(3)

    for i, (texto, modulo) in enumerate(modulos):
        with cols[i % 3]:
            # El botón ahora usa el 'modulo' para su key.
            if st.button(texto, key=f"btn_{modulo}"):
                st.session_state.page = modulo
                st.rerun()

    # -----------------------------------------------------
    #               BOTÓN CERRAR SESIÓN
    # -----------------------------------------------------
    st.write("---")
    
    # Mantenemos las columnas explícitas para centrar el botón de cerrar sesión
    col_center, col_btn, col_end = st.columns([1, 0.5, 1])

    with col_btn:
        # El CSS de arriba lo selecciona por el key="logout"
        if st.button("🔒 Cerrar sesión", key="logout"):
            st.session_state.clear()
            st.rerun()

# Llama a la función principal para que el menú se muestre
if __name__ == "__main__":
    mostrar_menu()

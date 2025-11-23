import streamlit as st 

def mostrar_menu():
    rol = st.session_state.get("rol", None)
    usuario = st.session_state.get("usuario", "").lower()

    if not rol:
        st.error("❌ No se detectó un rol en la sesión. Inicie sesión nuevamente.")
        return

    # -----------------------------------------------------
    #      🎨 CSS - Diseño Profesional y Moderno
    # -----------------------------------------------------
    st.markdown("""
    <style>
    /* Reset y configuración general */
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* Títulos y textos */
    .custom-title {
        text-align: center;
        color: #2C3E50;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .user-info {
        text-align: center;
        color: #5D6D7E;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    .role-badge {
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        border-radius: 25px;
        display: inline-block;
        margin: 0.5rem auto 2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Contenedor principal de botones */
    .buttons-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
        padding: 0 1rem;
    }
    
    /* Botones de módulos - Diseño profesional */
    .module-button {
        width: 100% !important;
        height: 100px !important;
        border: none !important;
        border-radius: 16px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: white !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        padding-left: 1.5rem !important;
    }
    
    .module-button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s ease;
    }
    
    .module-button:hover::before {
        left: 100%;
    }
    
    .module-button:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 30px rgba(0,0,0,0.25) !important;
    }
    
    .module-button:active {
        transform: translateY(-2px) !important;
    }
    
    /* Iconos en botones */
    .button-icon {
        font-size: 1.8rem !important;
        margin-right: 1rem !important;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
    }
    
    /* Colores específicos para cada módulo */
    button[key='btn_credenciales'] {
        background: linear-gradient(135deg, #FF9A9E 0%, #FAD0C4 100%) !important;
        color: #2C3E50 !important;
    }
    
    button[key='btn_grupos'] {
        background: linear-gradient(135deg, #A8E6CF 0%, #3EDBF0 100%) !important;
        color: #2C3E50 !important;
    }
    
    button[key='btn_reportes'] {
        background: linear-gradient(135deg, #FFD3A5 0%, #FD6585 100%) !important;
        color: #2C3E50 !important;
    }
    
    button[key='btn_GAPC'] {
        background: linear-gradient(135deg, #6A11CB 0%, #2575FC 100%) !important;
        color: white !important;
    }
    
    /* Botón de cerrar sesión */
    .logout-container {
        display: flex;
        justify-content: center;
        margin: 3rem 0 1rem 0;
        padding: 1rem;
    }
    
    button[key='logout'] {
        width: 200px !important;
        height: 60px !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2) !important;
    }
    
    button[key='logout']:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    /* Separador */
    .separator {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .buttons-grid {
            grid-template-columns: 1fr;
            gap: 1rem;
        }
        
        .module-button {
            height: 90px !important;
            font-size: 1rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

    # -----------------------------------------------------
    #                    ENCABEZADO
    # -----------------------------------------------------
    st.markdown("<h1 class='custom-title'>Menú Principal – GAPC</h1>", unsafe_allow_html=True)
    
    # Información del usuario
    st.markdown(
        f"<div class='user-info'>Usuario: <strong>{st.session_state['usuario']}</strong></div>", 
        unsafe_allow_html=True
    )

    # Badge del rol con colores específicos
    rol_l = rol.lower()
    role_colors = {
        "dark": "background: linear-gradient(135deg, #FF6B6B, #FFE66D); color: #2C3E50;",
        "promotor": "background: linear-gradient(135deg, #4ECDC4, #44A08D); color: white;",
        "institucional": "background: linear-gradient(135deg, #667eea, #764ba2); color: white;",
        "miembro": "background: linear-gradient(135deg, #FD746C, #FF9068); color: white;"
    }
    
    role_style = role_colors.get(rol_l, "background: linear-gradient(135deg, #95a5a6, #7f8c8d); color: white;")
    st.markdown(
        f"<div class='role-badge' style='{role_style}'>{rol.capitalize()}</div>", 
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    #                   MÓDULOS BASE
    # -----------------------------------------------------
    modulos_base = [
        ("📁 Credenciales", "credenciales"),
        ("👥 Gestión de Miembros", "registrar_miembros"),
        ("📝 Grupos", "grupos"),
        ("📜 Reglamento", "reglamento"),
        ("📊 Reportes", "reportes"),
        ("💸 Multas", "multas"),
        ("📋 Asistencia", "asistencia"),
        ("🏛️ GAPC", "GAPC"),
        ("💼 Préstamos", "prestamos"),
        ("💰 Caja", "caja"),
        ("💾 Ahorro", "ahorro_final"),
        ("📌 Reuniones", "reuniones"),
    ]

    # -----------------------------------------------------
    #          FILTRO POR ROL
    # -----------------------------------------------------
    if usuario == "dark":
        modulos = modulos_base
    elif rol_l == "institucional":
        modulos = [m for m in modulos_base if m[1] not in ["caja","multas","prestamos","reglamento","asistencia","registrar_miembros","reuniones","ahorro_final"]]
    elif rol_l == "promotor":
        modulos = [m for m in modulos_base if m[1] in ["credenciales", "grupos"]]
    elif rol_l == "miembro":
        modulos = [m for m in modulos_base if m[1] in ["reglamento", "caja", "multas", "prestamos", "ahorro_final", "reuniones","ahorro_final","registrar_miembros"]]
    else:
        st.warning(f"⚠️ El rol '{rol}' no tiene módulos asignados.")
        return

    # -----------------------------------------------------
    #               GRID DE BOTONES MODERNO
    # -----------------------------------------------------
    st.markdown("<div class='buttons-grid'>", unsafe_allow_html=True)
    
    # Crear columnas responsivas
    cols = st.columns(3)
    
    for i, (texto, modulo) in enumerate(modulos):
        with cols[i % 3]:
            if st.button(
                texto,
                key=f"btn_{modulo}",
                use_container_width=True
            ):
                st.session_state.page = modulo
                st.rerun()
                return
    
    st.markdown("</div>", unsafe_allow_html=True)

    # -----------------------------------------------------
    #               SEPARADOR Y BOTÓN LOGOUT
    # -----------------------------------------------------
    st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='logout-container'>", unsafe_allow_html=True)
    if st.button("🚪 Cerrar sesión", key="logout", use_container_width=False):
        st.session_state.clear()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Ejecutar la función
if __name__ == "__main__":
    mostrar_menu()

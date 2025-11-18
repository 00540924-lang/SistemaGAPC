import streamlit as st
from streamlit_extras.stylable_container import stylable_container

# LISTA DE OPCIONES DEL MENÚ (puedes editar lo que necesites)
opciones_menu = [
    {"id": "usuarios", "titulo": "Gestión de Usuarios", "icono": "👤"},
    {"id": "inventario", "titulo": "Inventario", "icono": "📦"},
    {"id": "ventas", "titulo": "Ventas", "icono": "💲"},
    {"id": "reportes", "titulo": "Reportes", "icono": "📊"},
    {"id": "config", "titulo": "Configuración", "icono": "⚙️"},
]


def mostrar_menu():
    st.title("Panel Principal")

    st.write("### Selecciona una opción")

    cols = st.columns(3)

    for index, item in enumerate(opciones_menu):
        col = cols[index % 3]

        with col:
            # CONTENEDOR ESTILIZADO COMO TARJETA
            with stylable_container(
                key=f"card_{item['id']}",
                css_styles="""
                    {
                        background: #ffffff;
                        padding: 20px;
                        border-radius: 15px;
                        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        transition: all 0.2s ease-in-out;
                        cursor: pointer;
                        text-align: center;
                    }
                    .styled-container:hover {
                        transform: scale(1.03);
                        box-shadow: 0 6px 16px rgba(0,0,0,0.25);
                    }
                """
            ):
                st.markdown(
                    f"""
                    <div style="font-size: 50px; margin-bottom: 10px;">
                        {item['icono']}
                    </div>
                    <b style="font-size: 18px;">{item['titulo']}</b>
                    """,
                    unsafe_allow_html=True
                )

                # BOTÓN INVISIBLE
                clicked = st.button(
                    "Abrir",
                    key=f"btn_{item['id']}",
                )

                # Al hacer clic, actualizamos la sesión
                if clicked:
                    st.session_state["modulo_actual"] = item["id"]
                    st.rerun()

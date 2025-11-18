import mysql.connector
import streamlit as st

def registrar_grupo():
    st.header("Registrar Grupo")

    nombre = st.text_input("Nombre del Grupo")
    descripcion = st.text_area("Descripción del Grupo")

    # Obtener lista de miembros
    conn = mysql.connector.connect(...)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_miembro, nombre FROM Miembros")
    lista_miembros = cursor.fetchall()

    miembros_seleccionados = st.multiselect(
        "Miembros del grupo",
        options=[m["id_miembro"] for m in lista_miembros],
        format_func=lambda x: next(m["nombre"] for m in lista_miembros if m["id_miembro"] == x)
    )

    if st.button("Guardar"):
        cursor.execute(
            "INSERT INTO Grupos (nombre_grupo, descripcion) VALUES (%s, %s)",
            (nombre, descripcion)
        )
        id_grupo = cursor.lastrowid

        # Insertar miembros seleccionados
        for id_miembro in miembros_seleccionados:
            cursor.execute(
                "INSERT INTO GrupoMiembros (id_grupo, id_miembro) VALUES (%s, %s)",
                (id_grupo, id_miembro)
            )

        conn.commit()
        st.success("Grupo registrado correctamente")

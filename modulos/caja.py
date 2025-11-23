import streamlit as st 
import mysql.connector
from datetime import date, datetime, timedelta
from modulos.config.conexion import obtener_conexion
import pandas as pd
import matplotlib.pyplot as plt

def obtener_totales_por_rango(id_grupo, fecha_inicio, fecha_fin):
    """
    Obtiene los totales acumulados de todos los campos de caja para un rango de fechas
    """
    conn = obtener_conexion()
    if not conn:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(multas), 0) as total_multas,
                COALESCE(SUM(ahorros), 0) as total_ahorros,
                COALESCE(SUM(otras_actividades), 0) as total_actividades,
                COALESCE(SUM(pago_prestamos), 0) as total_pago_prestamos,
                COALESCE(SUM(otros_ingresos), 0) as total_otros_ingresos,
                COALESCE(SUM(total_entrada), 0) as total_entrada,
                COALESCE(SUM(retiro_ahorros), 0) as total_retiros,
                COALESCE(SUM(desembolso), 0) as total_desembolso,
                COALESCE(SUM(gastos_grupo), 0) as total_gastos_grupo,
                COALESCE(SUM(total_salida), 0) as total_salida,
                COALESCE(SUM(saldo_cierre), 0) as total_saldo_cierre,
                COUNT(*) as total_registros
            FROM Caja 
            WHERE id_grupo = %s AND fecha BETWEEN %s AND %s
        """, (id_grupo, fecha_inicio, fecha_fin))
        
        resultado = cursor.fetchone()
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        return resultado
            
    except Exception as e:
        st.error(f"Error al obtener totales por rango: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_historial_caja(id_grupo, fecha_inicio=None, fecha_fin=None):
    """Obtiene el historial de caja con filtros opcionales"""
    conn = obtener_conexion()
    if not conn:
        return []
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        query = """
            SELECT fecha, multas, ahorros, otras_actividades, pago_prestamos, 
                   otros_ingresos, total_entrada, retiro_ahorros, desembolso, 
                   gastos_grupo, total_salida, saldo_cierre 
            FROM Caja WHERE id_grupo = %s
        """
        params = [id_grupo]

        if fecha_inicio and fecha_fin:
            query += " AND fecha BETWEEN %s AND %s"
            params.extend([fecha_inicio, fecha_fin])
        elif fecha_inicio:
            query += " AND fecha >= %s"
            params.append(fecha_inicio)
        elif fecha_fin:
            query += " AND fecha <= %s"
            params.append(fecha_fin)

        query += " ORDER BY fecha DESC"
        cursor.execute(query, tuple(params))
        registros = cursor.fetchall()
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        return registros
            
    except Exception as e:
        st.error(f"Error al obtener historial: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def mostrar_caja(id_grupo):
    """
    Módulo de caja - Solo visualización de totales por rango de fechas
    Recibe id_grupo desde app.py (obligatorio para miembros).
    """

    # ===============================
    # 0. Verificar acceso
    # ===============================
    rol = st.session_state.get("rol", "").lower()
    usuario = st.session_state.get("usuario", "").lower()

    if rol not in ["miembro", "institucional"] and usuario != "dark":
        st.error("❌ No tiene permisos para acceder a este módulo.")
        return

    if rol == "miembro" and not id_grupo:
        st.error("❌ No tiene un grupo asignado. Contacte al administrador.")
        return

    st.title("💰 Movimientos de Caja")

    # ===============================
    # 1. FILTRO POR RANGO DE FECHAS PARA TOTALES
    # ===============================
    st.subheader("📊 Totales por Rango de Fechas")
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        fecha_inicio_totales = st.date_input(
            "Fecha inicio", 
            date.today() - timedelta(days=30),
            key="fecha_inicio_totales"
        )
    
    with col2:
        fecha_fin_totales = st.date_input(
            "Fecha fin", 
            date.today(),
            key="fecha_fin_totales"
        )
    
    with col3:
        st.write("")  # Espacio vacío para alineación
        if st.button("🔄 Calcular Totales", use_container_width=True):
            st.session_state.calcular_totales = True

    # Calcular y mostrar totales si se solicita
    if st.session_state.get("calcular_totales", False):
        if fecha_inicio_totales > fecha_fin_totales:
            st.error("❌ La fecha de inicio no puede ser mayor que la fecha fin")
        else:
            totales = obtener_totales_por_rango(id_grupo, fecha_inicio_totales, fecha_fin_totales)
            
            if totales and totales['total_registros'] > 0:
                st.success(f"📈 Totales del período: {fecha_inicio_totales} al {fecha_fin_totales}")
                
                # Crear dos columnas para mostrar los totales
                col_entrada, col_salida = st.columns(2)
                
                with col_entrada:
                    st.markdown("### 🟩 Dinero que Entró")
                    st.metric("Multas", f"${totales['total_multas']:,.2f}")
                    st.metric("Ahorros", f"${totales['total_ahorros']:,.2f}")
                    st.metric("Otras actividades", f"${totales['total_actividades']:,.2f}")
                    st.metric("Pago de préstamos", f"${totales['total_pago_prestamos']:,.2f}")
                    st.metric("Otros ingresos", f"${totales['total_otros_ingresos']:,.2f}")
                    st.metric("**TOTAL ENTRADA**", f"${totales['total_entrada']:,.2f}", 
                             delta=f"{totales['total_entrada']:,.2f}")
                
                with col_salida:
                    st.markdown("### 🟥 Dinero que Salió")
                    st.metric("Retiros de ahorros", f"${totales['total_retiros']:,.2f}")
                    st.metric("Desembolso de préstamos", f"${totales['total_desembolso']:,.2f}")
                    st.metric("Otros gastos del grupo", f"${totales['total_gastos_grupo']:,.2f}")
                    st.metric("**TOTAL SALIDA**", f"${totales['total_salida']:,.2f}", 
                             delta=f"-{totales['total_salida']:,.2f}")
                
                # Saldo neto
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    saldo_neto = totales['total_entrada'] - totales['total_salida']
                    st.metric(
                        "**SALDO NETO DEL PERÍODO**", 
                        f"${saldo_neto:,.2f}",
                        delta=f"{saldo_neto:,.2f}" if saldo_neto >= 0 else f"{saldo_neto:,.2f}",
                        delta_color="normal" if saldo_neto >= 0 else "inverse"
                    )
                
                st.info(f"📋 Período analizado: {fecha_inicio_totales} al {fecha_fin_totales} - {totales['total_registros']} registros encontrados")
            else:
                st.warning(f"ℹ️ No se encontraron registros para el período: {fecha_inicio_totales} al {fecha_fin_totales}")

    st.write("---")

    # ===============================
    # 2. HISTORIAL DETALLADO CON GRÁFICO
    # ===============================
    st.subheader("📋 Historial Detallado")
    st.info("Filtre por fecha o deje vacío para ver todos los registros.")

    col1, col2, col3 = st.columns([1,1,1])
    fecha_inicio = col1.date_input("📅 Fecha inicio (opcional)", key="filtro_inicio")
    fecha_fin = col2.date_input("📅 Fecha fin (opcional)", key="filtro_fin")

    if col3.button("🧹 Limpiar filtros", key="limpiar_historial"):
        st.session_state["limpiar_filtros"] = True

    if st.session_state.get("limpiar_filtros", False):
        fecha_inicio = None
        fecha_fin = None
        st.session_state["limpiar_filtros"] = False

    # Obtener historial
    registros = obtener_historial_caja(id_grupo, fecha_inicio, fecha_fin)

    if registros:
        # Mostrar tabla con todos los datos
        st.markdown("### 📊 Tabla de Movimientos")
        df_detalle = pd.DataFrame(registros)
        
        # Formatear columnas monetarias
        columnas_monetarias = ['multas', 'ahorros', 'otras_actividades', 'pago_prestamos', 
                              'otros_ingresos', 'total_entrada', 'retiro_ahorros', 
                              'desembolso', 'gastos_grupo', 'total_salida', 'saldo_cierre']
        
        for col in columnas_monetarias:
            if col in df_detalle.columns:
                df_detalle[col] = df_detalle[col].apply(lambda x: f"${x:,.2f}" if pd.notnull(x) else "$0.00")
        
        st.dataframe(df_detalle, use_container_width=True)

        # Gráfico de entradas vs salidas
        st.markdown("### 📈 Gráfico de Entradas vs Salidas")
        df_grafico = pd.DataFrame(registros)
        df_grafico['fecha'] = pd.to_datetime(df_grafico['fecha'])
        df_grafico = df_grafico.sort_values('fecha').reset_index(drop=True)

        df_grafico['total_entrada'] = df_grafico['total_entrada'].fillna(0).astype(float)
        df_grafico['total_salida'] = df_grafico['total_salida'].fillna(0).astype(float)

        fig, ax = plt.subplots(figsize=(10, 5))
        width = 0.35
        x = range(len(df_grafico))

        ax.bar([i - width/2 for i in x], df_grafico['total_entrada'], width=width, color='#4CAF50', label='Entradas')
        ax.bar([i + width/2 for i in x], df_grafico['total_salida'], width=width, color='#F44336', label='Salidas')

        max_entrada = df_grafico['total_entrada'].max()
        max_salida = df_grafico['total_salida'].max()

        for i, row in df_grafico.iterrows():
            entrada_val = float(row['total_entrada'])
            salida_val = float(row['total_salida'])
            ax.text(i - width/2, entrada_val + max_entrada*0.01,
                    f"{entrada_val:.2f}", ha='center', va='bottom', fontsize=8, color='#2E7D32')
            ax.text(i + width/2, salida_val + max_salida*0.01,
                    f"{salida_val:.2f}", ha='center', va='bottom', fontsize=8, color='#B71C1C')

        ax.set_xlabel("Fecha", fontsize=12)
        ax.set_ylabel("Monto", fontsize=12)
        ax.set_title("Historial de Caja: Entradas y Salidas", fontsize=14, weight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in df_grafico['fecha']], rotation=45, ha='right', fontsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.6)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend()

        saldo_final = df_grafico['total_entrada'].sum() - df_grafico['total_salida'].sum()
        st.pyplot(fig)
        
        # Resumen del período filtrado
        st.markdown("### 💰 Resumen del Período")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Entradas", f"${df_grafico['total_entrada'].sum():,.2f}")
        with col2:
            st.metric("Total Salidas", f"${df_grafico['total_salida'].sum():,.2f}")
        with col3:
            st.metric("Saldo Neto", f"${saldo_final:,.2f}")
            
    else:
        st.info("No hay registros para mostrar.")

    # ===============================
    # 3. Botón regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

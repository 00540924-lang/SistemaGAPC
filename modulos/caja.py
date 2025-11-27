import streamlit as st 
import mysql.connector
from datetime import date, datetime, timedelta
from modulos.config.conexion import obtener_conexion
import pandas as pd
import matplotlib.pyplot as plt

def obtener_multas_pagadas_rango(id_grupo, fecha_inicio, fecha_fin):
    """Obtiene las multas pagadas directamente de la tabla Multas"""
    conn = obtener_conexion()
    if not conn:
        return 0.0
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute("""
            SELECT COALESCE(SUM(MT.monto_a_pagar), 0) AS total_multas
            FROM Multas MT
            JOIN Miembros M ON MT.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s
            AND MT.fecha BETWEEN %s AND %s
            AND MT.pagada = 1
        """, (id_grupo, fecha_inicio, fecha_fin))

        resultado_multa = cursor.fetchone()
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        return float(resultado_multa["total_multas"]) if resultado_multa else 0.0
        
    except Exception as e:
        st.error(f"Error al obtener multas pagadas: {e}")
        return 0.0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_ahorros_rango(id_grupo, fecha_inicio, fecha_fin):
    """Obtiene los datos de ahorro directamente del módulo de ahorro"""
    conn = obtener_conexion()
    if not conn:
        return 0.0, 0.0, 0.0
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        cursor.execute("""
            SELECT 
                COALESCE(SUM(ahorros), 0) as total_ahorros,
                COALESCE(SUM(actividades), 0) as total_actividades,
                COALESCE(SUM(retiros), 0) as total_retiros
            FROM ahorro_final 
            WHERE id_grupo = %s AND fecha_registro BETWEEN %s AND %s
        """, (id_grupo, fecha_inicio, fecha_fin))
        
        resultado = cursor.fetchone()
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        if resultado:
            return (
                float(resultado['total_ahorros']),
                float(resultado['total_actividades']),
                float(resultado['total_retiros'])
            )
        return 0.0, 0.0, 0.0
        
    except Exception as e:
        st.error(f"Error al obtener datos de ahorro: {e}")
        return 0.0, 0.0, 0.0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def obtener_prestamos_rango(id_grupo, fecha_inicio, fecha_fin):
    """Obtiene los datos de préstamos directamente de las tablas de préstamos"""
    conn = obtener_conexion()
    if not conn:
        return 0.0, 0.0
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # 1. Obtener pagos de préstamos
        cursor.execute("""
            SELECT COALESCE(SUM(PP.capital + PP.interes), 0) as total_pagos
            FROM prestamo_pagos PP
            JOIN prestamos P ON PP.id_prestamo = P.id_prestamo
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND PP.fecha BETWEEN %s AND %s
            AND PP.estado = 'pagado'
        """, (id_grupo, fecha_inicio, fecha_fin))
        
        resultado_pagos = cursor.fetchone()
        total_pagos = float(resultado_pagos['total_pagos']) if resultado_pagos else 0.0
        
        # 2. Obtener desembolsos de préstamos - SIN FILTRO DE ESTADO
        cursor.execute("""
            SELECT COALESCE(SUM(P.monto), 0) as total_desembolsos
            FROM prestamos P
            JOIN Miembros M ON P.id_miembro = M.id_miembro
            JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
            WHERE GM.id_grupo = %s 
            AND P.fecha_desembolso BETWEEN %s AND %s
        """, (id_grupo, fecha_inicio, fecha_fin))
        
        resultado_desembolsos = cursor.fetchone()
        total_desembolsos = float(resultado_desembolsos['total_desembolsos']) if resultado_desembolsos else 0.0
        
        return total_pagos, total_desembolsos
        
    except Exception as e:
        st.error(f"Error al obtener datos de préstamos: {e}")
        return 0.0, 0.0
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
def obtener_totales_por_rango(id_grupo, fecha_inicio, fecha_fin):
    """
    Obtiene los totales acumulados consultando directamente las tablas origen
    """
    # Obtener datos de cada módulo
    total_multas = obtener_multas_pagadas_rango(id_grupo, fecha_inicio, fecha_fin)
    total_ahorros, total_actividades, total_retiros = obtener_ahorros_rango(id_grupo, fecha_inicio, fecha_fin)
    total_pago_prestamos, total_desembolso = obtener_prestamos_rango(id_grupo, fecha_inicio, fecha_fin)
    
    # Valores por defecto para campos que no tenemos en otros módulos
    total_otros_ingresos = 0.0
    total_gastos_grupo = 0.0
    
    # Calcular totales
    total_entrada = total_multas + total_ahorros + total_actividades + total_pago_prestamos + total_otros_ingresos
    total_salida = total_retiros + total_desembolso + total_gastos_grupo
    total_saldo_cierre = total_entrada - total_salida
    
    # Contar registros (podemos estimar basado en si hay datos)
    total_registros = 1 if any([total_multas, total_ahorros, total_actividades, total_retiros, 
                               total_pago_prestamos, total_desembolso]) else 0
    
    return {
        'total_multas': total_multas,
        'total_ahorros': total_ahorros,
        'total_actividades': total_actividades,
        'total_pago_prestamos': total_pago_prestamos,
        'total_otros_ingresos': total_otros_ingresos,
        'total_entrada': total_entrada,
        'total_retiros': total_retiros,
        'total_desembolso': total_desembolso,
        'total_gastos_grupo': total_gastos_grupo,
        'total_salida': total_salida,
        'total_saldo_cierre': total_saldo_cierre,
        'total_registros': total_registros
    }

def obtener_datos_grafico(id_grupo, fecha_inicio=None, fecha_fin=None):
    """Obtiene los datos para el gráfico consultando directamente las tablas origen"""
    conn = obtener_conexion()
    if not conn:
        return []
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # Consulta para obtener datos diarios de todos los módulos
        query = """
            SELECT 
                fecha,
                COALESCE((
                    SELECT SUM(MT.monto_a_pagar)
                    FROM Multas MT
                    JOIN Miembros M ON MT.id_miembro = M.id_miembro
                    JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
                    WHERE GM.id_grupo = %s
                    AND MT.fecha = dias.fecha
                    AND MT.pagada = 1
                ), 0) as multas,
                
                COALESCE((
                    SELECT SUM(ahorros) 
                    FROM ahorro_final 
                    WHERE id_grupo = %s AND fecha_registro = dias.fecha
                ), 0) as ahorros,
                
                COALESCE((
                    SELECT SUM(actividades) 
                    FROM ahorro_final 
                    WHERE id_grupo = %s AND fecha_registro = dias.fecha
                ), 0) as actividades,
                
                COALESCE((
                    SELECT SUM(retiros) 
                    FROM ahorro_final 
                    WHERE id_grupo = %s AND fecha_registro = dias.fecha
                ), 0) as retiros,
                
                COALESCE((
                    SELECT SUM(PP.capital + PP.interes)
                    FROM prestamo_pagos PP
                    JOIN prestamos P ON PP.id_prestamo = P.id_prestamo
                    JOIN Miembros M ON P.id_miembro = M.id_miembro
                    JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
                    WHERE GM.id_grupo = %s 
                    AND PP.fecha = dias.fecha
                    AND PP.estado = 'pagado'
                ), 0) as pago_prestamos,
                
                COALESCE((
                    SELECT SUM(P.monto)
                    FROM prestamos P
                    JOIN Miembros M ON P.id_miembro = M.id_miembro
                    JOIN Grupomiembros GM ON GM.id_miembro = M.id_miembro
                    WHERE GM.id_grupo = %s 
                    AND P.fecha_desembolso = dias.fecha
                    -- REMOVER FILTRO DE ESTADO: AND P.estado IN ('activo', 'pendiente')
                ), 0) as desembolso
                
            FROM (
                SELECT DISTINCT fecha
                FROM (
                    SELECT fecha FROM Multas
                    UNION 
                    SELECT fecha_registro as fecha FROM ahorro_final
                    UNION 
                    SELECT fecha as fecha FROM prestamo_pagos
                    UNION 
                    SELECT fecha_desembolso as fecha FROM prestamos
                ) todas_fechas
                WHERE fecha BETWEEN %s AND %s
            ) dias
            ORDER BY fecha ASC
        """
        
        params = [id_grupo, id_grupo, id_grupo, id_grupo, id_grupo, id_grupo, fecha_inicio, fecha_fin]
        cursor.execute(query, tuple(params))
        registros = cursor.fetchall()
        
        # Asegurarse de que no hay más resultados
        cursor.fetchall()
        
        # Procesar los registros para calcular total_entrada y total_salida
        for registro in registros:
            registro['total_entrada'] = (
                registro['multas'] + 
                registro['ahorros'] + 
                registro['actividades'] + 
                registro['pago_prestamos']
            )
            registro['total_salida'] = (
                registro['retiros'] + 
                registro['desembolso']
            )
        
        return registros
            
    except Exception as e:
        st.error(f"Error al obtener datos para gráfico: {e}")
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
                
                st.info(f"📋 Período analizado: {fecha_inicio_totales} al {fecha_fin_totales}")
            else:
                st.warning(f"ℹ️ No se encontraron registros para el período: {fecha_inicio_totales} al {fecha_fin_totales}")

    st.write("---")

    # ===============================
    # 2. GRÁFICO ACTUALIZABLE AUTOMÁTICAMENTE
    # ===============================
    st.subheader("📈 Gráfico de Movimientos de Caja")
    
    # Obtener datos para el gráfico usando las mismas fechas del filtro superior
    datos_grafico = obtener_datos_grafico(id_grupo, fecha_inicio_totales, fecha_fin_totales)

    if datos_grafico:
        df = pd.DataFrame(datos_grafico)
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha').reset_index(drop=True)

        df['total_entrada'] = df['total_entrada'].fillna(0).astype(float)
        df['total_salida'] = df['total_salida'].fillna(0).astype(float)

        # Crear el gráfico
        fig, ax = plt.subplots(figsize=(12, 6))
        width = 0.35
        x = range(len(df))

        # Barras para entradas y salidas
        barras_entrada = ax.bar([i - width/2 for i in x], df['total_entrada'], 
                               width=width, color='#4CAF50', label='Entradas', alpha=0.8)
        barras_salida = ax.bar([i + width/2 for i in x], df['total_salida'], 
                              width=width, color='#F44336', label='Salidas', alpha=0.8)

        # Encontrar valores máximos para posicionar los textos
        max_entrada = df['total_entrada'].max()
        max_salida = df['total_salida'].max()
        max_valor = max(max_entrada, max_salida)

        # Agregar valores en las barras (solo si hay espacio suficiente)
        for i, row in df.iterrows():
            entrada_val = float(row['total_entrada'])
            salida_val = float(row['total_salida'])
            
            if entrada_val > 0:
                ax.text(i - width/2, entrada_val + max_valor*0.01,
                        f"${entrada_val:,.0f}", ha='center', va='bottom', 
                        fontsize=8, color='#2E7D32', fontweight='bold')
            
            if salida_val > 0:
                ax.text(i + width/2, salida_val + max_valor*0.01,
                        f"${salida_val:,.0f}", ha='center', va='bottom', 
                        fontsize=8, color='#B71C1C', fontweight='bold')

        # Configurar el gráfico
        ax.set_xlabel("Fecha", fontsize=12, fontweight='bold')
        ax.set_ylabel("Monto ($)", fontsize=12, fontweight='bold')
        
        # Título dinámico con el rango de fechas
        titulo = "Movimientos de Caja"
        if fecha_inicio_totales and fecha_fin_totales:
            titulo += f" ({fecha_inicio_totales} al {fecha_fin_totales})"
        
        ax.set_title(titulo, fontsize=16, fontweight='bold', pad=20)
        
        ax.set_xticks(x)
        ax.set_xticklabels([d.strftime('%d/%m/%Y') for d in df['fecha']], 
                          rotation=45, ha='right', fontsize=9)
        
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Remover bordes
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_alpha(0.3)
        ax.spines['bottom'].set_alpha(0.3)
        
        ax.legend(frameon=True, fancybox=True, shadow=True)

        # Mostrar el gráfico
        st.pyplot(fig)
            
    else:
        st.info("📊 No hay datos para mostrar en el gráfico. Seleccione un rango de fechas y haga clic en 'Calcular Totales'.")

    # ===============================
    # 3. Botón regresar
    # ===============================
    st.write("---")
    if st.button("⬅️ Regresar al Menú"):
        st.session_state.page = "menu"
        st.rerun()

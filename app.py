import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4
import io
import datetime
import random
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Envíos Angelitos",
    page_icon="✈️",
    layout="centered"
)

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .main {background-color: #F0F2F6;}
    .stButton>button {background-color: #1F2658; color: white; width: 100%;}
    .stButton>button:hover {background-color: #A8182D; color: white;}
    h1 {color: #1F2658;}
    </style>
""", unsafe_allow_html=True)

# --- ESTADO DE MEMORIA ---
if 'productos' not in st.session_state:
    st.session_state['productos'] = []

# --- DATOS CONSTANTES ---
LOGO_FILENAME = "logo solo.png" 
EMPRESA_NOMBRE = "ENVÍOS ANGELITOS"
TEL_ARUBA = "+297 5637658"
TEL_COLOMBIA = "+57 316 6981780"
PDF_AZUL = colors.HexColor("#1F2658")
PDF_ROJO = colors.HexColor("#A8182D")

# --- GENERADOR PDF ---
def generar_pdf(datos_cliente, productos, config):
    buffer = io.BytesIO()
    
    # 1. CÁLCULOS DE DESGLOSE
    total_peso = sum(p['peso'] for p in productos)
    total_impuestos = sum(p['imp'] for p in productos)
    total_valor_prod = sum(p['val'] for p in productos if p['cobrar'])
    
    tarifa = config['tarifa']
    valor_total_peso = total_peso * tarifa
    
    gran_total = valor_total_peso + total_impuestos + total_valor_prod

    # 2. DEFINICIÓN DE ALTURA
    ancho_a4 = A4[0]
    altura_encabezado = 200 
    altura_fila = 25
    altura_tabla = (len(productos) + 6) * altura_fila 
    altura_pie = 120
    altura_total = altura_encabezado + altura_tabla + altura_pie
    
    c = canvas.Canvas(buffer, pagesize=(ancho_a4, altura_total))
    width, height = ancho_a4, altura_total

    # --- ENCABEZADO ---
    c.setFillColor(PDF_AZUL)
    c.rect(0, height - 25, width, 25, fill=1, stroke=0)
    
    # Logo
    if os.path.exists(LOGO_FILENAME):
        try:
            logo_display_width = 250
            logo_display_height = logo_display_width * 0.43
            c.drawImage(LOGO_FILENAME, 30, height - 125, width=logo_display_width, height=logo_display_height, mask='auto', preserveAspectRatio=True)
        except:
            c.setFont("Helvetica-Bold", 28)
            c.drawString(30, height - 80, EMPRESA_NOMBRE)
    else:
        c.setFont("Helvetica-Bold", 28)
        c.drawString(30, height - 80, EMPRESA_NOMBRE)

    # Datos Contacto
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10)
    c.drawRightString(width - 30, height - 60, "Aruba ⇌ Colombia")
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 30, height - 75, f"Aruba: {TEL_ARUBA}")
    c.drawRightString(width - 30, height - 90, f"Colombia: {TEL_COLOMBIA}")

    # Bloque Cliente
    y_bloque = height - 160
    c.setFillColor(colors.HexColor("#F4F6F7"))
    c.roundRect(30, y_bloque - 60, width - 60, 80, 8, fill=1, stroke=0)

    c.setFillColor(PDF_AZUL)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(45, y_bloque, "FACTURADO A:")
    c.drawRightString(width - 45, y_bloque, "DETALLES:")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(45, y_bloque - 20, f"Cliente: {datos_cliente['nombre']}")
    c.drawString(45, y_bloque - 35, f"Dirección: {datos_cliente['direccion']}")
    c.drawString(45, y_bloque - 50, f"Tel: {datos_cliente['telefono']}")
    
    fecha = datetime.datetime.now().strftime("%Y-%m-%d")
    c.drawRightString(width - 45, y_bloque - 20, f"N° Factura: {random.randint(10000, 99999)}")
    c.drawRightString(width - 45, y_bloque - 35, f"Fecha: {fecha}")
    c.setFillColor(PDF_ROJO)
    c.drawRightString(width - 45, y_bloque - 50, f"Tarifa Base: {tarifa} {config['moneda']} / Kg")

    # --- TABLA CON DESGLOSE ---
    moneda = config['moneda']
    data = [['DESCRIPCIÓN', f'VALOR ({moneda})', 'PESO (Kg)', f'IMPUESTO ({moneda})']]
    
    for p in productos:
        data.append([
            p['desc'], f"{p['val']:,.0f}", f"{p['peso']}", f"{p['imp']:,.0f}"
        ])
    
    # FILAS DE CÁLCULO
    texto_calculo_peso = f"Total Peso ({total_peso} Kg x {tarifa})"
    data.append([texto_calculo_peso, '', '', f"{valor_total_peso:,.0f} {moneda}"])
    
    data.append(['Total Impuestos', '', '', f"{total_impuestos:,.0f} {moneda}"])
    
    if total_valor_prod > 0:
        data.append(['Valor Productos (Cobrados)', '', '', f"{total_valor_prod:,.0f} {moneda}"])
        
    # GRAN TOTAL
    data.append(['TOTAL A PAGAR', '', '', f"{gran_total:,.0f} {moneda}"])

    # Estilos
    table = Table(data, colWidths=[9*cm, 3.5*cm, 2.5*cm, 4*cm])
    
    estilos_tabla = [
        # Encabezado
        ('BACKGROUND', (0,0), (-1,0), PDF_AZUL),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        
        # Cuerpo (Productos)
        ('ROWBACKGROUNDS', (0,1), (-1,-5), [colors.white, colors.HexColor("#EBF5FB")]),
        ('LINEBEFORE', (1, 1), (-1, -5), 0.5, colors.HexColor("#D0D3D4")),
    ]
    
    # Lógica para estilos de las filas finales (Desglose)
    num_filas_extra = 3 if total_valor_prod == 0 else 4
    start_desglose = -num_filas_extra
    
    # Unir celdas para los textos
    estilos_extra = [('SPAN', (0, i), (2, i)) for i in range(start_desglose, 0)]
    estilos_tabla.extend(estilos_extra)
    
    # --- AQUÍ ESTÁ EL CAMBIO PRINCIPAL ---
    estilos_tabla.extend([
        # Estilo para TODAS las filas de desglose (Peso, Imp, Prod, Total Final)
        ('BACKGROUND', (0, start_desglose), (-1, -1), PDF_AZUL), # Fondo azul para todo el bloque
        ('TEXTCOLOR', (0, start_desglose), (-1, -1), colors.white), # Texto blanco para todo
        ('ALIGN', (0, start_desglose), (2, -1), 'RIGHT'), # Alinear textos a la derecha
        ('FONTNAME', (0, start_desglose), (-1, -1), 'Helvetica-Bold'), # Negrita para todo
        
        # Líneas blancas separadoras entre los totales para que no se vea un solo bloque azul
        ('LINEBELOW', (0, start_desglose), (-1, -2), 1, colors.white),

        # El GRAN TOTAL un poco más grande
        ('FONTSIZE', (0,-1), (-1,-1), 12),
    ])

    ts = TableStyle(estilos_tabla)
    table.setStyle(ts)
    
    y_tabla_inicio = y_bloque - 80
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, y_tabla_inicio - altura_tabla + altura_fila + 20) 

    # --- PIE DE PÁGINA ---
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.darkgrey)
    c.drawCentredString(width/2, 60, "¡Gracias por confiar en nosotros! Enviamos sus productos con el corazón.")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, 40, "Instagram: @envios.angelitos    |    Facebook: @envios Angelito aruba-colombia")

    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFAZ WEB ---

col_logo, col_titulo = st.columns([1, 3])
with col_logo:
    if os.path.exists(LOGO_FILENAME):
        st.image(LOGO_FILENAME, width=150)
with col_titulo:
    st.title("Gestión de Envíos ✈️")
    st.markdown("**Aruba ⇌ Colombia**")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuración")
    moneda = st.radio("Moneda:", ["Fl", "COP"], horizontal=True)
    tarifa_default = 20.0 if moneda == "Fl" else 45000.0
    tarifa = st.number_input("Tarifa por Kilo:", value=tarifa_default)
    if st.button("🗑️ Borrar lista"):
        st.session_state['productos'] = []
        st.rerun()

with st.container():
    st.subheader("👤 Datos del Cliente")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre Completo")
        telefono = st.text_input("Teléfono")
    with col2:
        direccion = st.text_input("Dirección")
        pais = st.selectbox("País Destino", ["Colombia", "Aruba"])

st.markdown("### 📦 Agregar Carga")
with st.form("form_prod", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    desc = c1.text_input("Descripción")
    val = c2.number_input("Valor Decl.", min_value=0.0)
    peso = c3.number_input("Peso (Kg)", min_value=0.0)
    imp = c4.number_input("Impuesto", min_value=0.0)
    cobrar = st.checkbox("¿Cobrar producto?")
    if st.form_submit_button("➕ Agregar"):
        if desc:
            st.session_state['productos'].append({
                "desc": desc, "val": val, "peso": peso, "imp": imp, "cobrar": cobrar
            })
            st.rerun()

if st.session_state['productos']:
    st.markdown("### 📋 Resumen")
    data_web = []
    total_web = 0
    for p in st.session_state['productos']:
        costo_envio = (p['peso'] * tarifa) + p['imp']
        linea = costo_envio + p['val'] if p['cobrar'] else costo_envio
        total_web += linea
        data_web.append({
            "Descripción": p['desc'],
            "Peso": f"{p['peso']} Kg",
            "Total Línea": f"{linea:,.0f}"
        })
    st.table(data_web)
    st.info(f"Total estimado: {total_web:,.0f} {moneda}")

    if nombre and telefono:
        datos = {"nombre": nombre, "telefono": telefono, "direccion": direccion}
        conf = {"moneda": moneda, "tarifa": tarifa}
        pdf = generar_pdf(datos, st.session_state['productos'], conf)
        st.download_button("📄 DESCARGAR PDF", pdf, f"Factura_{nombre}.pdf", "application/pdf")
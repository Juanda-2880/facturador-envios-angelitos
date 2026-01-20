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

# --- ESTILOS CSS PERSONALIZADOS (Para que se vea bonito en web) ---
st.markdown("""
    <style>
    .main {
        background-color: #F0F2F6;
    }
    .stButton>button {
        background-color: #1F2658;
        color: white;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #A8182D;
        color: white;
    }
    h1 {
        color: #1F2658;
    }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZAR ESTADO (Memoria de la app web) ---
if 'productos' not in st.session_state:
    st.session_state['productos'] = []

# --- DATOS CONSTANTES ---
LOGO_FILENAME = "logo solo.png" 
EMPRESA_NOMBRE = "ENVÍOS ANGELITOS"
TEL_ARUBA = "+297 5637658"
TEL_COLOMBIA = "+57 316 6981780"
PDF_AZUL = colors.HexColor("#1F2658")
PDF_ROJO = colors.HexColor("#A8182D")

# --- FUNCIÓN GENERADORA DE PDF ---
def generar_pdf(datos_cliente, productos, config):
    buffer = io.BytesIO()
    
    # Cálculos de altura dinámica
    ancho_a4 = A4[0]
    altura_encabezado = 200 
    altura_fila = 25
    altura_tabla = (len(productos) + 3) * altura_fila 
    altura_pie = 120
    altura_total = altura_encabezado + altura_tabla + altura_pie
    
    c = canvas.Canvas(buffer, pagesize=(ancho_a4, altura_total))
    width, height = ancho_a4, altura_total

    # 1. ENCABEZADO
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
    c.drawRightString(width - 45, y_bloque - 50, f"Tarifa Base: {config['tarifa']} {config['moneda']} / Kg")

    # 2. TABLA
    moneda = config['moneda']
    data = [['DESCRIPCIÓN', f'VALOR ({moneda})', 'PESO (Kg)', f'IMPUESTO ({moneda})']]
    total_pagar = 0
    
    for p in productos:
        data.append([
            p['desc'], f"{p['val']:,.0f}", f"{p['peso']}", f"{p['imp']:,.0f}"
        ])
        total_pagar += p['tot']
        
    data.append(['TOTAL', '', '', f"{total_pagar:,.0f} {moneda}"])

    table = Table(data, colWidths=[9*cm, 3.5*cm, 2.5*cm, 4*cm])
    
    ts = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PDF_AZUL),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#EBF5FB")]),
        ('LINEBEFORE', (1, 1), (-1, -2), 0.5, colors.HexColor("#D0D3D4")),
        ('BACKGROUND', (0,-1), (-1,-1), PDF_AZUL),
        ('TEXTCOLOR', (0,-1), (-1,-1), colors.white),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,-1), (-1,-1), 12),
        ('SPAN', (0,-1), (2,-1)), 
        ('ALIGN', (0,-1), (2,-1), 'RIGHT'), 
        ('ALIGN', (-1,-1), (-1,-1), 'CENTER'),
    ])
    table.setStyle(ts)
    
    y_tabla_inicio = y_bloque - 80
    table.wrapOn(c, width, height)
    table.drawOn(c, 30, y_tabla_inicio - altura_tabla + altura_fila + 20) 

    # 3. PIE DE PÁGINA
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(colors.darkgrey)
    c.drawCentredString(width/2, 60, "¡Gracias por confiar en nosotros! Enviamos sus productos con el corazón.")
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, 40, "Instagram: @envios.angelitos    |    Facebook: @envios Angelito aruba-colombia")

    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFAZ WEB (STREAMLIT) ---

# Header y Logo
col_logo, col_titulo = st.columns([1, 3])
with col_logo:
    if os.path.exists(LOGO_FILENAME):
        st.image(LOGO_FILENAME, width=150)
    else:
        st.warning("Logo no encontrado")
with col_titulo:
    st.title("Gestión de Envíos ✈️")
    st.markdown("**Aruba ⇌ Colombia**")

st.markdown("---")

# Sidebar (Configuración)
with st.sidebar:
    st.header("⚙️ Configuración")
    moneda = st.radio("Moneda:", ["Fl", "COP"], horizontal=True)
    tarifa_default = 20.0 if moneda == "Fl" else 45000.0
    tarifa = st.number_input("Tarifa por Kilo:", value=tarifa_default)
    
    if st.button("🗑️ Borrar toda la lista"):
        st.session_state['productos'] = []
        st.rerun()

# Formulario Cliente
with st.container():
    st.subheader("👤 Datos del Cliente")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre Completo")
        telefono = st.text_input("Teléfono")
    with col2:
        direccion = st.text_input("Dirección")
        pais = st.selectbox("País Destino", ["Colombia", "Aruba"])

# Formulario Agregar Producto
st.markdown("### 📦 Agregar Carga")
with st.form("form_producto", clear_on_submit=True):
    c1, c2, c3, c4 = st.columns(4)
    desc = c1.text_input("Descripción")
    val = c2.number_input("Valor Declarado", min_value=0.0)
    peso = c3.number_input("Peso (Kg)", min_value=0.0)
    imp = c4.number_input("Impuesto Extra", min_value=0.0)
    
    cobrar_prod = st.checkbox("¿Cobrar valor del producto al cliente?")
    
    submitted = st.form_submit_button("➕ Agregar a la Lista")
    
    if submitted and desc:
        costo_envio = (peso * tarifa) + imp
        total_linea = costo_envio + val if cobrar_prod else costo_envio
        
        st.session_state['productos'].append({
            "desc": desc, "val": val, "peso": peso, "imp": imp, 
            "tot": total_linea, "cobrar": cobrar_prod
        })

# Mostrar Tabla de Productos
if st.session_state['productos']:
    st.markdown("### 📋 Resumen de Factura")
    
    # Crear DataFrame para visualización limpia
    df_show = pd.DataFrame(st.session_state['productos'])
    # Formatear columnas para visualización
    df_vis = pd.DataFrame()
    df_vis['Descripción'] = df_show['desc']
    df_vis['Valor'] = df_show['val'].apply(lambda x: f"{x:,.0f}")
    df_vis['Peso'] = df_show['peso']
    df_vis['Impuesto'] = df_show['imp'].apply(lambda x: f"{x:,.0f}")
    df_vis['¿Se Cobra?'] = df_show['cobrar'].apply(lambda x: "SÍ" if x else "NO")
    df_vis['Total'] = df_show['tot'].apply(lambda x: f"{x:,.0f} {moneda}")
    
    st.table(df_vis)
    
    total_final = sum(p['tot'] for p in st.session_state['productos'])
    st.markdown(f"<h3 style='text-align: right; color: #1F2658;'>TOTAL A PAGAR: {total_final:,.0f} {moneda}</h3>", unsafe_allow_html=True)

    # Botón Generar PDF
    if nombre and telefono:
        datos_cliente = {"nombre": nombre, "direccion": direccion, "telefono": telefono, "pais": pais}
        config_factura = {"moneda": moneda, "tarifa": tarifa}
        
        pdf_bytes = generar_pdf(datos_cliente, st.session_state['productos'], config_factura)
        
        st.download_button(
            label="📄 DESCARGAR FACTURA PDF",
            data=pdf_bytes,
            file_name=f"Factura_{nombre.replace(' ','_')}.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("⚠️ Ingresa el nombre y teléfono del cliente para habilitar la descarga.")

else:
    st.info("Agrega productos para comenzar.")
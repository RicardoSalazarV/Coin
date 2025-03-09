import streamlit as st
import psycopg2
import os
from twilio.rest import Client

# ---------------------- CONFIGURACIÓN ----------------------

# Obtener la URL de la base de datos desde Render
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("🚨 ERROR: La variable de entorno DATABASE_URL no está definida.")

# Asegurar que la URL usa "postgresql://"
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

# Twilio (para WhatsApp)
TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
ADMIN_WHATSAPP_NUMBER = os.getenv("ADMIN_WHATSAPP_NUMBER")

def enviar_whatsapp(mensaje, numero_cliente):
    if TWILIO_SID and TWILIO_AUTH_TOKEN:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=mensaje,
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{numero_cliente}"
        )

# ---------------------- BASE DE DATOS ----------------------

def conectar_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        st.error(f"❌ ERROR: No se pudo conectar a la base de datos. {e}")
        raise

def obtener_menu():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, categoria, nombre, precio FROM menu")
    menu = cursor.fetchall()
    cursor.close()
    conn.close()
    return menu

def registrar_pedido(nombre_cliente, numero_cliente, productos, total):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pedidos (nombre_cliente, numero_cliente, productos, total) VALUES (%s, %s, %s, %s)",
                   (nombre_cliente, numero_cliente, productos, total))
    conn.commit()
    cursor.close()
    conn.close()
    
    mensaje = f"📌 *Nuevo Pedido de {nombre_cliente}*\n📋 Productos: {productos}\n💲 Total: ${total:.2f}"
    enviar_whatsapp(mensaje, numero_cliente)
    enviar_whatsapp("✅ Tu pedido ha sido registrado. Te avisaremos cuando esté listo. ☕", numero_cliente)

# ---------------------- INTERFAZ ----------------------

st.set_page_config(page_title="Cafetería", page_icon="☕", layout="wide")

# Opciones de navegación
seccion = st.sidebar.radio("Navegación", ["Página Principal", "Panel de Administración"])

if seccion == "Página Principal":
    st.title("☕ Menú de la Cafetería")
    
    # Mostrar menú de forma interactiva
    st.header("🛒 Hacer un Pedido")
    nombre_cliente = st.text_input("Nombre del Cliente")
    numero_cliente = st.text_input("Número de WhatsApp (+52...)")
    
    menu = obtener_menu()
    if not menu:
        st.warning("⚠️ No hay productos en el menú.")
    else:
        pedido = {}
        total = 0.0
        for producto_id, categoria, nombre, precio in menu:
            cantidad = st.number_input(f"{nombre} - ${precio:.2f}", min_value=0, max_value=10, value=0, step=1)
            if cantidad > 0:
                pedido[nombre] = (cantidad, precio)
        
        if pedido:
            st.subheader("🧾 Resumen del Pedido")
            productos_lista = []
            for nombre, (cantidad, precio) in pedido.items():
                productos_lista.append(f"{cantidad}x {nombre}")
                total += cantidad * precio
            
            st.write("\n".join(productos_lista))
            st.subheader(f"💰 Total: ${total:.2f}")
            
            if st.button("Enviar Pedido"):
                if nombre_cliente and numero_cliente:
                    productos_str = ", ".join(productos_lista)
                    registrar_pedido(nombre_cliente, numero_cliente, productos_str, total)
                    st.success("✅ Pedido registrado correctamente. Recibirás un mensaje cuando esté listo.")
                else:
                    st.error("⚠️ Todos los campos son obligatorios.")
        else:
            st.info("Selecciona al menos un producto para realizar el pedido.")

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

def enviar_whatsapp(mensaje):
    if TWILIO_SID and TWILIO_AUTH_TOKEN:
        client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=mensaje,
            from_=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            to=f"whatsapp:{ADMIN_WHATSAPP_NUMBER}"
        )

# ---------------------- BASE DE DATOS ----------------------

def conectar_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        st.error(f"❌ ERROR: No se pudo conectar a la base de datos. {e}")
        raise

def crear_tablas():
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu (
            id SERIAL PRIMARY KEY,
            categoria TEXT NOT NULL,
            nombre TEXT NOT NULL,
            precio NUMERIC NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            nombre_cliente TEXT NOT NULL,
            productos TEXT NOT NULL,
            total NUMERIC NOT NULL,
            estado TEXT DEFAULT 'Pendiente'
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

def obtener_menu():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT categoria, nombre, precio FROM menu")
    menu = cursor.fetchall()
    cursor.close()
    conn.close()
    return menu

def registrar_pedido(nombre_cliente, productos, total):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pedidos (nombre_cliente, productos, total) VALUES (%s, %s, %s)",
                   (nombre_cliente, productos, total))
    conn.commit()
    cursor.close()
    conn.close()
    
    mensaje = f"📌 Nuevo Pedido de {nombre_cliente}\nProductos: {productos}\nTotal: ${total:.2f}"
    enviar_whatsapp(mensaje)

def obtener_pedidos():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_cliente, productos, total, estado FROM pedidos WHERE estado = 'Pendiente'")
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return pedidos

def actualizar_estado_pedido(pedido_id, nuevo_estado):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET estado = %s WHERE id = %s", (nuevo_estado, pedido_id))
    conn.commit()
    cursor.close()
    conn.close()

def agregar_producto(nombre, categoria, precio):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO menu (nombre, categoria, precio) VALUES (%s, %s, %s)", (nombre, categoria, precio))
    conn.commit()
    cursor.close()
    conn.close()

def eliminar_producto(producto_id):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM menu WHERE id = %s", (producto_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ---------------------- INTERFAZ ----------------------

st.set_page_config(page_title="Cafetería", page_icon="☕", layout="wide")

# Opciones de navegación
seccion = st.sidebar.radio("Navegación", ["Página Principal", "Panel de Administración"])

if seccion == "Página Principal":
    st.title("☕ Menú de la Cafetería")

    # Mostrar menú
    st.header("Menú Disponible")
    menu = obtener_menu()
    if menu:
        for categoria, nombre, precio in menu:
            st.write(f"**{nombre}** - {categoria} - ${precio:.2f}")
    else:
        st.warning("No hay productos en el menú.")

    # Formulario para pedidos
    st.header("🛒 Hacer un Pedido")
    nombre_cliente = st.text_input("Nombre del Cliente")
    productos = st.text_area("Productos (separados por comas)")
    total = st.number_input("Total a pagar", min_value=0.0, format="%.2f")

    if st.button("Enviar Pedido"):
        if nombre_cliente and productos and total > 0:
            registrar_pedido(nombre_cliente, productos, total)
            st.success("✅ Pedido registrado correctamente.")
        else:
            st.error("⚠️ Todos los campos son obligatorios.")

elif seccion == "Panel de Administración":
    st.title("🔧 Panel de Administración")

    # Agregar producto al menú
    st.header("📋 Agregar Producto al Menú")
    nombre = st.text_input("Nombre del Producto")
    categoria = st.text_input("Categoría")
    precio = st.number_input("Precio", min_value=0.0, format="%.2f")

    if st.button("Agregar Producto"):
        if nombre and categoria and precio > 0:
            agregar_producto(nombre, categoria, precio)
            st.success("✅ Producto agregado al menú.")
        else:
            st.error("⚠️ Todos los campos son obligatorios.")

    # Eliminar producto del menú
    st.header("🗑️ Eliminar Producto del Menú")
    menu = obtener_menu()
    if menu:
        opciones = {f"{nombre} - {categoria} - ${precio:.2f}": i for i, (categoria, nombre, precio) in enumerate(menu)}
        seleccion = st.selectbox("Selecciona un producto para eliminar", list(opciones.keys()))
        if st.button("Eliminar Producto"):
            producto_id = opciones[seleccion] + 1  # Ajustar ID según la base de datos
            eliminar_producto(producto_id)
            st.success("✅ Producto eliminado correctamente.")
    else:
        st.warning("No hay productos en el menú.")

    # Gestión de pedidos
    st.header("📦 Pedidos Pendientes")
    pedidos = obtener_pedidos()
    if pedidos:
        for pedido in pedidos:
            pedido_id, nombre_cliente, productos, total, estado = pedido
            st.write(f"📌 **Pedido #{pedido_id}** - {nombre_cliente} - ${total:.2f}")
            st.write(f"📋 Productos: {productos}")
            if st.button(f"Marcar como Completado #{pedido_id}"):
                actualizar_estado_pedido(pedido_id, "Completado")
                st.success(f"✅ Pedido #{pedido_id} completado.")
    else:
        st.info("No hay pedidos pendientes.")

# Ejecutar la creación de tablas al iniciar
crear_tablas()
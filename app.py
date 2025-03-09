import streamlit as st
import psycopg2
import os

# Obtener la URL de la base de datos desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("🚨 ERROR: La variable de entorno DATABASE_URL no está definida.")

# Asegurar que la URL usa "postgresql://" en lugar de "postgres://"
DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

# Función para conectar a la base de datos
def conectar_db():
    try:
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        return conn
    except Exception as e:
        st.error(f"❌ ERROR: No se pudo conectar a la base de datos. Detalles: {e}")
        raise

# Función para crear las tablas si no existen
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

# Función para obtener el menú de la base de datos
def obtener_menu():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT categoria, nombre, precio FROM menu")
    menu = cursor.fetchall()
    cursor.close()
    conn.close()
    return menu

# Función para registrar un pedido
def registrar_pedido(nombre_cliente, productos, total):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO pedidos (nombre_cliente, productos, total) VALUES (%s, %s, %s)",
                   (nombre_cliente, productos, total))
    conn.commit()
    cursor.close()
    conn.close()

# Función para obtener los pedidos pendientes
def obtener_pedidos():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_cliente, productos, total, estado FROM pedidos WHERE estado = 'Pendiente'")
    pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return pedidos

# Función para actualizar el estado de un pedido
def actualizar_estado_pedido(pedido_id, nuevo_estado):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET estado = %s WHERE id = %s", (nuevo_estado, pedido_id))
    conn.commit()
    cursor.close()
    conn.close()

# ---------------------- INTERFAZ STREAMLIT ----------------------

st.title("☕ Menú de la Cafetería")

# Mostrar el menú
st.header("Menú Disponible")
menu = obtener_menu()
if menu:
    for categoria, nombre, precio in menu:
        st.write(f"**{nombre}** - {categoria} - ${precio:.2f}")
else:
    st.warning("No hay productos en el menú.")

# Formulario para hacer pedidos
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

# Sección para administrar pedidos
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

# Ejecutar la función de creación de tablas al inicio
crear_tablas()
import streamlit as st
import psycopg2
import os

# Obtener la URL de la base de datos desde Render (agregar en las variables de entorno)
DATABASE_URL = os.getenv("DATABASE_URL")

# Función para conectar a la base de datos PostgreSQL
def conectar_db():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

# Crear tabla si no existe
def crear_tablas():
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id SERIAL PRIMARY KEY,
            categoria TEXT NOT NULL,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# Función para obtener el menú
def obtener_menu():
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT categoria, nombre, precio FROM menu")
    menu = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return menu

# Función para agregar un nuevo producto al menú
def agregar_producto(categoria, nombre, precio):
    conn = conectar_db()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO menu (categoria, nombre, precio) VALUES (%s, %s, %s)", 
                   (categoria, nombre, precio))
    
    conn.commit()
    cursor.close()
    conn.close()

# Función para realizar un pedido
def realizar_pedido(producto, cantidad):
    st.success(f"Pedido recibido: {cantidad}x {producto}. ¡Gracias!")

# Llamar a la función de creación de tablas al iniciar
crear_tablas()

# Interfaz de la aplicación con Streamlit
st.title("Menú de la Cafetería ☕")

# Mostrar el menú actual
st.subheader("📜 Menú Disponible")
menu = obtener_menu()

if menu:
    for categoria, nombre, precio in menu:
        st.write(f"**{categoria}** - {nombre}: ${precio:.2f}")
else:
    st.warning("No hay productos en el menú.")

# Sección para agregar nuevos productos (solo administradores)
st.subheader("➕ Agregar Producto al Menú")
categoria = st.text_input("Categoría")
nombre = st.text_input("Nombre del Producto")
precio = st.number_input("Precio", min_value=0.0, format="%.2f")

if st.button("Agregar Producto"):
    if categoria and nombre and precio > 0:
        agregar_producto(categoria, nombre, precio)
        st.success(f"Producto {nombre} agregado con éxito.")
    else:
        st.error("Por favor, completa todos los campos.")

# Sección para realizar pedidos
st.subheader("🛒 Realizar Pedido")
productos = [f"{nombre} - ${precio:.2f}" for _, nombre, precio in menu]
producto_seleccionado = st.selectbox("Selecciona un producto", productos)
cantidad = st.number_input("Cantidad", min_value=1, step=1)

if st.button("Hacer Pedido"):
    realizar_pedido(producto_seleccionado, cantidad)
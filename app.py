import streamlit as st
import sqlite3
from twilio.rest import Client

# Configurar Twilio
TWILIO_SID = "TU_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "TU_AUTH_TOKEN"
TWILIO_PHONE = "whatsapp:+14155238886"  # Número oficial de Twilio

client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Función para obtener el menú
def obtener_menu():
    conn = sqlite3.connect("cafeteria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT categoria, nombre, precio FROM menu")
    datos = cursor.fetchall()
    conn.close()
    
    menu = {}
    for categoria, nombre, precio in datos:
        if categoria not in menu:
            menu[categoria] = {}
        menu[categoria][nombre] = precio
    return menu

# Función para enviar pedidos
def enviar_pedido(pedido, telefono):
    conn = sqlite3.connect("cafeteria.db")
    cursor = conn.cursor()
    for item, (cantidad, precio) in pedido.items():
        total = cantidad * precio
        cursor.execute("INSERT INTO pedidos (producto, cantidad, total, estado, telefono) VALUES (?, ?, ?, 'Pendiente', ?)", 
                       (item, cantidad, total, telefono))
    conn.commit()
    conn.close()

# Función para obtener pedidos
def obtener_pedidos():
    conn = sqlite3.connect("cafeteria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, producto, cantidad, total, estado, telefono FROM pedidos")
    pedidos = cursor.fetchall()
    conn.close()
    return pedidos

# Función para actualizar estado y notificar al cliente
def actualizar_estado_pedido(pedido_id, nuevo_estado, telefono, producto):
    conn = sqlite3.connect("cafeteria.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos SET estado = ? WHERE id = ?", (nuevo_estado, pedido_id))
    conn.commit()
    conn.close()
    
    # Enviar notificación si el pedido está listo
    if nuevo_estado == "Elaborado":
        mensaje = f"✅ Tu pedido de {producto} está listo para recoger. ¡Gracias por tu compra! ☕"
        client.messages.create(
            from_=TWILIO_PHONE,
            body=mensaje,
            to=f"whatsapp:{telefono}"
        )

# Función para verificar administrador
def verificar_admin(usuario, contraseña):
    conn = sqlite3.connect("cafeteria.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM administradores WHERE usuario = ? AND contraseña = ?", (usuario, contraseña))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None

# Sección de menú para clientes
st.title("Menú de la Cafetería ☕")
menu = obtener_menu()
pedido = {}
telefono = st.text_input("📞 Ingresa tu número de WhatsApp (+52... para México)", max_chars=15)

for categoria, items in menu.items():
    with st.expander(f"🍽️ {categoria}"):
        for item, precio in items.items():
            cantidad = st.number_input(f"{item} - ${precio} MXN", min_value=0, max_value=10, step=1, key=item)
            if cantidad > 0:
                pedido[item] = (cantidad, precio)

if pedido and telefono:
    if st.button("🛒 Enviar Pedido"):
        enviar_pedido(pedido, telefono)
        st.success("✅ Pedido enviado correctamente.")

# Panel de administración
st.sidebar.title("📋 Panel de Administración")
usuario = st.sidebar.text_input("Usuario")
contraseña = st.sidebar.text_input("Contraseña", type="password")
login_button = st.sidebar.button("Iniciar sesión")

if login_button and verificar_admin(usuario, contraseña):
    st.sidebar.success("Acceso concedido")
    st.title("📦 Pedidos en Cocina")

    pedidos = obtener_pedidos()
    if pedidos:
        for pedido_id, producto, cantidad, total, estado, telefono in pedidos:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"🍽️ {cantidad} x {producto} - ${total} MXN")
            with col2:
                st.write(f"📌 Estado: {estado}")
            with col3:
                if estado == "Pendiente":
                    if st.button(f"✅ Marcar como Elaborado", key=f"elab_{pedido_id}"):
                        actualizar_estado_pedido(pedido_id, "Elaborado", telefono, producto)
                        st.experimental_rerun()
                elif estado == "Elaborado":
                    st.write("✔️ Listo")
import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect("cafeteria.db")
cursor = conn.cursor()

# Crear tabla de menú
cursor.execute('''
CREATE TABLE IF NOT EXISTS menu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT,
    nombre TEXT UNIQUE,
    precio REAL
)
''')

# Crear tabla de pedidos con teléfono del cliente
cursor.execute('''
CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    producto TEXT,
    cantidad INTEGER,
    total REAL,
    estado TEXT DEFAULT 'Pendiente',
    telefono TEXT
)
''')

# Crear tabla de administradores
cursor.execute('''
CREATE TABLE IF NOT EXISTS administradores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT UNIQUE,
    contraseña TEXT
)
''')

# Insertar un administrador por defecto
try:
    cursor.execute("INSERT INTO administradores (usuario, contraseña) VALUES ('admin', 'admin123')")
except sqlite3.IntegrityError:
    pass  # Si ya existe, no hacer nada

conn.commit()
conn.close()
print("Base de datos configurada correctamente.")
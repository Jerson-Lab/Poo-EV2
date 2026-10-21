"""Conexión a SQLite y gestión de operaciones CRUD con consultas parametrizadas."""
import sqlite3

ESQUEMA = """
CREATE TABLE IF NOT EXISTS departamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    nombre TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS empleado (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    nombre TEXT NOT NULL, 
    direccion TEXT, 
    telefono TEXT,
    email TEXT NOT NULL, 
    fecha_inicio TEXT NOT NULL, 
    salario REAL NOT NULL,
    departamento_id INTEGER REFERENCES departamento(id)
);
CREATE TABLE IF NOT EXISTS proyecto (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    nombre TEXT NOT NULL, 
    descripcion TEXT, 
    fecha_inicio TEXT
);
CREATE TABLE IF NOT EXISTS registro_tiempo (
    id INTEGER PRIMARY KEY AUTOINCREMENT, 
    empleado_id INTEGER NOT NULL REFERENCES empleado(id),
    proyecto_id INTEGER NOT NULL REFERENCES proyecto(id),
    fecha TEXT NOT NULL, 
    horas REAL NOT NULL, 
    descripcion TEXT NOT NULL
);
"""

class BaseDatos:
    def __init__(self, ruta="ecotech.db"):
        self.__ruta = ruta

    def conectar(self):
        conexion = sqlite3.connect(self.__ruta)
        conexion.execute("PRAGMA foreign_keys = ON")
        return conexion

    def probar_conexion(self):
        try:
            with self.conectar() as con:
                version = con.execute("SELECT sqlite_version()").fetchone()[0]
            return True, f"Conexión exitosa (SQLite {version})"
        except sqlite3.Error as error:
            return False, f"Error de conexión: {error}"

    def crear_tablas(self):
        with self.conectar() as con:
            con.executescript(ESQUEMA)

    # --- OPERACIONES CRUD ---

    def insertar_departamento(self, nombre):
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("INSERT INTO departamento (nombre) VALUES (?)", (nombre,))
            con.commit()
            return cursor.lastrowid

    def obtener_departamentos(self):
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("SELECT id, nombre FROM departamento")
            return cursor.fetchall()

    def insertar_empleado(self, nombre, direccion, telefono, email, fecha_inicio, salario, departamento_id=None):
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute(
                """INSERT INTO empleado (nombre, direccion, telefono, email, fecha_inicio, salario, departamento_id)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (nombre, direccion, telefono, email, str(fecha_inicio), salario, departamento_id)
            )
            con.commit()
            return cursor.lastrowid

    def obtener_empleados(self):
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("SELECT id, nombre, direccion, telefono, email, fecha_inicio, salario, departamento_id FROM empleado")
            return cursor.fetchall()

    def actualizar_salario_empleado(self, empleado_id, nuevo_salario):
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("UPDATE empleado SET salario = ? WHERE id = ?", (nuevo_salario, empleado_id))
            con.commit()
            return cursor.rowcount > 0

    def eliminar_empleado(self, empleado_id):
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM empleado WHERE id = ?", (empleado_id,))
            con.commit()
            return cursor.rowcount > 0

    def insertar_proyecto(self, nombre, descripcion, fecha_inicio):
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute(
                "INSERT INTO proyecto (nombre, descripcion, fecha_inicio) VALUES (?, ?, ?)",
                (nombre, descripcion, str(fecha_inicio))
            )
            con.commit()
            return cursor.lastrowid

    def obtener_proyectos(self):
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute("SELECT id, nombre, descripcion, fecha_inicio FROM proyecto")
            return cursor.fetchall()

    def insertar_registro_tiempo(self, empleado_id, proyecto_id, fecha, horas, descripcion):
        with self.conectar() as con:
            cursor = con.cursor()
            cursor.execute(
                """INSERT INTO registro_tiempo (empleado_id, proyecto_id, fecha, horas, descripcion)
                   VALUES (?, ?, ?, ?, ?)""",
                (empleado_id, proyecto_id, str(fecha), horas, descripcion)
            )
            con.commit()
            return cursor.lastrowid
"""Conexión a SQLite con la librería oficial sqlite3 (consultas parametrizadas)."""
import sqlite3

ESQUEMA = """
CREATE TABLE IF NOT EXISTS departamento (
    id INTEGER PRIMARY KEY, nombre TEXT NOT NULL UNIQUE, gerente_id INTEGER);
CREATE TABLE IF NOT EXISTS empleado (
    id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, direccion TEXT, telefono TEXT,
    email TEXT NOT NULL, fecha_inicio TEXT NOT NULL, salario REAL NOT NULL,
    departamento_id INTEGER REFERENCES departamento(id));
CREATE TABLE IF NOT EXISTS cuenta_usuario (
    empleado_id INTEGER PRIMARY KEY REFERENCES empleado(id),
    usuario TEXT NOT NULL UNIQUE, password_hash BLOB NOT NULL, salt BLOB NOT NULL,
    rol TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS proyecto (
    id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, descripcion TEXT, fecha_inicio TEXT);
CREATE TABLE IF NOT EXISTS asignacion_proyecto (
    empleado_id INTEGER REFERENCES empleado(id),
    proyecto_id INTEGER REFERENCES proyecto(id),
    fecha_asignacion TEXT NOT NULL, fecha_fin TEXT,
    PRIMARY KEY (empleado_id, proyecto_id, fecha_asignacion));
CREATE TABLE IF NOT EXISTS registro_tiempo (
    id INTEGER PRIMARY KEY, empleado_id INTEGER NOT NULL REFERENCES empleado(id),
    proyecto_id INTEGER NOT NULL REFERENCES proyecto(id),
    fecha TEXT NOT NULL, horas REAL NOT NULL, descripcion TEXT NOT NULL);
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

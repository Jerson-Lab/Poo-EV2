"""Modelos del dominio de EcoTech Solutions (traducción del diagrama UML a Python)."""
import hashlib
import hmac
import os
from datetime import date, datetime

PERMISOS = {
    "ADMIN_RRHH": {"empleados", "departamentos", "proyectos", "informes"},
    "GERENTE": {"departamentos", "proyectos", "registros", "informes"},
    "EMPLEADO": {"registros"},
}


class CuentaUsuario:
    """Credenciales y permisos. Composición: la cuenta pertenece a un Empleado."""
    MAX_INTENTOS = 5

    def __init__(self, usuario, clave, rol="EMPLEADO"):
        if rol not in PERMISOS:
            raise ValueError(f"Rol inválido: {rol}")
        if len(clave) < 8:
            raise ValueError("La clave debe tener al menos 8 caracteres")
        self.__usuario = usuario
        self.__rol = rol
        self.__intentos_fallidos = 0
        self.__salt = os.urandom(16)
        self.__password_hash = self.__calcular_hash(clave)

    def __calcular_hash(self, clave):
        return hashlib.pbkdf2_hmac("sha256", clave.encode(), self.__salt, 100_000)

    @property
    def usuario(self):
        return self.__usuario

    @property
    def rol(self):
        return self.__rol

    def autenticar(self, clave):
        if self.__intentos_fallidos >= self.MAX_INTENTOS:
            return False
        if hmac.compare_digest(self.__calcular_hash(clave), self.__password_hash):
            self.__intentos_fallidos = 0
            return True
        self.__intentos_fallidos += 1
        return False

    def tiene_permiso(self, modulo):
        return modulo in PERMISOS[self.__rol]


class Empleado:
    """Clase base de personal. Atributos privados con validación en propiedades."""
    _contador_id = 0

    def __init__(self, nombre, direccion, telefono, email, fecha_inicio, salario,
                 cuenta=None):
        Empleado._contador_id += 1
        self.__id = Empleado._contador_id          # ID único automático
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.fecha_inicio = fecha_inicio
        self.salario = salario
        self.__cuenta = cuenta                      # composición 1 a 1
        self.__departamento = None                  # agregación: 0..1 departamento
        self.__asignaciones = []                    # vía AsignacionProyecto
        self.__registros = []

    @property
    def id(self):
        return self.__id

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío")
        self.__nombre = valor.strip()

    @property
    def direccion(self):
        return self.__direccion

    @direccion.setter
    def direccion(self, valor):
        self.__direccion = valor

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        if not str(valor).replace("+", "").replace(" ", "").isdigit():
            raise ValueError("Teléfono inválido")
        self.__telefono = str(valor)

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        if "@" not in valor or "." not in valor.split("@")[-1]:
            raise ValueError("Email inválido")
        self.__email = valor

    @property
    def fecha_inicio(self):
        return self.__fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self, valor):
        if not isinstance(valor, date):
            raise ValueError("fecha_inicio debe ser una fecha")
        self.__fecha_inicio = valor

    @property
    def salario(self):
        return self.__salario

    @salario.setter
    def salario(self, valor):
        if valor <= 0:
            raise ValueError("El salario debe ser positivo")
        self.__salario = valor

    @property
    def cuenta(self):
        return self.__cuenta

    @property
    def departamento(self):
        return self.__departamento

    @property
    def asignaciones(self):
        return list(self.__asignaciones)

    @property
    def registros(self):
        return list(self.__registros)

    def asignar_departamento(self, departamento):
        """Un empleado pertenece a un solo departamento a la vez (reasigna si ya tenía)."""
        if self.__departamento is not None:
            self.__departamento._retirar(self)
        departamento._incorporar(self)
        self.__departamento = departamento

    def _limpiar_departamento(self):
        self.__departamento = None

    def asignar_a_proyecto(self, proyecto):
        asignacion = AsignacionProyecto(self, proyecto)
        asignacion.asignar()
        return asignacion

    def _agregar_asignacion(self, asignacion):
        self.__asignaciones.append(asignacion)

    def esta_asignado(self, proyecto):
        return any(a.proyecto is proyecto and a.fecha_fin is None
                   for a in self.__asignaciones)

    def registrar_tiempo(self, proyecto, fecha, horas, descripcion):
        if not self.esta_asignado(proyecto):
            raise PermissionError("El empleado no está asignado a ese proyecto")
        registro = RegistroTiempo(self, proyecto, fecha, horas, descripcion)
        registro.validar()
        self.__registros.append(registro)
        return registro

    def __str__(self):
        return f"[{self.id}] {self.nombre}"


class Gerente(Empleado):
    """Especialización de Empleado (herencia)."""

    def __init__(self, *args, area_responsable="", **kwargs):
        super().__init__(*args, **kwargs)
        self.__area_responsable = area_responsable

    @property
    def area_responsable(self):
        return self.__area_responsable

    def aprobar_registros(self, registros):
        """Devuelve solo los registros válidos."""
        return [r for r in registros if r.validar()]

    def ver_reporte_depto(self):
        d = self.departamento
        if d is None:
            return {}
        return {"departamento": d.nombre, "empleados": len(d.empleados)}


class Departamento:
    _contador_id = 0

    def __init__(self, nombre, gerente=None):
        Departamento._contador_id += 1
        self.__id = Departamento._contador_id
        self.__nombre = nombre
        self.__gerente = gerente                   # asociación 0..1 a 1 con Gerente
        self.__empleados = []

    @classmethod
    def crear(cls, nombre, gerente=None):
        return cls(nombre, gerente)

    @property
    def id(self):
        return self.__id

    @property
    def nombre(self):
        return self.__nombre

    @property
    def gerente(self):
        return self.__gerente

    @property
    def empleados(self):
        return list(self.__empleados)

    def editar(self, nombre=None, gerente=None):
        if nombre:
            self.__nombre = nombre
        if gerente:
            self.__gerente = gerente

    @staticmethod
    def buscar(departamentos, nombre):
        return [d for d in departamentos if nombre.lower() in d.nombre.lower()]

    def eliminar(self):
        for e in list(self.__empleados):
            e._limpiar_departamento()
        self.__empleados.clear()

    def _incorporar(self, empleado):
        if empleado not in self.__empleados:
            self.__empleados.append(empleado)

    def _retirar(self, empleado):
        if empleado in self.__empleados:
            self.__empleados.remove(empleado)


class Proyecto:
    _contador_id = 0

    def __init__(self, nombre, descripcion, fecha_inicio):
        Proyecto._contador_id += 1
        self.__id = Proyecto._contador_id
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__fecha_inicio = fecha_inicio
        self.__asignaciones = []

    @classmethod
    def crear(cls, nombre, descripcion, fecha_inicio):
        return cls(nombre, descripcion, fecha_inicio)

    @property
    def id(self):
        return self.__id

    @property
    def nombre(self):
        return self.__nombre

    @property
    def descripcion(self):
        return self.__descripcion

    @property
    def fecha_inicio(self):
        return self.__fecha_inicio

    @property
    def asignaciones(self):
        return list(self.__asignaciones)

    def editar(self, nombre=None, descripcion=None):
        if nombre:
            self.__nombre = nombre
        if descripcion:
            self.__descripcion = descripcion

    def eliminar(self):
        self.__asignaciones.clear()

    def _agregar_asignacion(self, asignacion):
        self.__asignaciones.append(asignacion)


class AsignacionProyecto:
    """Clase asociación entre Empleado y Proyecto (relación muchos a muchos)."""

    def __init__(self, empleado, proyecto):
        self.__empleado = empleado
        self.__proyecto = proyecto
        self.__fecha_asignacion = date.today()
        self.__fecha_fin = None

    @property
    def empleado(self):
        return self.__empleado

    @property
    def proyecto(self):
        return self.__proyecto

    @property
    def fecha_asignacion(self):
        return self.__fecha_asignacion

    @property
    def fecha_fin(self):
        return self.__fecha_fin

    def asignar(self):
        self.__empleado._agregar_asignacion(self)
        self.__proyecto._agregar_asignacion(self)

    def desasignar(self):
        self.__fecha_fin = date.today()


class RegistroTiempo:
    def __init__(self, empleado, proyecto, fecha, horas, descripcion):
        self.empleado = empleado
        self.proyecto = proyecto
        self.fecha = fecha
        self.horas = horas
        self.descripcion = descripcion

    def validar(self):
        if not isinstance(self.fecha, date):
            raise ValueError("Fecha inválida")
        if not 0 < self.horas <= 24:
            raise ValueError("Las horas deben estar entre 0 y 24")
        if not self.descripcion or not self.descripcion.strip():
            raise ValueError("La descripción es obligatoria")
        return True

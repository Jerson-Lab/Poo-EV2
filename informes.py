"""Informes y exportadores (polimorfismo mediante la interfaz Exportador)."""
from abc import ABC, abstractmethod
from datetime import datetime


class Exportador(ABC):
    @abstractmethod
    def exportar(self, datos) -> bytes:
        ...


class ExportadorPDF(Exportador):
    def exportar(self, datos) -> bytes:
        # Pendiente: reemplazar por una librería oficial (p. ej. reportlab).
        return ("PDF\n" + "\n".join(str(f) for f in datos)).encode()


class ExportadorExcel(Exportador):
    def exportar(self, datos) -> bytes:
        # Pendiente: reemplazar por openpyxl para generar .xlsx real.
        return "\n".join(";".join(map(str, f)) for f in datos).encode()


class Informe:
    def __init__(self, titulo, filtros=None):
        self.__titulo = titulo
        self.__fecha_generacion = datetime.now()
        self.__filtros = filtros or {}
        self.__datos = []

    @property
    def titulo(self):
        return self.__titulo

    def generar(self, datos):
        self.__datos = list(datos)
        return self.__datos

    def exportar(self, exportador: Exportador) -> bytes:
        return exportador.exportar(self.__datos)

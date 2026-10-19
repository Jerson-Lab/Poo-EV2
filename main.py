from datetime import date
from modelos import (CuentaUsuario, Empleado, Gerente, Departamento, Proyecto)
from informes import Informe, ExportadorPDF, ExportadorExcel
from base_datos import BaseDatos


def main():
    gerente = Gerente("Ana Rojas", "Av. Providencia 123", "+56911111111",
                      "ana@ecotech.cl", date(2024, 3, 1), 2_500_000,
                      cuenta=CuentaUsuario("arojas", "Clave#Segura1", "GERENTE"),
                      area_responsable="I+D")
    emp = Empleado("Luis Pérez", "Calle 45", "+56922222222", "luis@ecotech.cl",
                   date(2025, 1, 10), 1_200_000,
                   cuenta=CuentaUsuario("lperez", "Otra#Clave22"))
    depto = Departamento.crear("Investigación y Desarrollo", gerente)
    proyecto = Proyecto.crear("Paneles solares", "Prototipo eficiente", date(2026, 2, 1))

    gerente.asignar_departamento(depto)
    emp.asignar_departamento(depto)
    emp.asignar_a_proyecto(proyecto)
    emp.registrar_tiempo(proyecto, date.today(), 6, "Pruebas de eficiencia")

    informe = Informe("Horas por empleado")
    informe.generar([
    ("Empleado", "Proyecto", "Horas"),          # fila de encabezados
    *[(r.empleado.nombre, r.proyecto.nombre, r.horas) for r in emp.registros],
    ])

    with open("informe.pdf", "wb") as archivo:
        archivo.write(informe.exportar(ExportadorPDF()))

    with open("informe.xlsx", "wb") as archivo:
        archivo.write(informe.exportar(ExportadorExcel()))

    print("Archivos generados: informe.pdf e informe.xlsx")

    print("Auth OK:", emp.cuenta.autenticar("Otra#Clave22"))
    print("Empleados en depto:", [str(e) for e in depto.empleados])

    informe = Informe("Horas por empleado")
    informe.generar([(r.empleado.nombre, r.proyecto.nombre, r.horas)
                     for r in emp.registros])
    for exportador in (ExportadorPDF(), ExportadorExcel()):   # polimorfismo
        print(type(exportador).__name__, informe.exportar(exportador)[:40])

    bd = BaseDatos()
    ok, mensaje = bd.probar_conexion()
    print(mensaje)
    if ok:
        bd.crear_tablas()


if __name__ == "__main__":
    main()

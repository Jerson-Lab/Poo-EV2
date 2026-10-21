from datetime import date
from base_datos import BaseDatos
from informes import Informe, ExportadorPDF, ExportadorExcel


def menu():
    bd = BaseDatos()
    ok, mensaje = bd.probar_conexion()
    print(f"[{'✔' if ok else '✖'}] {mensaje}")
    if ok:
        bd.crear_tablas()

    while True:
        print("\n--- SISTEMA DE GESTIÓN ECOTECH SOLUTIONS (CRUD PERSISTENTE) ---")
        print("1. Registrar Empleado (INSERT)")
        print("2. Crear Departamento (INSERT)")
        print("3. Crear Proyecto (INSERT)")
        print("4. Registrar Tiempo de Trabajo (INSERT)")
        print("5. Ver Empleados y Departamentos (SELECT)")
        print("6. Actualizar Salario de Empleado (UPDATE)")
        print("7. Eliminar Empleado (DELETE)")
        print("8. Generar Informe y Exportar (PDF/Excel)")
        print("9. Salir")
        
        opcion = input("\nSelecciona una opción (1-9): ").strip()

        if opcion == "1":
            print("\n--- Registrar Nuevo Empleado ---")
            nombre = input("Nombre completo: ")
            direccion = input("Dirección: ")
            telefono = input("Teléfono (+569...): ")
            email = input("Correo electrónico: ")
            salario = float(input("Salario CLP (ej: 1200000): "))
            
            # Listar departamentos para asignar opcionalmente
            deptos = bd.obtener_departamentos()
            depto_id = None
            if deptos:
                print("\nDepartamentos disponibles:")
                for d in deptos:
                    print(f"ID: {d[0]} - {d[1]}")
                d_input = input("Ingresa el ID del departamento (o déjalo vacío): ").strip()
                if d_input.isdigit():
                    depto_id = int(d_input)

            try:
                nuevo_id = bd.insertar_empleado(nombre, direccion, telefono, email, date.today(), salario, depto_id)
                print(f"¡Empleado registrado con éxito en la Base de Datos con ID {nuevo_id}!")
            except Exception as e:
                print(f"Error al registrar empleado: {e}")

        elif opcion == "2":
            print("\n--- Crear Departamento ---")
            nombre = input("Nombre del departamento: ")
            try:
                nuevo_id = bd.insertar_departamento(nombre)
                print(f"¡Departamento creado con éxito con ID {nuevo_id}!")
            except Exception as e:
                print(f"Error al crear departamento: {e}")

        elif opcion == "3":
            print("\n--- Crear Proyecto ---")
            nombre = input("Nombre del proyecto: ")
            desc = input("Descripción: ")
            try:
                nuevo_id = bd.insertar_proyecto(nombre, desc, date.today())
                print(f"¡Proyecto creado con éxito con ID {nuevo_id}!")
            except Exception as e:
                print(f"Error al crear proyecto: {e}")

        elif opcion == "4":
            print("\n--- Registrar Tiempo ---")
            empleados = bd.obtener_empleados()
            proyectos = bd.obtener_proyectos()

            if not empleados or not proyectos:
                print("Error: Debes tener al menos un empleado y un proyecto registrados en la base de datos.")
                continue

            print("Empleados:")
            for e in empleados:
                print(f"ID: {e[0]} - {e[1]}")
            emp_id = int(input("Ingresa el ID del empleado: "))

            print("\nProyectos:")
            for p in proyectos:
                print(f"ID: {p[0]} - {p[1]}")
            proy_id = int(input("Ingresa el ID del proyecto: "))

            horas = float(input("Cantidad de horas trabajadas: "))
            desc = input("Descripción de las tareas: ")

            try:
                bd.insertar_registro_tiempo(emp_id, proy_id, date.today(), horas, desc)
                print("¡Registro de tiempo guardado exitosamente en la base de datos!")
            except Exception as e:
                print(f"Error al registrar tiempo: {e}")

        elif opcion == "5":
            print("\n--- Listado desde la Base de Datos (SELECT) ---")
            deptos = bd.obtener_departamentos()
            print(f"\nDepartamentos ({len(deptos)}):")
            for d in deptos:
                print(f" - ID: {d[0]} | Nombre: {d[1]}")

            empleados = bd.obtener_empleados()
            print(f"\nEmpleados ({len(empleados)}):")
            for e in empleados:
                print(f" - ID: {e[0]} | Nombre: {e[1]} | Email: {e[4]} | Salario: ${e[6]:,.0f}")

            proyectos = bd.obtener_proyectos()
            print(f"\nProyectos ({len(proyectos)}):")
            for p in proyectos:
                print(f" - ID: {p[0]} | Nombre: {p[1]} | Desc: {p[2]}")

        elif opcion == "6":
            print("\n--- Actualizar Salario de Empleado (UPDATE) ---")
            empleados = bd.obtener_empleados()
            for e in empleados:
                print(f"ID: {e[0]} - {e[1]} (Salario actual: ${e[6]:,.0f})")
            
            emp_id = int(input("Ingresa el ID del empleado a actualizar: "))
            nuevo_salario = float(input("Ingresa el nuevo salario: "))

            if bd.actualizar_salario_empleado(emp_id, nuevo_salario):
                print("¡Salario actualizado con éxito en la base de datos!")
            else:
                print("No se encontró un empleado con ese ID.")

        elif opcion == "7":
            print("\n--- Eliminar Empleado (DELETE) ---")
            empleados = bd.obtener_empleados()
            for e in empleados:
                print(f"ID: {e[0]} - {e[1]}")
            
            emp_id = int(input("Ingresa el ID del empleado a eliminar: "))
            if bd.eliminar_empleado(emp_id):
                print("¡Empleado eliminado con éxito de la base de datos!")
            else:
                print("No se encontró un empleado con ese ID.")

        elif opcion == "8":
            print("\n--- Generar Informes ---")
            informe = Informe("Reporte General de Actividades")
            
            # Simular datos recopilados para exportar
            datos_filas = [("ID", "Nombre", "Email", "Salario")]
            for e in bd.obtener_empleados():
                datos_filas.append((e[0], e[1], e[4], e[6]))

            informe.generar(datos_filas)

            with open("informe.pdf", "wb") as f:
                f.write(informe.exportar(ExportadorPDF()))
            with open("informe.xlsx", "wb") as f:
                f.write(informe.exportar(ExportadorExcel()))
            
            print("¡Archivos 'informe.pdf' e 'informe.xlsx' exportados con éxito!")

        elif opcion == "9":
            print("Saliendo del sistema. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Por favor, elige un número del 1 al 9.")


if __name__ == "__main__":
    menu()
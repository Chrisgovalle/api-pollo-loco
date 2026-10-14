# API Pollo Loco

API REST para gestionar clientes, ventas de pollo y el costo actual del pollo.
Hecha con Python, FastAPI y Pydantic. Sin base de datos: la información se guarda en memoria.

## Requisitos
- Python 3.9 o superior

## Instalación y ejecución

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Abre la documentación Swagger en: http://localhost:8000/docs

## Endpoints

| Operación | Método y URL |
|---|---|
| Listar clientes | GET /v1/api/clientes |
| Registrar cliente | POST /v1/api/clientes |
| Actualizar cliente | PUT /v1/api/clientes/{id_cliente} |
| Desactivar cliente | DELETE /v1/api/clientes/{id_cliente} |
| Registrar venta | POST /v1/api/ventas |
| Consultar ventas (reporte) | GET /v1/api/ventas?fecha_inicio=AAAA-MM-DD&fecha_fin=AAAA-MM-DD |
| Actualizar venta | PUT /v1/api/ventas/{id_venta} |
| Ver costo del pollo | GET /v1/api/costo-pollo |
| Modificar costo del pollo | PUT /v1/api/costo-pollo |

## Reglas
- Los clientes no se eliminan: DELETE cambia `active` a `false`.
- Solo se registran ventas de clientes activos.
- No se puede actualizar una venta de un cliente inactivo.
- El reporte solo muestra clientes activos y calcula `total_venta = cantidad_pollo × costo_pollo`.
- Cada venta guarda el costo vigente al momento de registrarse.
- Costo inicial: 350.00

## Integrantes
- Christian Gabriel Gonzalez Ovalle
-Alejandro Mireles Velazquez 

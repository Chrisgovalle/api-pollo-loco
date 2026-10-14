from datetime import date, datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

app = FastAPI(
    title="API Pollo Loco",
    description="API REST para gestión de clientes y ventas de pollo",
    version="1.0.0",
)

clientes = []
ventas = []
costo_pollo = 350.00

siguiente_id_cliente = 1
siguiente_id_venta = 1


class CrearCliente(BaseModel):
    nombre_cliente: str = Field(..., min_length=1, examples=["Juan Pérez"])
    direccion: str = Field(..., min_length=1, examples=["Calle 5 #123, Guadalupe"])


class ActualizarCliente(BaseModel):
    nombre_cliente: str = Field(..., min_length=1)
    direccion: str = Field(..., min_length=1)


class CrearVenta(BaseModel):
    id_cliente: int
    cantidad_pollo: float = Field(..., ge=0, description="No puede ser negativa")
    fecha_registro: Optional[datetime] = None


class ActualizarVenta(BaseModel):
    cantidad_pollo: Optional[float] = Field(None, ge=0)
    fecha_registro: Optional[datetime] = None


class ActualizarCosto(BaseModel):
    costo_pollo: float = Field(..., ge=0, description="No puede ser negativo")


def buscar_cliente(id_cliente: int):
    for cliente in clientes:
        if cliente["id_cliente"] == id_cliente:
            return cliente
    return None


def buscar_venta(id_venta: int):
    for venta in ventas:
        if venta["id_venta"] == id_venta:
            return venta
    return None


def quitar_zona_horaria(fecha: datetime) -> datetime:
    """Evita errores al comparar fechas con y sin zona horaria."""
    if fecha.tzinfo is not None:
        return fecha.astimezone().replace(tzinfo=None)
    return fecha


@app.get("/v1/api/clientes", tags=["Clientes"])
def listar_clientes():
    return {
        "exito": True,
        "total_clientes": len(clientes),
        "clientes": clientes,
    }


@app.post("/v1/api/clientes", status_code=201, tags=["Clientes"])
def registrar_cliente(datos: CrearCliente):
    global siguiente_id_cliente

    nuevo = {
        "id_cliente": siguiente_id_cliente,
        "nombre_cliente": datos.nombre_cliente,
        "direccion": datos.direccion,
        "active": True,
    }
    clientes.append(nuevo)
    siguiente_id_cliente += 1

    return {"exito": True, "mensaje": "Cliente registrado", "cliente": nuevo}


@app.put("/v1/api/clientes/{id_cliente}", tags=["Clientes"])
def actualizar_cliente(id_cliente: int, datos: ActualizarCliente):
    cliente = buscar_cliente(id_cliente)
    if cliente is None:
        raise HTTPException(status_code=404, detail="El cliente no existe")

    cliente["nombre_cliente"] = datos.nombre_cliente
    cliente["direccion"] = datos.direccion

    return {"exito": True, "mensaje": "Cliente actualizado", "cliente": cliente}


@app.delete("/v1/api/clientes/{id_cliente}", tags=["Clientes"])
def desactivar_cliente(id_cliente: int):
    """Borrado lógico: el cliente NO se elimina, solo cambia active a False."""
    cliente = buscar_cliente(id_cliente)
    if cliente is None:
        raise HTTPException(status_code=404, detail="El cliente no existe")

    cliente["active"] = False

    return {"exito": True, "mensaje": "Cliente desactivado", "cliente": cliente}


@app.put("/v1/api/clientes/{id_cliente}/activar", tags=["Clientes"])
def activar_cliente(id_cliente: int):
    """Reactiva un cliente que fue desactivado (active vuelve a True)."""
    cliente = buscar_cliente(id_cliente)
    if cliente is None:
        raise HTTPException(status_code=404, detail="El cliente no existe")

    cliente["active"] = True

    return {"exito": True, "mensaje": "Cliente activado", "cliente": cliente}


@app.post("/v1/api/ventas", status_code=201, tags=["Ventas"])
def registrar_venta(datos: CrearVenta):
    global siguiente_id_venta

    cliente = buscar_cliente(datos.id_cliente)
    if cliente is None:
        raise HTTPException(status_code=404, detail="El cliente no existe")
    if not cliente["active"]:
        raise HTTPException(
            status_code=409,
            detail="No se puede registrar una venta para un cliente inactivo",
        )

    fecha = datos.fecha_registro if datos.fecha_registro else datetime.now()

    nueva = {
        "id_venta": siguiente_id_venta,
        "id_cliente": datos.id_cliente,
        "cantidad_pollo": datos.cantidad_pollo,
        "fecha_registro": quitar_zona_horaria(fecha),
        "costo_pollo": costo_pollo,
    }
    ventas.append(nueva)
    siguiente_id_venta += 1

    return {"exito": True, "mensaje": "Venta registrada", "venta": nueva}


@app.get("/v1/api/ventas", tags=["Ventas"])
def consultar_ventas(
    fecha_inicio: Optional[date] = Query(None, description="Formato AAAA-MM-DD"),
    fecha_fin: Optional[date] = Query(None, description="Formato AAAA-MM-DD"),
):
    """Reporte de ventas: solo clientes activos, con filtro opcional por fecha."""
    if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
        raise HTTPException(
            status_code=400,
            detail="fecha_inicio no puede ser mayor que fecha_fin",
        )

    resultado = []
    for venta in ventas:
        cliente = buscar_cliente(venta["id_cliente"])

        if cliente is None or not cliente["active"]:
            continue

        dia_venta = venta["fecha_registro"].date()
        if fecha_inicio and dia_venta < fecha_inicio:
            continue
        if fecha_fin and dia_venta > fecha_fin:
            continue

        resultado.append(
            {
                "id_venta": venta["id_venta"],
                "id_cliente": cliente["id_cliente"],
                "nombre_cliente": cliente["nombre_cliente"],
                "direccion": cliente["direccion"],
                "cantidad_pollo": venta["cantidad_pollo"],
                "fecha_registro": venta["fecha_registro"],
                "costo_pollo": venta["costo_pollo"],
                "total_venta": venta["cantidad_pollo"] * venta["costo_pollo"],
            }
        )

    return {
        "exito": True,
        "total_ventas": len(resultado),
        "total_general": sum(v["total_venta"] for v in resultado),
        "ventas": resultado,
    }


@app.put("/v1/api/ventas/{id_venta}", tags=["Ventas"])
def actualizar_venta(id_venta: int, datos: ActualizarVenta):
    venta = buscar_venta(id_venta)
    if venta is None:
        raise HTTPException(status_code=404, detail="La venta no existe")

    cliente = buscar_cliente(venta["id_cliente"])
    if cliente is None:
        raise HTTPException(status_code=404, detail="El cliente no existe")
    if not cliente["active"]:
        raise HTTPException(
            status_code=409,
            detail="No se puede actualizar una venta de un cliente inactivo",
        )

    if datos.cantidad_pollo is None and datos.fecha_registro is None:
        raise HTTPException(
            status_code=400,
            detail="Envía al menos cantidad_pollo o fecha_registro",
        )

    if datos.cantidad_pollo is not None:
        venta["cantidad_pollo"] = datos.cantidad_pollo
    if datos.fecha_registro is not None:
        venta["fecha_registro"] = quitar_zona_horaria(datos.fecha_registro)

    return {"exito": True, "mensaje": "Venta actualizada", "venta": venta}



@app.get("/v1/api/costo-pollo", tags=["Costo del pollo"])
def ver_costo_pollo():
    return {"exito": True, "costo_pollo": costo_pollo}


@app.put("/v1/api/costo-pollo", tags=["Costo del pollo"])
def modificar_costo_pollo(datos: ActualizarCosto):
    global costo_pollo
    costo_pollo = datos.costo_pollo
    return {
        "exito": True,
        "mensaje": "Costo actualizado. Se usará en las ventas nuevas",
        "costo_pollo": costo_pollo,
    }
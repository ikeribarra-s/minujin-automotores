import enum


class EstadoVehiculo(str, enum.Enum):
    disponible = "disponible"
    reservado = "reservado"
    vendido = "vendido"


class TipoVehiculo(str, enum.Enum):
    usado = "usado"
    cero_km = "cero_km"


class Procedencia(str, enum.Enum):
    compra = "compra"
    permuta = "permuta"
    consignacion = "consignacion"


class FormaPagoVenta(str, enum.Enum):
    contado = "contado"
    financiado = "financiado"
    permuta = "permuta"
    mixto = "mixto"


class ConceptoCobro(str, enum.Enum):
    sena = "sena"
    saldo = "saldo"
    cuota = "cuota"
    otro = "otro"


class FormaPagoCobro(str, enum.Enum):
    efectivo = "efectivo"
    transferencia = "transferencia"
    cheque = "cheque"
    tarjeta = "tarjeta"


class EstadoCheque(str, enum.Enum):
    pendiente = "pendiente"
    cobrado = "cobrado"
    rechazado = "rechazado"
    depositado = "depositado"

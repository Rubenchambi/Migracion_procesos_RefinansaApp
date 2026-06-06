from ninja import Schema
from typing import Optional
from decimal import Decimal

class MetaCarteraSchema(Schema):
    cartera_id: int
    cartera_nombre: str
    tipo_meta: str
    mes_asignacion: int
    año_asignacion: int
    meta_monto: Decimal
    
    # Campos opcionales (pueden ser null en la BD)
    tramo: Optional[str] = None
    subcartera: Optional[str] = None
    asesor_nombre: Optional[str] = None
    meta_porcentaje: Optional[Decimal] = None
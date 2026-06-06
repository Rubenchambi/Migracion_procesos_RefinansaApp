from ninja import Router
from apps.db import obtener_engine_sql
from .schemas import MetaCarteraSchema
from sqlalchemy import text
from datetime import datetime
from typing import List

router = Router()

@router.get("/listar-metas")
def listar_metas(request, page: int = 1, page_size: int = 5):
    engine = obtener_engine_sql(db_type="metas")
    offset = (page - 1) * page_size
    
    # Consulta con paginación
    query = text(f"""
        SELECT * FROM [dbo].[metas_carteras] WHERE activo = 1 
        ORDER BY fecha_registro DESC
        OFFSET {offset} ROWS FETCH NEXT {page_size} ROWS ONLY
    """)
    
    # Consulta para saber el total de registros (para la paginación)
    count_query = text("SELECT COUNT(*) FROM [dbo].[metas_carteras] WHERE activo = 1")
    
    with engine.connect() as conn:
        total = conn.execute(count_query).scalar()
        result = conn.execute(query)
        metas = [dict(row._mapping) for row in result]
        
    return {"items": metas, "total": total, "page": page, "pages": (total // page_size) + 1}

@router.get("/carteras-maestra")
def listar_carteras_maestra(request):
    # Endpoint auxiliar para llenar tu <select> dinámico
    engine = obtener_engine_sql(db_type="metas")
    query = text("SELECT DISTINCT cartera_id, cartera_nombre FROM [dbo].[metas_carteras] WHERE activo = 1")
    with engine.connect() as conn:
        result = conn.execute(query)
        return [dict(row._mapping) for row in result]

@router.post("/guardar-meta")
def guardar_meta(request, data: MetaCarteraSchema):
    engine = obtener_engine_sql(db_type="metas")
    
    # Lógica de UPSERT (Update or Insert)
    update_query = text("""
        UPDATE [dbo].[metas_carteras] 
        SET cartera_nombre = :cartera_nombre, tramo = :tramo, tipo_meta = :tipo_meta, 
            subcartera = :subcartera, asesor_nombre = :asesor_nombre, 
            meta_monto = :meta_monto, meta_porcentaje = :meta_porcentaje,
            mes_asignacion = :mes_asignacion, año_asignacion = :año_asignacion
        WHERE cartera_id = :cartera_id AND mes_asignacion = :mes_asignacion AND año_asignacion = :año_asignacion
    """)
    
    insert_query = text("""
        INSERT INTO [dbo].[metas_carteras] 
        (cartera_id, cartera_nombre, tramo, tipo_meta, subcartera, asesor_nombre, 
         meta_monto, meta_porcentaje, mes_asignacion, año_asignacion, activo, fecha_registro)
        VALUES 
        (:cartera_id, :cartera_nombre, :tramo, :tipo_meta, :subcartera, :asesor_nombre, 
         :meta_monto, :meta_porcentaje, :mes_asignacion, :año_asignacion, 1, :fecha)
    """)
    
    with engine.begin() as conn:
        result = conn.execute(update_query, data.dict())
        if result.rowcount == 0:
            conn.execute(insert_query, {**data.dict(), "fecha": datetime.now()})
            mensaje = "Meta creada exitosamente"
        else:
            mensaje = "Meta actualizada correctamente"
            
    return {"success": True, "message": mensaje}

@router.get("/configuracion-cartera/{cartera_id}")
def obtener_configuracion(request, cartera_id: int):
    engine = obtener_engine_sql(db_type="metas")
    
    with engine.connect() as conn:
        # 1. Obtenemos el nombre
        res_nombre = conn.execute(
            text("SELECT TOP 1 cartera_nombre FROM [dbo].[metas_carteras] WHERE cartera_id = :id"), 
            {"id": cartera_id}
        ).fetchone()
        cartera_nombre = res_nombre[0] if res_nombre else "Desconocida"
        
        # 2. Obtenemos tramos
        res_tramos = conn.execute(
            text("SELECT DISTINCT tramo FROM [dbo].[metas_carteras] WHERE cartera_id = :id AND tramo IS NOT NULL"), 
            {"id": cartera_id}
        ).fetchall()
        tramos = [r[0] for r in res_tramos]
        
        # 3. Obtenemos subcarteras
        res_sub = conn.execute(
            text("SELECT DISTINCT subcartera FROM [dbo].[metas_carteras] WHERE cartera_id = :id AND subcartera IS NOT NULL"), 
            {"id": cartera_id}
        ).fetchall()
        subcarteras = [r[0] for r in res_sub]
        
        # 4. Obtenemos tipos
        res_tipos = conn.execute(
            text("SELECT DISTINCT tipo_meta FROM [dbo].[metas_carteras] WHERE cartera_id = :id AND tipo_meta IS NOT NULL"), 
            {"id": cartera_id}
        ).fetchall()
        tipos = [r[0] for r in res_tipos]
        
        return {
            "cartera_nombre": cartera_nombre,
            "tramos": tramos,
            "subcarteras": subcarteras,
            "tipos": tipos
        }
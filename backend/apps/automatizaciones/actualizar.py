from ninja import Router, File, Form
from ninja.files import UploadedFile
import pandas as pd
from sqlalchemy import text
from apps.db import obtener_engine_sql

router = Router()

# 1. VISTA PREVIA
@router.post("/actualizar-preview")
def preview_datos(request, archivo: UploadedFile = File(...)):
    df = pd.read_excel(archivo.file)
    return {
        "success": True,
        "total_filas": len(df),
        "columnas": df.columns.tolist(),
        "preview": df.head(5).to_dict(orient="records")
    }

# 2. EJECUCIÓN DINÁMICA
@router.post("/actualizar-ejecutar")
def ejecutar_actualizacion(
    request, 
    archivo: UploadedFile = File(...),
    opcion: str = Form(...),
    mes: int = Form(...),
    anio: int = Form(...)
):
    try:
        df = pd.read_excel(archivo.file)
        engine = obtener_engine_sql(db_type="actualizacion")
        
        with engine.begin() as conn:
            # Limpieza
            conn.execute(text("DELETE FROM [Actualizar_datos]"))
            # Carga
            df.to_sql('Actualizar_datos', con=conn, if_exists='append', index=False, chunksize=5000)
            
            # Procesamiento Dinámico
            mensaje = "Solo se subieron los datos correctamente."
            params = {"mes": mes, "anio": anio}
            
            if opcion in ["1", "2", "3"]:
                queries = {
                    "1": "UPDATE matr_hip_2025 SET pagos = ad.PAGOS, fecha_pago = ad.FECHA_PAGOS FROM matr_hip_2025 AS pre JOIN Actualizar_datos AS ad ON ad.ENTIDADES = pre.idcliente WHERE mes_asignacion = :mes AND año_asignacion = :anio AND cartera = 'ADMINISTRADA' AND estado = 'Activo'",
                    "2": "UPDATE matr_hip_2025 SET pagos = CASE WHEN p.PAGOS >= (m.total_saldo_vencido * m.total_saldo_diferido) THEN (m.total_saldo_vencido * m.total_saldo_diferido) ELSE p.PAGOS END, fecha_pago = CAST(p.FECHA_PAGOS AS VARCHAR(20)) FROM matr_hip_2025 AS m JOIN Actualizar_datos AS p ON p.ENTIDADES = m.idcliente WHERE m.cartera = 'HIPOTECARIO' AND m.mes_asignacion = :mes AND m.año_asignacion = :anio AND m.estado = 'Activo'",
                    "3": "UPDATE matr_conv_2025 SET pagos = ad.PAGOS, fecha_pago = ad.FECHA_PAGOS FROM matr_conv_2025 AS pre JOIN Actualizar_datos AS ad ON ad.ENTIDADES = pre.idcliente WHERE mes_asignacion = :mes AND año_asignacion = :anio AND cartera = 'CONVENIO' AND estado = 'Activo'"
                }
                conn.execute(text(queries[opcion]), params)
                mensaje = f"Proceso {opcion} ejecutado exitosamente para {mes}/{anio}."

        return {"success": True, "proceso": mensaje}

    except Exception as e:
        return {"success": False, "error": str(e)}
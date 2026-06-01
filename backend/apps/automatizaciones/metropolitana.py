import os
from datetime import datetime
import pandas as pd
from ninja import Router, File
from ninja.files import UploadedFile
from sqlalchemy import text
from apps.db import obtener_engine_sql 
from datetime import datetime, timedelta
router = Router()

# =================================================================
# CONFIGURACIÓN DINÁMICA (Mes actual)
# =================================================================
def obtener_nombre_tabla():
    """Genera el nombre de la tabla según el mes/año actual, ej: AsignacionCmetro_May26"""
    hoy = datetime.now() - timedelta(days=1)
    mes_corto = hoy.strftime("%b").capitalize() # Ej: May
    anio_corto = hoy.strftime("%y")             # Ej: 26
    return f"AsignacionCmetro_{mes_corto}{anio_corto}"

def obtener_ruta_excel_defecto():
    """Calcula la ruta automática en la red"""
    hoy = datetime.now()
    anio = str(hoy.year)

    MESES_ESPANOL = {
        1: "1.Enero", 2: "2.Febrero", 3: "3.Marzo", 4: "4.Abril",
        5: "5.Mayo", 6: "6.Junio", 7: "7.Julio", 8: "8.Agosto",
        9: "9.Septiembre", 10: "10.Octubre", 11: "11.Noviembre", 12: "12.Diciembre"
    }
    mes_carpeta = MESES_ESPANOL[hoy.month]
    
    ruta_base = rf"//192.168.1.249/Compartido/compartido_Refinansa_2022/Reingenieria Procesos/{anio}/Complementos_SQL_{anio}/{mes_carpeta}/Subir asignacion-SQL"
    archivo_nombre = "Actualizacion-metropolitana_dxd_subir.xlsx"
    return os.path.join(ruta_base, archivo_nombre)

def procesar_metropolitana(origen):
    """Lógica de limpieza y tipos de datos"""
    dtypes = {
        'NroDocumento-Credito': str, 'Credito': str, 'Codigo': str,
        'CodigoSbs': str, 'año': str, 'mes': str,
        'NroDocumento': str, 'DiasAtraso': str
    }
    df = pd.read_excel(origen, sheet_name='Asignacion_metropolitana_diario', dtype=dtypes)
    df["created_at"] = datetime.now()
    return df

# =================================================================
# ENDPOINT 1: PREVISUALIZACIÓN
# =================================================================
@router.post("/preview")
def preview_metropolitana(request, archivo: UploadedFile = File(None)):
    origen = archivo if archivo else obtener_ruta_excel_defecto()
    tabla_destino = obtener_nombre_tabla()
    
    try:
        df = procesar_metropolitana(origen)
        engine = obtener_engine_sql(db_type="asignaciones")
        
        with engine.connect() as conn:
            # Validamos si la tabla existe antes de contar
            query = text(f"SELECT COUNT(*) FROM [{tabla_destino}]")
            try:
                registros_antes = conn.execute(query).scalar()
            except:
                registros_antes = 0 # Si la tabla no existe aún
        preview_data = df.head(10).to_dict(orient="records")    
        return {
            "success": True,
            "tabla_destino": tabla_destino,
            "filas_excel": len(df),
            "registros_antes": registros_antes,
            "preview": preview_data
        }
    except Exception as e:
        return {"success": False, "error": f"Error en preview: {str(e)}"}

# =================================================================
# ENDPOINT 2: EJECUCIÓN
# =================================================================
@router.post("/ejecutar")
def ejecutar_metropolitana(request, archivo: UploadedFile = File(None)):
    origen = archivo if archivo else obtener_ruta_excel_defecto()
    tabla_destino = obtener_nombre_tabla()
    
    try:
        df = procesar_metropolitana(origen)
        engine = obtener_engine_sql(db_type="asignaciones")
        
        # Inserción
        df.to_sql(tabla_destino, con=engine, if_exists="append", index=False, chunksize=1000)
        
        return {
            "success": True, 
            "message": f"Carga exitosa en tabla {tabla_destino}",
            "filas_insertadas": len(df)
        }
    except Exception as e:
        return {"success": False, "error": f"Fallo en la carga SQL: {str(e)}"}
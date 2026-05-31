import os
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
from ninja import File, Router
from ninja.files import UploadedFile
from sqlalchemy import text
from fastapi import Form
from fastapi import Request

# Importamos tu conector de base de datos reutilizable
from apps.db import obtener_engine_sql

load_dotenv()
router = Router()

# Nombre de tu tabla fija en SQL Server
TABLA = "Actualizar_Lista_negra"

# =================================================================
# GENERACIÓN DINÁMICA DE LA RUTA DE RED (Criterio Mensual)
# =================================================================
def obtener_ruta_excel_defecto():
    """Calcula automáticamente la ruta en la red basándose en el año

    y mes actual del sistema, respetando tu estructura de carpetas.
    """
    hoy = datetime.now()
    anio_actual = str(hoy.year)
    mes_numero = hoy.month

    # Tu formato exacto de carpetas mensuales (Número.Nombre)
    MESES_ESPANOL = {
        1: "1.Enero", 2: "2.Febrero", 3: "3.Marzo", 4: "4.Abril",
        5: "5.Mayo", 6: "6.Junio", 7: "7.Julio", 8: "8.Agosto",
        9: "9.Septiembre", 10: "10.Octubre", 11: "11.Noviembre", 12: "12.Diciembre"
    }
    
    mes_carpeta = MESES_ESPANOL[mes_numero]
    
    # Construcción de la ruta con tus variables de red dinámicas
    ruta_base = rf"//192.168.1.249/Compartido/compartido_Refinansa_2022/Reingenieria Procesos/{anio_actual}/Complementos_SQL_{anio_actual}/{mes_carpeta}/Subir asignacion-SQL"
    archivo_nombre = "Actualizar_ListaNegra_telefonos_subir.xlsx"
    
    return os.path.join(ruta_base, archivo_nombre)


# =================================================================
# FUNCIÓN INTERNA DE PROCESAMIENTO (100% tus dtypes y filtros)
# =================================================================
def procesar_y_limpiar_excel(ruta_o_archivo):
    df = pd.read_excel(
        ruta_o_archivo,
        dtype={
            "nro_documento": str,
            "telefono": str,
            "observaciones": str,
            "fecha_registro": str,
            "obs": str,
            "cartera_id": "Int64",
            "estado": str,
        },
    )

    # Tus limpiezas y conversiones exactas
    for col in ["nro_documento", "telefono", "observaciones", "obs", "estado"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace(["nan", "None", "null", ""], None)

    if "cartera_id" in df.columns:
        df["cartera_id"] = (
            pd.to_numeric(df["cartera_id"], errors="coerce").astype("Int64")
        )

    df["created_at"] = datetime.now()
    return df


# =================================================================
# ENDPOINT 1: PREVISUALIZACIÓN (Paso 1)
# =================================================================
@router.post("/lista-negra/preview")
def preview_lista_negra(request, archivo: UploadedFile = File(None)):
    # Si no suben archivo por el Front, calculamos la ruta del mes actual en la red
    if archivo is None:
        ruta_calculada = obtener_ruta_excel_defecto()
        if not os.path.exists(ruta_calculada):
            return {
                "success": False,
                "error": f"No se encontró el archivo automático del mes en la red. Ruta buscada:\n{ruta_calculada}"
            }
        origen_datos = ruta_calculada
        nombre_archivo = os.path.basename(ruta_calculada)
    else:
        # Si arrastran un archivo modificado o con otro nombre al Front
        origen_datos = archivo
        nombre_archivo = archivo.name

    try:
        df = procesar_y_limpiar_excel(origen_datos)
        filas_excel = len(df)
        duplicados_excel = int(
            df.duplicated(subset=["nro_documento", "telefono"], keep=False).sum()
        )

        # Consulta de control "Antes" con el engine centralizado
        engine = obtener_engine_sql()
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM [{TABLA}]"))
            registros_antes = result.scalar()

        # Mandamos las primeras 5 filas para que el usuario las valide visualmente
        preview_data = df.head(10).to_dict(orient="records")

        return {
            "success": True,
            "nombre_archivo": nombre_archivo,
            "filas_excel": filas_excel,
            "duplicados_excel": duplicados_excel,
            "registros_antes": registros_antes,
            "preview_filas": preview_data,
        }
    except Exception as e:
        return {"success": False, "error": f"Error al previsualizar el Excel: {str(e)}"}


# =================================================================
# ENDPOINT 2: EJECUCIÓN FINAL (Paso 2)
# =================================================================
@router.post("/lista-negra/ejecutar")
async def ejecutar_carga_lista_negra(request):
    accion = request.POST.get("accion", "insertar")
    archivo = request.FILES.get("archivo")
    
    print(f"DEBUG: Accion recibida: {accion}")
    print(f"DEBUG: Archivo recibido: {archivo}")
    tiempo_inicio = datetime.now()

    if archivo is None or archivo == 'undefined':
        ruta_calculada = obtener_ruta_excel_defecto()
        origen_datos = ruta_calculada
        nombre_archivo = os.path.basename(ruta_calculada)
    else:
        # FastAPI recibe el archivo como objeto UploadFile, 
        # accedemos a .file para obtener el stream de datos
        origen_datos = archivo.file
        nombre_archivo = archivo.name

    try:
        df = procesar_y_limpiar_excel(origen_datos)
        filas_excel = len(df)
        duplicados_excel = int(
            df.duplicated(subset=["nro_documento", "telefono"], keep=False).sum()
        )

        engine = obtener_engine_sql()

        with engine.connect() as conn:
            # Lógica de Limpieza
            if accion == "limpiar":
                conn.execute(text(f"TRUNCATE TABLE [{TABLA}]"))

            result = conn.execute(text(f"SELECT COUNT(*) FROM [{TABLA}]"))
            registros_antes = result.scalar()
            conn.commit()

        # Inserción en SQL Server
        df.to_sql(
            TABLA,
            con=engine,
            if_exists="append",
            index=False,
            chunksize=1000,
        )

        # Conteo final y última fecha
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM [{TABLA}]"))
            registros_despues = result.scalar()

            result = conn.execute(text(f"SELECT MAX(created_at) FROM [{TABLA}]"))
            ultima_fecha = result.scalar()
            ultima_fecha_str = (
                ultima_fecha.strftime("%Y-%m-%d %H:%M:%S")
                if ultima_fecha
                else "N/A"
            )

        filas_insertadas = registros_despues - registros_antes
        tiempo_total = (datetime.now() - tiempo_inicio).total_seconds()

        return {
            "success": True,
            "resumen": {
                "archivo": nombre_archivo,
                "filas_excel": filas_excel,
                "registros_antes": registros_antes,
                "filas_insertadas": filas_insertadas,
                "total_sql": registros_despues,
                "ultima_fecha_created": ultima_fecha_str,
                "tiempo_total_segundos": round(tiempo_total, 1),
            },
            "alertas": {
                "diferencia_filas": filas_insertadas != filas_excel,
                "duplicados_excel": duplicados_excel,
            },
        }

    except Exception as e:
        return {"success": False, "error": f"Fallo en la carga SQL: {str(e)}"}
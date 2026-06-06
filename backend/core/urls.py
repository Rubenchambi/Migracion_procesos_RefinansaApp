from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
# Importamos el router donde está tu proceso de lista negra
from apps.automatizaciones.api import router as automatizaciones_router
from apps.automatizaciones.metropolitana import router as metropolitana_router
from apps.automatizaciones.actualizar import router as actualizar_router
from apps.metas.meta import router as metas_router
# Inicializamos Django Ninja con el título de tu proyecto
api = NinjaAPI(
    title="RefinansaApp API",
    version="1.0.0",
    description="Sistema Centralizado de Automatizaciones y Procesos - Refinansaperú"
)

# Registramos el router de tus scripts bajo el prefijo /automatizaciones
api.add_router("/automatizaciones/", automatizaciones_router)
api.add_router("/automatizaciones/metropolitana", metropolitana_router)
api.add_router("/automatizaciones/", actualizar_router)
api.add_router("/metas", metas_router)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls), # <-- Aquí se expone toda tu API
]
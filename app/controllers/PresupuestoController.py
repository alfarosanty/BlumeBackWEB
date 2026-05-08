from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Annotated, cast
from app.core.security import obtener_usuario_confirmado
from app.models.Usuario import Usuario
from app.schemas.PresupuestoSchema import PresupuestoCreate, PresupuestoFiltros, PresupuestoResponse, PresupuestoUpdate
from app.schemas.pagination import PagedResponse
from app.services.IPresupuestoService import IPresupuestoService
from app.services.imp.PresupuestoService import get_presupuesto_service
from app.services.imp.PDFService import PDFService
from app.services.imp.EmailService import EmailService

router = APIRouter(prefix="/presupuestos", tags=["Presupuesto"])

PresupuestoServiceDep = Annotated[IPresupuestoService, Depends(get_presupuesto_service)]

def enviar_notificacion_background(presupuesto_id: int, email_destino: str, service: IPresupuestoService):
    """
    Orquesta la generación del PDF y envío de Email fuera del request principal.
    """

    print(f"--- Iniciando envío de mail para Presupuesto ID: {presupuesto_id} ---")
    db_presupuesto = service.get_by_id(presupuesto_id)
    if not db_presupuesto:
        return

    pdf_service = PDFService()
    email_service = EmailService()
    
    pdf_bytes = None
    estado = str(db_presupuesto.estado.value).lower() if hasattr(db_presupuesto.estado, 'value') else str(db_presupuesto.estado).lower()
    
    if estado != "eliminado":
        pdf_bytes = pdf_service.generar_presupuesto_pdf(db_presupuesto)
        
    exito = email_service.enviar_notificacion_presupuesto(
        email_destino=email_destino,
        presupuesto=db_presupuesto,
        pdf_content=pdf_bytes
    )
    if exito:
        print(f"--- Mail enviado con éxito a {email_destino} ---")
    else:
        print(f"--- Error crítico: El mail a {email_destino} no salió ---")


@router.get("", response_model=PagedResponse[PresupuestoResponse])
def get_presupuestos(
    service: PresupuestoServiceDep,
    filtros: PresupuestoFiltros = Depends(),
    auth: Usuario = Depends(obtener_usuario_confirmado)
):
    return service.obtener_presupuestos_filtrados(filtros, auth)

@router.post("", response_model=PresupuestoResponse, status_code=status.HTTP_201_CREATED)
def crear_presupuesto(
    service: PresupuestoServiceDep,
    presupuesto: PresupuestoCreate,
    background_tasks: BackgroundTasks,
    auth: Usuario = Depends(obtener_usuario_confirmado)
):
    # Evitamos errores de comparación con cast explícito
    id_cliente_auth = int(cast(int, auth.id_cliente)) if auth.id_cliente else 0 # type: ignore
    
    if auth.rol == "client" and presupuesto.id_cliente != id_cliente_auth: # type: ignore
        raise HTTPException(status_code=403, detail="No podés crear presupuestos para otro cliente")
    
    nuevo_presupuesto = service.crear(presupuesto)
    
    # Usamos getattr o cast para que Pylance no vea el objeto 'Column'
    p_id = int(cast(int, nuevo_presupuesto.id))
    u_email = str(auth.email) if auth.email else "" # type: ignore

    background_tasks.add_task(
        enviar_notificacion_background, 
        p_id, 
        u_email, 
        service
    )
    
    return nuevo_presupuesto

@router.put("/{presupuesto_id}", response_model=PresupuestoResponse)
def actualizar_presupuesto(
    presupuesto_id: int,
    service: PresupuestoServiceDep,
    presupuesto_in: PresupuestoUpdate,
    background_tasks: BackgroundTasks,
    auth: Usuario = Depends(obtener_usuario_confirmado)
):
    if auth.rol != "admin": # type: ignore
        raise HTTPException(status_code=403, detail="No tenés permiso para editar este presupuesto")

    db_presupuesto = service.get_by_id(presupuesto_id)
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    presupuesto_upd = service.actualizar(presupuesto_id, presupuesto_in)

    if presupuesto_upd.cliente and hasattr(presupuesto_upd.cliente, 'email') and presupuesto_upd.cliente.email:
        p_id = int(cast(int, presupuesto_upd.id))
        c_email = str(presupuesto_upd.cliente.email) # type: ignore
        
        background_tasks.add_task(
            enviar_notificacion_background, 
            p_id, 
            c_email, 
            service
        )

    return presupuesto_upd

@router.get("/{presupuesto_id}", response_model=PresupuestoResponse)
def obtener_presupuesto(
    presupuesto_id: int,
    service: IPresupuestoService = Depends(get_presupuesto_service),
    auth: Usuario = Depends(obtener_usuario_confirmado)
):
    db_presupuesto = service.get_by_id(presupuesto_id)
    
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    if auth.rol == "client": # type: ignore
        id_cliente_db = int(cast(int, db_presupuesto.id_cliente))
        id_cliente_auth = int(cast(int, auth.id_cliente)) if auth.id_cliente else -1 # type: ignore
        
        if id_cliente_db != id_cliente_auth:
            raise HTTPException(status_code=403, detail="No tenés permiso para ver este presupuesto")
    
    return db_presupuesto
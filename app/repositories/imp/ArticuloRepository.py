from typing import Any, Iterable, Mapping, Optional
from sqlalchemy.orm import Session, joinedload
from app.models import ArticuloPrecio, Articulo
from IArticuloRepository import IArticuloRepository
from app.schemas.pagination import PagedResponse

class ArticuloRepository(IArticuloRepository):

    db: Session

    def __init__(self, db: Session):
        """Recibe la sesión de base de datos (Inyección de dependencia manual)"""
        self.db = db

    def get_paginado(
        self, 
        skip: int, 
        limit: int, 
        filtro_codigo: Optional[str] = None,
        id_subfamilia: Optional[int] = None,
        id_articulo_precio: Optional[int] = None
    ) -> PagedResponse[Articulo]:
        
        # 1. Armamos la query base con Eager Loading (Include en .NET)
        query = self.db.query(Articulo).options(
            joinedload(Articulo.subfamilia),
            joinedload(Articulo.articulo_precio)
        )

        # 2. Aplicamos filtros
        if id_subfamilia:
            query = query.filter(Articulo.id_subfamilia == id_subfamilia)
        
        if id_articulo_precio:
            query = query.filter(Articulo.id_articulo_precio == id_articulo_precio)
            
        if filtro_codigo:
            query = query.filter(Articulo.codigo == filtro_codigo)

        # 3. Ejecutamos la lógica de base de datos
        total = query.count()
        items = query.offset(skip).limit(limit).all()

        # 4. Usamos TU CLASE para devolver el objeto completo
        # Esto calcula la página actual y las totales automáticamente
        return PagedResponse[Articulo].crear(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    
    def get_precio_paginado(
        self, 
        skip: int, 
        limit: int, 
        filtro_codigo: Optional[str] = None,
    ) -> PagedResponse[ArticuloPrecio]:
        
        # 1. Armamos la query base con Eager Loading (Include en .NET)
        query = self.db.query(ArticuloPrecio)

        # 2. Aplicamos filtros           
        if filtro_codigo:
            query = query.filter(ArticuloPrecio.codigo == filtro_codigo)

        # 3. Ejecutamos la lógica de base de datos
        total = query.count()
        items = query.offset(skip).limit(limit).all()

        # 4. Usamos TU CLASE para devolver el objeto completo
        # Esto calcula la página actual y las totales automáticamente
        return PagedResponse[ArticuloPrecio].crear(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )

    def sync_precios(self, mappings: Iterable[Mapping[str, Any]]) -> int:
        try:
            for data in mappings:
                # Al ser Mapping[str, Any], el ** ya no tira error
                nuevo_precio = ArticuloPrecio(**data) 
                self.db.merge(nuevo_precio)
            
            self.db.commit()
            # Para contar elementos de un Iterable de forma segura:
            return sum(1 for _ in mappings)
        except Exception as e:
            self.db.rollback()
            raise e
        
    def sync_articulos(self, mappings: Iterable[Mapping[str, Any]]) -> int:
        try:
            contador = 0
            for data in mappings:
                # Sincronizamos el objeto
                nuevo_articulo = Articulo(**data) 
                self.db.merge(nuevo_articulo)
                contador += 1
            
            self.db.commit()
            return contador
            
        except Exception as e:
            self.db.rollback()
            raise e
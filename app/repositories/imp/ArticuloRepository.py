from typing import Any, Iterable, List, Mapping, Optional
from urllib.parse import unquote
from fastapi import Query
from sqlalchemy import func, text
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session, joinedload, selectinload
from app.models import ArticuloPrecio, Articulo, Familia, SubFamilia
from app.repositories.IArticuloRepository import IArticuloRepository
from app.schemas import ArticuloPrecioSchema, ArticuloSchema, PagedResponse, ArticuloSugerencia
import time

class ArticuloRepository(IArticuloRepository):

    db: Session

    def __init__(self, db: Session):
        """Recibe la sesión de base de datos (Inyección de dependencia manual)"""
        self.db = db

    def get_paginado(
        self, 
        skip: Optional[int], 
        limit: Optional[int], 
        filtro_codigo: Optional[str] = None,
        id_subfamilia: Optional[int] = None,
        id_articulo_precio: Optional[int] = None
    ) -> PagedResponse[ArticuloSchema]:
        
        start_time = time.time()
        codigo_limpio = unquote(filtro_codigo) if filtro_codigo else None
        
        query = self.db.query(Articulo).options(
            joinedload(Articulo.color),
            joinedload(Articulo.medida),
            joinedload(Articulo.subfamilia).joinedload(SubFamilia.familia).joinedload(Familia.sector),
            joinedload(Articulo.articulo_precio)
        )

        if id_subfamilia:
            query = query.filter(Articulo.id_subfamilia == id_subfamilia)
        if id_articulo_precio:
            query = query.filter(Articulo.id_articulo_precio == id_articulo_precio)
        if codigo_limpio:
            query = query.filter(Articulo.codigo == codigo_limpio)

        db_items = query.offset(skip).limit(limit).all()

        items_schema = [ArticuloSchema.model_validate(item) for item in db_items]

        total_estimado = (skip or 0) + len(db_items)

        
        return PagedResponse[ArticuloSchema].crear(
            items=items_schema, 
            total=total_estimado, 
            skip=skip or 0, 
            limit=limit or 1
        )    
    def get_precio_paginado(self, skip: int, 
                        limit: int,
                        filtro_codigo: Optional[str] = None, 
                        sector_id: Optional[int] = None, 
                        familia_id: Optional[int] = None, 
                        subfamilia_id: Optional[int] = None
                        )-> PagedResponse[ArticuloPrecioSchema]:
    
        print(f"Sector: {sector_id} | Familia: {familia_id} | Subfamilia: {subfamilia_id} | Codigo: {filtro_codigo}")
        print(f"Skip: {skip} | Limit: {limit}")

        subquery = (
            self.db.query(func.min(Articulo.id).label("min_id"))
            .group_by(Articulo.codigo)
            .subquery()
        )

        query = self.db.query(ArticuloPrecio).join(Articulo)

        query = query.filter(Articulo.id.in_(subquery.select()))

        if sector_id:
            query = query.outerjoin(Articulo.subfamilia).outerjoin(SubFamilia.familia)
            query = query.filter(Familia.id_sector == sector_id)

        if familia_id:
            if not sector_id:
                query = query.outerjoin(Articulo.subfamilia)
            query = query.filter(SubFamilia.id_familia == familia_id)
        total_real = query.count()
        print(f"DEBUG: Total de productos encontrados: {total_real}")

        items = query.offset(skip).limit(limit).all()
        print(f"DEBUG: Items retornados en esta página: {len(items)}")
        
        items_schema = [ArticuloPrecioSchema.model_validate(item) for item in items]

        return PagedResponse[ArticuloPrecioSchema].crear(
            items=items_schema, 
            total=total_real,
            skip=skip or 0, 
            limit=limit or 20
        )

    def sync_precios(self, mappings: Iterable[Mapping[str, Any]]) -> int:
        try:
            precios_list = list(mappings)
            if not precios_list:
                return 0
                
            stmt = insert(ArticuloPrecio).values(precios_list)
            
            do_update_stmt = stmt.on_duplicate_key_update(
                codigo=stmt.inserted.codigo,
                descripcion=stmt.inserted.descripcion,
                precio1=stmt.inserted.precio1,
                precio2=stmt.inserted.precio2,
                precio3=stmt.inserted.precio3
            )
            
            self.db.execute(do_update_stmt)
            self.db.commit()
            
            return len(precios_list)
            
        except Exception as e:
            self.db.rollback()
            raise e
            
    def sync_articulos(self, mappings: Iterable[Mapping[str, Any]]) -> int:
        articulos_list = list(mappings)
        if not articulos_list:
            print("\n[SYNC] ⚠️ No llegaron artículos para procesar.")
            return 0
            
        print(f"\n[SYNC] 🚀 Iniciando sincronización de {len(articulos_list)} artículos...")
        
        batch_size = 500
        total_insertados = 0
        
        try:
            for i in range(0, len(articulos_list), batch_size):
                batch = articulos_list[i:i + batch_size]
                
                # --- DEBUG DE DATOS ---
                print(f"\n--- Analizando Lote {i//batch_size + 1} ---")
                for idx, item in enumerate(batch[:3]): # Miramos los primeros 3 de cada lote
                    print(f"Item {idx} de muestra: Cod={item.get('codigo')}, Color={item.get('id_color')}, Medida={item.get('id_medida')}, ID={item.get('id')}")

                # 1. Armamos el insert
                stmt = insert(Articulo).values(batch)
                
                # 2. Definimos el Upsert
                do_update_stmt = stmt.on_duplicate_key_update(
                    codigo=stmt.inserted.codigo,
                    descripcion=stmt.inserted.descripcion,
                    id_color=stmt.inserted.id_color,
                    id_medida=stmt.inserted.id_medida,
                    id_subfamilia=stmt.inserted.id_subfamilia,
                    id_articulo_precio=stmt.inserted.id_articulo_precio,
                    habilitado=stmt.inserted.habilitado
                )
                
                # 3. Ejecutamos y miramos qué dice MySQL
                result = self.db.execute(do_update_stmt)
                
                # rowcount en MySQL: 1 si insertó, 2 si actualizó (pisó)
                print(f"RESULTADO: Filas afectadas en este lote: {result.rowcount}") # type: ignore
                if result.rowcount > len(batch): # type: ignore
                    print(f"⚠️ AVISO: Hay {result.rowcount - len(batch)} actualizaciones. Estás PISANDO datos existentes.") # type: ignore
                
                total_insertados += len(batch)

            self.db.commit()
            print(f"\n[SYNC] ✅ Finalizado. Total procesado: {total_insertados} registros.\n")
            return total_insertados
            
        except Exception as e:
            self.db.rollback()
            print(f"\n[ERROR CRÍTICO] ❌ Falló la sincronización:")
            print(f"Tipo de error: {type(e).__name__}")
            print(f"Mensaje: {str(e)}")
            # Si el error es de MySQL, suele traer el detalle de la clave que falló
            raise e
        
    def actualizar_url_foto(self, articulo_precio_id: int, url: str) -> None:
        # Buscamos el registro
        articulo = self.db.query(ArticuloPrecio).filter(
            ArticuloPrecio.id == articulo_precio_id
        ).first()
        
        if articulo:
            articulo.url_foto = url # type: ignore
            self.db.commit()
            self.db.refresh(articulo)
        else:
            # Manejo básico si no se encuentra el ID
            raise ValueError(f"No se encontró el artículo con ID {articulo_precio_id}")
        

    def get_sugerencias(self, query_booleana: str) -> List[ArticuloSugerencia]:
        sql = text("""
            SELECT ap.id, ap.codigo, ap.descripcion, ap.url_foto, ap.precio1 as precio
            FROM articulos_precio ap
            WHERE MATCH(ap.codigo, ap.descripcion) AGAINST(:q IN BOOLEAN MODE)
            ORDER BY MATCH(ap.codigo, ap.descripcion) AGAINST(:q IN BOOLEAN MODE) DESC
            LIMIT 5
        """)
        
        result = self.db.execute(sql, {"q": query_booleana})
        
        # El mapeo es una sola línea, sin objetos anidados
        return [ArticuloSugerencia(**row._asdict()) for row in result]
    

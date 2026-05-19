from typing import Any, Iterable, List, Mapping, Optional, Dict
from urllib.parse import unquote
from sqlalchemy import func, text, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import Session, joinedload
from app.models import ArticuloPrecio, Articulo, Familia, SubFamilia, ArticuloMaestro
from app.models.ArticuloMaestroXArticuloPrecio import ArticuloMaestroXArticuloPrecio
from app.repositories.IArticuloRepository import IArticuloRepository
from app.schemas import ArticuloPrecioSchema, ArticuloSchema, PagedResponse, ArticuloSugerencia
from sqlalchemy.orm import joinedload, contains_eager

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
                        subfamilia_id: Optional[int] = None,
                        filtro_codigo_maestro: Optional[str] = None
                        )-> PagedResponse[ArticuloPrecioSchema]:
    
        subquery = (
            self.db.query(func.min(Articulo.id).label("min_id"))
            .group_by(Articulo.codigo)
            .subquery()
        )

        query = self.db.query(ArticuloPrecio).join(Articulo)
        query = query.options(joinedload(ArticuloPrecio.articulo).joinedload(Articulo.articulo_maestro))
        query = query.filter(Articulo.id.in_(subquery.select()))

        if sector_id or familia_id or subfamilia_id:
            query = query.join(Articulo.subfamilia)

        if sector_id:
            query = query.join(SubFamilia.familia)
            query = query.filter(Familia.id_sector == sector_id)

        if familia_id:
            query = query.filter(SubFamilia.id_familia == familia_id)

        if subfamilia_id:
            query = query.filter(Articulo.id_subfamilia == subfamilia_id)
        
        if filtro_codigo_maestro:
            query = query.filter(Articulo.articulo_maestro.has(ArticuloMaestro.codigo.ilike(f"%{filtro_codigo_maestro}%")))

        if filtro_codigo:
            query = query.filter(Articulo.codigo.ilike(f"%{filtro_codigo}%"))

        total_real = query.count()
        items = query.order_by(Articulo.codigo).offset(skip).limit(limit).all()

        items_schema = [ArticuloPrecioSchema.model_validate(item) for item in items]

        return PagedResponse[ArticuloPrecioSchema].crear(
            items=items_schema, 
            total=total_real,
            skip=skip, 
            limit=limit
        )

    # --- LÓGICA DE ARTÍCULO MAESTRO ---

    def bulk_insert_maestros(self, lista_maestros: list[dict]):
        if not lista_maestros:
            return

        from sqlalchemy import insert as sa_insert
        maestros_unicos_excel = {m['codigo']: m for m in lista_maestros}.values()
        codigos_nuevos = {m['codigo'] for m in maestros_unicos_excel}
        
        query_existentes = select(ArticuloMaestro.codigo).where(ArticuloMaestro.codigo.in_(codigos_nuevos))
        existentes = set(self.db.execute(query_existentes).scalars().all())

        maestros_a_insertar = [
            m for m in maestros_unicos_excel if m['codigo'] not in existentes
        ]

        if maestros_a_insertar:
            self.db.execute(sa_insert(ArticuloMaestro), maestros_a_insertar)
            self.db.commit()



    def get_all_maestros(
        self, 
        solo_activos: bool, 
        skip: int = 0, 
        limit: int = 20,
        filtro_codigo: Optional[str] = None,
        id_subfamilia: Optional[int] = None,
        id_familia: Optional[int] = None,
        id_sector: Optional[int] = None
    ) -> tuple[int, list[ArticuloMaestro]]:


        where_conditions = []
        join_intermedia_required = False

        if solo_activos:
            where_conditions.append(ArticuloMaestro.activo == True)

        if filtro_codigo:
            where_conditions.append(ArticuloMaestro.codigo.ilike(f"%{filtro_codigo}%"))

        intermedia_conditions = []
        
        if id_subfamilia:
            join_intermedia_required = True
            intermedia_conditions.append(ArticuloMaestroXArticuloPrecio.subfamilia_id == id_subfamilia)
            
        if id_familia:
            join_intermedia_required = True
            intermedia_conditions.append(
                ArticuloMaestroXArticuloPrecio.subfamilia.has(SubFamilia.id_familia == id_familia)
            )
            
        if id_sector:
            join_intermedia_required = True
            intermedia_conditions.append(
                ArticuloMaestroXArticuloPrecio.subfamilia.has(
                    SubFamilia.familia.has(Familia.id_sector == id_sector)
                )
            )


        count_stmt = select(func.count(func.distinct(ArticuloMaestro.id)))
        
        if join_intermedia_required:
            count_stmt = count_stmt.join(ArticuloMaestro.variantes) # Asumiendo que 'variantes' apunta a la intermedia
            if intermedia_conditions:
                count_stmt = count_stmt.where(*intermedia_conditions)
                
        if where_conditions:
            count_stmt = count_stmt.where(*where_conditions)
            
        total = self.db.execute(count_stmt).scalar() or 0

        stmt = select(ArticuloMaestro)

        if join_intermedia_required:
            stmt = stmt.join(ArticuloMaestro.variantes)
            if intermedia_conditions:
                stmt = stmt.where(*intermedia_conditions)
            
            stmt = stmt.options(contains_eager(ArticuloMaestro.variantes))
        else:
            stmt = stmt.options(joinedload(ArticuloMaestro.variantes))

        if where_conditions:
            stmt = stmt.where(*where_conditions)

        stmt = stmt.offset(skip).limit(limit)

        result = self.db.execute(stmt)
        
        return total, list(result.scalars().unique().all())

    def vincular_maestros_a_articulos(self, mapeo_codigos: List[Dict[str, str]]) -> int:
        count = 0
        for item in mapeo_codigos:
            codigo_maestro = item.get('codigo_maestro')
            codigo_articulo = item.get('codigo_articulo')

            maestro = self.db.query(ArticuloMaestro).filter(ArticuloMaestro.codigo == codigo_maestro).first()
            if maestro:
                res = self.db.query(Articulo).filter(Articulo.codigo == codigo_articulo).update(
                    {Articulo.id_articulo_maestro: maestro.id}, synchronize_session=False
                )
                count += res
        self.db.commit()
        return count

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
        # Modificamos la consulta para incluir ArticuloMaestro en la búsqueda
        sql = text("""
            SELECT 
                am.id, 
                am.codigo, 
                am.descripcion, 
                am.url_foto, 
            FROM ArticuloMaestro am
            WHERE MATCH(am.codigo, am.descripcion) AGAINST(:q IN BOOLEAN MODE)
            GROUP BY am.id -- Agrupamos por am.id para evitar duplicados si un maestro tiene varias variantes con el mismo precio
            ORDER BY MATCH(am.codigo, am.descripcion) AGAINST(:q IN BOOLEAN MODE) DESC
            LIMIT 5
        """)
        
        result = self.db.execute(sql, {"q": query_booleana})
        
        # Mapeamos los resultados al esquema ArticuloSugerencia
        # Asegúrate de que tu tabla 'articulos_precio' y 'articulos_maestro' tengan índices FULLTEXT en 'codigo' y 'descripcion'
        return [ArticuloSugerencia(**row._asdict()) for row in result]
    

from sqlalchemy.orm import Session

from app.models import WebConfig

class WebConfigRepository:
    @staticmethod
    def get_config(db: Session):
        return db.query(WebConfig).first()
    
    @staticmethod
    def get_by_id(db: Session, config_id: int):
        return db.query(WebConfig).filter(WebConfig.id == config_id).first()

    @staticmethod
    def update(db: Session, db_config: WebConfig):
        db.commit()
        db.refresh(db_config)
        return db_config
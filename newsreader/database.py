from typing import Optional, List, Any
import datetime as dt
from sqlmodel import Field, Session, SQLModel, create_engine, select

# ~~~ Database ~~~~~~~~~~~~~~~

class Database:
    def __init__(self, uri: str):
        self.engine = create_engine(uri)
        SQLModel.metadata.create_all(self.engine)

    def create_all(self, items: List[SQLModel]):
        with Session(self.engine) as session:
            for item in items:
                session.add(item)
            session.commit()

    def get_by_id(self, id: str, model: SQLModel):
        with Session(self.engine) as session:
            stmt = select(model).where(model.id == id)
            return session.exec(stmt).first()
    
    def get_by_field(self, key: str, value: Any, model: SQLModel):
        stmt = select(model).where(getattr(model, key) == value)
        print(stmt)
        return self.exec(stmt)
    
    def exec(self, stmt: str):
        with Session(self.engine) as session:
            return session.exec(stmt).all()
    

# ~~~ Models ~~~~~~~~~~~~~~~~~

class Document(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    href: str
    date: dt.datetime
    text: Optional[str] = None
    date_collected: dt.datetime
    collected_by: str

class Paragraph(SQLModel, table=True):
    id: str = Field(primary_key=True)
    text: str
    document_id: str = Field(foreign_key="document.id")
    sentiment: str
    sent_score: float

class EntityMention(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    word: str
    score: float
    label: str
    paragraph_id: str = Field(foreign_key="paragraph.id")
    start: int
    end: int





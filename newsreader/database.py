from re import T
from typing import Optional, Dict, List, Any, Union
import datetime as dt
from sqlmodel import Field, Session, SQLModel, create_engine, select
from threading import Thread
import queue

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

    def get_by_id(self, id: Union[str, int], model: SQLModel):
        with Session(self.engine) as session:
            stmt = select(model).where(model.id == id)
            return session.exec(stmt).first()
    
    def get_by_field(self, key: str, value: Any, model: SQLModel):
        stmt = select(model).where(getattr(model, key) == value)
        print(stmt)
        return self.exec(stmt)
    
    def exec(self, stmt: str, params = {}):
        with Session(self.engine) as session:
            return session.exec(stmt, params=params).all()

class DatabaseWorker(Thread):
    def __init__(self, 
            uri: str,
            queue: queue.Queue, 
            batch: int = None,
            timeout: int = 10
        ):
        super().__init__()
        self.q = queue
        self.db = Database(uri)
        self.timeout = timeout
        self.batch = batch
    
    def run(self):
        while True:
            cache = []
            try:
                cache.append(self.q.get(timeout=self.timeout))
                if self.batch:
                    if len(cache) % self.batch == 0:
                        self.db.create_all(cache)
                        cache = []
                else:
                    self.db.create_all(cache)
                    cache = []
            except queue.Empty:
                break

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

class Entity(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    description: Optional[str]

class EntityMention(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    score: Optional[float]
    label: str
    start: int
    end: int
    paragraph_id: str = Field(foreign_key="paragraph.id")
    kb_id: Optional[str] = Field(foreign_key="entity.id")

class EntityFeature(SQLModel, table=True):
    id: int = Field(primary_key=True)
    kb_id: int = Field(foreign_key="entity.id")
    key: str
    value: str





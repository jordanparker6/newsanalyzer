from threading import Thread
from ..wikidata import Wikidata
from ..database import Database, Entity

class EntityContext(Thread):
    """
    A Thread that collects entity data from wikidata.
    """
    def __init__(self, database: Database):
        self.db = database
        self._wiki = Wikidata()
    
    def run(self):
        while True:
            ents = self.get_new_ents()
            features = self._wiki.get_info(ents.label, ents.id)


    def get_new_ents(self):
        self.db.exec     
# Currently there is an issue with the latest SpaCy and PyDantic
import subprocess
import sys
import multiprocessing as mp
from tqdm import tqdm
import logging
import spacy
from textblob import TextBlob
from ..database import Database, Entity, Paragraph, EntityMention
from .utils import split_paragraphs, get_docs, get_sent_label

log = logging.getLogger(__name__)

THRESHOLD = 0.25
NUM_THREADS = mp.cpu_count()


def add_paragraph_to_db(
        doc_id, 
        i, 
        doc, 
        sent, 
        db: Database
    ):
    output = [
        Paragraph(
            id=f"{doc_id}:{i}",
            text=doc.text,
            sentiment=get_sent_label(sent.polarity),
            sent_score=sent.polarity,
            document_id=doc_id
        )
    ]
    for span in doc.ents:
        output.append(
            EntityMention(
                paragraph_id=f"{doc_id}:{i}",
                text=span.text,
                start=span.start,
                end=span.start + len(span.text),
                kb_id=span.kb_id_,
                label=span.label_,
                score=span._.score
            )
        )
        if span.kb_id_:
            if not db.get_by_id(span.kb_id_, Entity):
                db.create_all([
                    Entity(
                        id=span.kb_id_,
                        name=span._.label[0],
                        description=span._.description
                    )
                ])
    db.create_all(output)

class TextWorker:
    def __init__(self, model: str) -> None:
        super().__init__()
        self.nlp = spacy.load(model)
        self.nlp.add_pipe('opentapioca')
    
    def __call__(self, item):
        idx, i, text = item
        try:
            return (idx, i, list(self.nlp.pipe([text]))[0], TextBlob(text).sentiment)
        except Exception as e:
            log.error(e, extra={ "id": idx, "text": text })
            return None

def analyse(
        database: Database,
        model: str
    ):
    print("NLP Analysis:")
    worker = TextWorker(model)   

    while True:
        docs = get_docs(database)
        if len(docs) == 0:
            break
        for doc in tqdm(docs):
            idx, text = doc
            paragraphs = split_paragraphs(text)
            if len(paragraphs) == 0:
                continue
            items = map(worker, [(idx, *x) for x in enumerate(paragraphs)])
            for item in items:
                if item:
                    add_paragraph_to_db(*item, db=database)



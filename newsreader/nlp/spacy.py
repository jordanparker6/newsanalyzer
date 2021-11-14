from tqdm import tqdm
import logging
import spacy
import urllib3
import time
from queue import Queue
from textblob import TextBlob
from ..database import Database, Entity, EntityFeature, Paragraph, EntityMention
from .utils import split_paragraphs, get_docs, get_sent_label
from ..wikidata import Wikidata

log = logging.getLogger(__name__)

def process_doc(queue, msg):
    idx, text = msg
    paragraphs = split_paragraphs(text)
    if len(paragraphs) == 0:
        return
    items = [(idx, *x) for x in enumerate(paragraphs)]
    for item in items:
        yield item

def process_para(queue, msg, model):
    idx, i, text = msg
    try:
        doc, sent = list(model.pipe([text]))[0], TextBlob(text).sentiment
        try:
            queue.put(Paragraph(
                id=f"{idx}:{i}",
                text=doc.text,
                sentiment=get_sent_label(sent.polarity),
                sent_score=sent.polarity,
                document_id=idx
            ))
        except urllib3.exceptions.ConnectionError as e:
            print("Connection Error... waiting")
            time.sleep(5)
        for span in doc.ents:
            yield (idx, i, span)
    except UnboundLocalError as e:
        print(e)

def process_entity(queue, msg):
    idx, i, span = msg
    queue.put(EntityMention(
        paragraph_id=f"{idx}:{i}",
        text=span.text,
        start=span.start,
        end=span.start + len(span.text),
        kb_id=span.kb_id_,
        label=span.label_,
        score=span._.score
    ))
    if span.kb_id_:
        yield (
            span.label_, 
            span.kb_id_, 
            Entity(
                id=span.kb_id_,
                name=span._.label[0],
                description=span._.description
            )
        )

def enrich_entity(queue, msg):
    type, idx = msg
    wiki = Wikidata()
    if type == "ORG":
        data = wiki.get_organisation_info(idx)
        for d in data:
            for k, v in d.items():
                queue.put(EntityFeature(
                    kb_id=idx,
                    key=k,
                    value=v
                ))
                

def analyse(
        uri: str,
        model: str
    ):
    print("NLP Analysis:")
    queue = Queue()
    nlp = spacy.load(model)
    nlp.add_pipe('opentapioca')
    db = Database(uri)
    docs = get_docs(db)
    if len(docs) == 0:
        return
    #worker = DatabaseWorker(uri, queue, batch=50)
    #worker.start()
    for doc in tqdm(docs):
        for para in process_doc(queue, doc):
            for entmen in process_para(queue, para, nlp):
                for type, idx, ent in process_entity(queue, entmen):
                    if not db.get_by_id(idx, Entity):
                        db.create_all([ent])
                        enrich_entity(queue, (type, idx))
        entries = []
        print("adding a total of", queue.qsize(), "entries")
        for _ in range(queue.qsize()):
            entries.append(queue.get())
        db.create_all(entries)
            

            


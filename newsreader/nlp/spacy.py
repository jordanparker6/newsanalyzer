# Currently there is an issue with the latest SpaCy and PyDantic

from tqdm import tqdm
import logging
import spacy
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from database import Database, Paragraph, EntityMention
from .utils import split_paragraphs

log = logging.getLogger(__name__)

# ~~~~ Utility Processing Methods ~~~~~~~

def split_paragraphs(text: str):
    text = text.replace("\r\n", "\n")
    paragraphs = text.split('\n\n')
    return list(filter(lambda x: len(x) > 0, paragraphs))

def analyse(
        database: Database,
        sent_model: str
    ):
    print("NLP Analysis:")
    # ~~~~ Inititate the Language Model Pipelines ~~~~~~~
    pipe = spacy.load('en_core_web_trf')
    #pipe.add_pipe('coreferee')
    pipe.add_pipe('opentapioca')
    #pipe.add_pipe('spacytextblob')
    sent = pipeline(
        task="sentiment-analysis", 
        model=AutoModelForSequenceClassification.from_pretrained(sent_model),
        tokenizer=AutoTokenizer.from_pretrained(sent_model)
    )

    # ~~~~ Imperative analysis and processing ~~~~~~~
    while True:
        docs = database.exec("""
            SELECT document.id, document.text FROM document
            WHERE NOT EXISTS (SELECT paragraph.id FROM paragraph WHERE document.id = paragraph.document_id)
        """)
        n = len(docs)
        if n == 0:
            break
        for doc in tqdm(docs):
            id, text = doc
            paragraphs = split_paragraphs(text)
            if len(paragraphs) > 0:
                items = zip(pipe(paragraphs), sent(paragraphs))
                results = []
                for j, item in enumerate(items):
                    doc, sentiment = item
                    results.append(
                        Paragraph(
                            id=f"{id}:{j}",
                            text=doc.text,
                            sentiment=sentiment["label"],
                            sent_score=sentiment["score"],
                            document_id=id
                        )
                    )
                    for span in doc.ents:
                        results.append(
                            EntityMention(
                                paragraph_id=f"{id}:{j}",
                                text=span.text,
                                kb_id=span.kb_id,
                                label=span.label_,
                                score=span.score_
                            )
                        )
            database.create_all(results)

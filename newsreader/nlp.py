from tqdm import tqdm
import logging
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification, pipeline
from database import Database, Paragraph, EntityMention

log = logging.getLogger(__name__)

# ~~~~ Utility Processing Methods ~~~~~~~

def split_paragraphs(text: str):
    text = text.replace("\r\n", "\n")
    paragraphs = text.split('\n\n')
    return list(filter(lambda x: len(x) > 0, paragraphs))

def clean_ner_schema(ent):
    ent["label"] = ent["entity_group"]
    ent["text"] = ent["word"]
    del ent["entity_group"]
    del ent["word"]
    return ent

def analyse(
        database: Database, 
        ner_model: str, 
        sent_model: str
    ):
    print("NLP Analysis:")
    # ~~~~ Inititate the Language Model Pipelines ~~~~~~~

    ner = pipeline(
            task="ner", 
            model=AutoModelForTokenClassification.from_pretrained(ner_model),
            tokenizer=AutoTokenizer.from_pretrained(ner_model),
            aggregation_strategy="average"
        )
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
                try:
                    items = zip(
                            paragraphs, 
                            sent(paragraphs), 
                            ner(paragraphs)
                        )
                except Exception as e:
                    log.error(e, extra={ "id": id, "text": text, "paragraphs": paragraphs })
                    continue
                results = []
                for j, item in enumerate(items):
                    results.append(
                        Paragraph(
                            id=f"{id}:{j}",
                            text=item[0],
                            sentiment=item[1]["label"],
                            sent_score=item[1]["score"],
                            document_id=id
                        )
                    )
                    for ent in item[2]:
                        ent = clean_ner_schema(ent)
                        results.append(
                            EntityMention(paragraph_id=f"{id}:{j}", **ent)
                        )
            database.create_all(results)

import config
from database import Database, Paragraph, EntityMention
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification, pipeline

# ~~~~ Inititate the Language Model Pipelines ~~~~~~~

ner = pipeline(
        task="ner", 
        model=AutoModelForTokenClassification.from_pretrained(config.NER_MODEL),
        tokenizer=AutoTokenizer.from_pretrained(config.NER_MODEL),
        aggregation_strategy="average"
    )
sent = pipeline(
        task="sentiment-analysis", 
        model=AutoModelForSequenceClassification.from_pretrained(config.SENT_MODEL),
        tokenizer=AutoTokenizer.from_pretrained(config.SENT_MODEL)
    )

# ~~~~ Utility Processing Methods ~~~~~~~

def split_paragraphs(text: str):
    return text.split('\n\n')

# ~~~~ Imperative analysis and processing ~~~~~~~

def analyse(database: Database):
    print("NLP Analysis:")
    statement = """
        SELECT document.id, document.text FROM document
        WHERE NOT EXISTS (SELECT paragraph.id FROM paragraph WHERE document.id = paragraph.document_id)
    """
    docs = database.exec(statement)
    n = len(docs)
    if n == 0:
        print("Done")
    for i, doc in enumerate(docs):
        id, text = doc
        paragraphs = split_paragraphs(text)
        items = zip(paragraphs, sent(paragraphs), ner(paragraphs))
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
                ent["label"] = ent["entity_group"]
                del ent["entity_group"]
                results.append(
                    EntityMention(paragraph_id=f"{id}:{j}", **ent)
                )
        print("Total Documents:", i + 1, "of", n, end="\r", flush=True)
        database.create_all(results)
    print("NLP Analysis Complete:", i + 1, "of", n, "documents")

if __name__ == "__main__":
    print("starting...")
    database = Database("sqlite:///database.db")
    analyse(database)
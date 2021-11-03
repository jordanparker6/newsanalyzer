from database import Database, Paragraph, EntityMention
import spacy
from transformers import AutoTokenizer, AutoModelForTokenClassification, AutoModelForSequenceClassification, pipeline

# ~~~~ Utility Processing Methods ~~~~~~~

def split_paragraphs(text: str):
    return text.split('\n\n')

def analyse(database: Database, ner_model: str, sent_model: str):
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
        for i, doc in enumerate(docs):
            id, text = doc
            paragraphs = split_paragraphs(text)
            try:
                items = zip(paragraphs, sent(paragraphs), ner(paragraphs))
            except Exception as e:
                print(e)
                print("Data:", id, text, paragraphs)
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
    db = Database("sqlite:///database.db")
    analyse(db, "dslim/bert-base-NER", "finiteautomata/bertweet-base-sentiment-analysis")
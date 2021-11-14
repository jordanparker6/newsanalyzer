from ..database import Database

def split_paragraphs(text: str):
    text = text.replace("\r\n", "\n")
    paragraphs = text.split('\n\n')
    return list(filter(lambda x: len(x) > 0, paragraphs))

def truncate_text(text: str, max_length: int):
    try:
        return text[:max_length]
    except KeyError as e:
        return text

def get_docs(database: Database):
    return database.exec("""
        SELECT document.id, document.text FROM document
        WHERE 
        document.text IS NOT NULL
        AND
        NOT EXISTS (SELECT paragraph.id FROM paragraph WHERE document.id = paragraph.document_id)
    """)

def get_sent_label(score, threshold = 0.25):
    if score > threshold:
        return "POS"
    elif score < -1 * threshold:
        return "NEG"
    else:
        return "NEU"
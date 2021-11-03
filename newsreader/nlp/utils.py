
def split_paragraphs(text: str):
    text = text.replace("\r\n", "\n")
    paragraphs = text.split('\n\n')
    return list(filter(lambda x: len(x) > 0, paragraphs))

def truncate_text(text: str, max_length: int):
    try:
        return text[:max_length]
    except KeyError as e:
        return text
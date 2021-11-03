from questionary import Style, Validator, ValidationError, prompt, print as pprint
from pyfiglet import figlet_format
import datetime as dt
import scrapers

style = Style([
    ('qmark', '#07b05b bold'),                  # token in front of the question
    ('answer', '#00b3ff bold'),                 # submitted answer text behind the question
    ('pointer', '#07b05b bold'),                # pointer used in select and checkbox prompts
    ('highlighted', 'bold'),                    # pointed-at choice in select and checkbox prompts
    ('selected', 'bold noreverse'),                    # style for a selected item of a checkbox
    ('separator', '#cc5454'),                   # separator in lists
    ('instruction', ''),                        # user instructions for select, rawselect, checkbox
    ('text', ''),                               # plain text
    ('disabled', 'fg:#858585 italic')           # disabled choices for select and checkbox prompts
])

# ~~~ CLI Logging Utility ~~~~~~~~~~~~~~~

def log(string, style, font="slant", figlet=False):
    if not figlet:
        pprint(string, style)
    else:
        pprint(figlet_format(
            string, font=font
        ), style)

# ~~~ Validators ~~~~~~~~~~~~~~~

class EmptyValidator(Validator):
    def validate(self, value):
        if len(value.text):
            return True
        else:
            raise ValidationError(
                message="You can't leave this blank",
                cursor_position=len(value.text))

class ISODatetimeValidator(Validator):
    def validate(self, value):
        if isinstance(dt.datetime.fromisoformat(value.text), dt.datetime):
            return True
        else:
            raise ValidationError(
                message="The period to a valid ISO date string",
                cursor_position=len(value.text)
            )

# ~~~ Questions ~~~~~~~~~~~~~~~

def askQuestions(methods):
    cfg = {}
    if "scrapers" in methods:
        cfg["scrapers"] = askScraperInfo()
    if "nlp" in methods:
        cfg["nlp"] = askNLPInfo()
    return cfg

def askDatabaseInfo():
    questions = [
        {
            'type': 'input',
            'name': 'uri',
            'message': 'What is the database URI?',
            'default': "sqlite:///database.db",
            'validate': EmptyValidator
        }
    ]
    answers = prompt(questions, style=style)
    return answers

def askMethodInfo():
    questions = [
        {
            'type': 'checkbox',
            'name': 'methods',
            'message': 'Which features do you wish to run?',
            'choices': [
                { "value": "scrapers", "name": "1) Run Web Scrapers", "checked": True },
                { "value": "nlp", "name": "2) Run NLP Analysis", "checked": True },
                { "value": "dashboard", "name": "3) Serve Dashboard", "checked": False },
            ],
            'validate': lambda answer: 'You must choose at least one operation.' if len(answer) == 0 else True
        }
    ]
    return prompt(questions, style=style)

def askScraperInfo():
    now = dt.date.today()
    scraper_classes = list(map(lambda x: x.__name__, scrapers.ScraperBase.__subclasses__()))
    questions = [
        {
            'type': 'input',
            'name': "period_to",
            'message': "How far back do you wish to scrape?",
            'default': now.replace(year=now.year - 1).isoformat(),
            'validate': ISODatetimeValidator,
        },
        {
            'type': 'checkbox',
            'name': 'classes',
            'message': 'Which scrapers to run?',
            'choices': map(lambda x: { "name": x, "checked": True }, scraper_classes),
            'validate': lambda answer: 'You must choose at least one operation.' if len(answer) == 0 else True
        }
    ]
    return prompt(questions, style=style)

def askNLPInfo():
    questions = [
        {
            'type': 'input',
            'name': "ner",
            'message': "Which Huggingface NER model to use?",
            'default': "dslim/bert-base-NER",
            'validate': EmptyValidator
        },
                {
            'type': 'input',
            'name': "sent",
            'message': "Which Huggingface Sentiment Analysis model to use?",
            'default': "finiteautomata/bertweet-base-sentiment-analysis",
            'validate': EmptyValidator
        }
    ]
    return prompt(questions, style=style)
from PyInquirer import Token, ValidationError, Validator, print_json, prompt, style_from_dict
from pyfiglet import figlet_format
import datetime as dt
try:
    from termcolor import colored
except ImportError:
    colored = None

style = style_from_dict({
    Token.QuestionMark: '#fac731 bold',
    Token.Answer: '#4688f1 bold',
    Token.Instruction: '',  # default
    Token.Separator: '#cc5454',
    Token.Selected: '#0abf5b',  # default
    Token.Pointer: '#673ab7 bold',
    Token.Question: '',
})

# ~~~ CLI Logging Utility ~~~~~~~~~~~~~~~

def log(string, color, font="slant", figlet=False):
    if colored:
        if not figlet:
            print(colored(string, color))
        else:
            print(colored(figlet_format(
                string, font=font), color))
    else:
        print(string)

# ~~~ PyInquirer Validators ~~~~~~~~~~~~~~~

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

# ~~~ PyInquirer Questions ~~~~~~~~~~~~~~~

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
    answers = prompt(questions, style=style)
    return answers

def askScraperInfo():
    now = dt.date.today()
    questions = [
        {
            'type': 'input',
            'name': "period_to",
            'message': "How far back do you wish to scrape?",
            'default': now.replace(year=now.year - 1).isoformat(),
            'validate': ISODatetimeValidator,
        }
    ]
    answers = prompt(questions, style=style)
    return answers

def askNLPInfo():
    questions = [
        {
            'type': 'input',
            'name': "ner",
            'message': "Which Hugginface NER model to use?",
            'default': "dslim/bert-base-NER",
            'validate': EmptyValidator
        },
                {
            'type': 'input',
            'name': "sent",
            'message': "Which Hugginface Sentiment Analysis model to use?",
            'default': "finiteautomata/bertweet-base-sentiment-analysis",
            'validate': EmptyValidator
        }
    ]
    answers = prompt(questions, style=style)
    return answers
import sys
import spacy
import subprocess
from . import dashboard

def install_spacy_required_packages(model: str):
    if not spacy.util.is_package(model):
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model])

def run_streamlit_dashboard(db: str):
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard.__file__, "--", "--database", db], check=True)
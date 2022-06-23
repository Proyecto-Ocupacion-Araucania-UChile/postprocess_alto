import os
import spacy

#contantes
CURRENT = current_dir = os.path.dirname(os.path.abspath(__file__))
XML_NOCLEAN ="transfo/input/"
XML_CLEAN ="transfo/output/"
GROUND_TRUTH = "data/ground_truth/"
IMG = "transfo/img/"
GEO_DICT = "data/dict/diccionario.json"

#spacy
NLP = spacy.load("es_core_news_md")
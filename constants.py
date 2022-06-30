import os
import spacy

#contantes
CURRENT = os.path.dirname(os.path.abspath(__file__))
XML_NOCLEAN = os.path.join(CURRENT, "transfo/input/")
XML_CLEAN = os.path.join(CURRENT, "transfo/output/")
GROUND_TRUTH = os.path.join(CURRENT, "data/ground_truth/")
IMG = os.path.join(CURRENT, "transfo/img/")
GEO_DICT = os.path.join(CURRENT, "data/dict/diccionario.json")
LOGS = os.path.join(CURRENT, "transfo/logs/activity.json")
TXT_LOGS = os.path.join(XML_CLEAN, "activity.txt")

#spacy
NLP = spacy.load("es_core_news_md")
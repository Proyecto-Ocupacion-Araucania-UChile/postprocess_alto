import json
import os

from ..opt.utils import suppress_char
from .parser import ParserXML
from constants import GEO_DICT, NLP, GROUND_TRUTH

def write_text():
    """
    Scraper .txt in ground_truth directory
    keep numbers because its can help to transcribe world. Ex: 1er
    :return:
    """

    lines = []

    with open(os.path.join(GROUND_TRUTH, "DONT_USE.txt"), 'r') as txt:
        list_dontuse = [bad_file for bad_file in txt]

    for root, dirs, files in os.walk(GROUND_TRUTH):
        for directory in dirs:
            for file in os.listdir(os.path.join(GROUND_TRUTH, directory)):
                if file.endswith(".xml") and file not in list_dontuse:
                    xml = ParserXML(os.path.join(GROUND_TRUTH, directory, file))
                    lines = lines + xml.collect()

    with open(os.path.join(GROUND_TRUTH, "data.txt"), 'w') as txt:
        for n, line in enumerate(lines):
            #Clean data
            line = suppress_char(line)
            list_word = []
            for word in line.split():
                list_word.append(word)
                if "xxx" in word :
                    line = line.replace(word, "")
            #management cut words
            if list_word[-1].endswith("-"):
                line = line.replace(list_word[-1], " ")
                next_line = [s for s in lines[n+1].split()]
                if len(next_line) <= 1:
                    lines.remove(lines[n + 1])
                else:
                    lines[n + 1] = lines[n + 1].replace(next_line[0], " ")
            line = line.replace("   ", " ")
            line = line.replace("  ", " ")
            line = line.strip()
            txt.write(line + " ")

def check_geo(word: str):
    word_split = list(word)
    first_letter = word_split[0].upper()

    with open(GEO_DICT, "r") as f:
        file = json.load(f)

        try:
            for name in file[0][first_letter]:
                if word.lower() in [str(w).lower() for w in NLP(name) if w.is_stop is False]:
                    return True
                else:
                    return False
        except KeyError:
            pass
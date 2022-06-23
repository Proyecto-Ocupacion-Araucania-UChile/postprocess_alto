import json
import os

from ..constants import CURRENT, GEO_DICT, NLP

def check_geo(word: str):
    word_split = list(word)
    first_letter = word_split[0].upper()

    with open(os.path.join(CURRENT, GEO_DICT), "r") as f:
        file = json.load(f)

        try:
            for name in file[0][first_letter]:
                if word.lower() in [str(w).lower() for w in NLP(name) if w.is_stop is False]:
                    return True
                else:
                    return False
        except KeyError:
            pass
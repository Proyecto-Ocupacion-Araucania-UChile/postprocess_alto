import json
import os


from tqdm import tqdm
import click
from spellchecker import SpellChecker

from src.opt.click import RequiredOption
from constants import XML_CLEAN, XML_NOCLEAN, GROUND_TRUTH, NLP
from src.opt.utils import cleaning_folder
from src.bin.tools import check_geo, write_text
from src.bin.parser import ParserXML


########Click Run############
@click.command()
@click.option("-t", "--text", "text", is_flag=True, show_default=True, default=False, help="Text generation to do list \
                frequency of data ground truth. option [frequency] is required !")
@click.option("-f", "--frequency", "frequency", is_flag=True, show_default=True, default=False, cls=RequiredOption,
              required_if="text", help="To do list of world frequency of data ground truth")
def word_parsing(frequency, text):
    """
    https://github.com/Anatole-DC/learning_english/blob/master/server/analyses.py
    https://github.com/ElkheirT/Data-Science-Final-Project/blob/main/main.py
    https://github.com/ElkheirT/Data-Science-Final-Project/blob/main/SpellCheck.py
    https://spacy.io/models/es
    https://github.com/andresdtobar/text_classification_GRUNet/blob/main/dictionary_construction.ipynb
    :return:
    """

    #clean dir
    cleaning_folder(XML_CLEAN)

    #variable
    list_files = []

    #init spellchecker
    if frequency:
        if text:
            print("writing data dictionary")
            write_text()
            print("finish !")
        try:
            text_parsing = os.path.join(GROUND_TRUTH, "data.txt")
            spell = SpellChecker(language=None, case_sensitive=True, distance=4)
            spell.word_frequency.load_text_file(text_parsing)
        except FileNotFoundError:
            return print("Data ground truth is not found. You can active option [text] to generate data for dictionary !")
    else:
        spell = SpellChecker(language='es', case_sensitive=True, distance=2)

    #parsing
    for file in os.listdir(XML_NOCLEAN):
        if file.endswith(".xml"):
            xml = ParserXML(os.path.join(XML_NOCLEAN, file))
            print("----" + str(file) + "----")
            for n_line, line in enumerate(tqdm(xml.text)):
                # clean lines
                line_clean = line.replace("  ", " ")
                line_clean = line_clean.replace("   ", " ")
                line_spe = line_clean.replace("⁋", "")

                # doc modele
                doc = NLP(str(line_spe))

                # dict to register modification
                dict_line = {}

                # tokenization
                for token in doc:
                    if token.pos_ != "PUNCT" and token.pos_ != "PROPN":
                        dict_sugg = {
                            "word": str(token),
                            "type": str(token.pos_),
                            "citation": line_clean,
                            "file": str(file),
                            "line": n_line,
                            "corrected": spell.correction(str(token)) if spell.correction(str(token)) != str(
                                token) else None,
                            "probability": spell.word_usage_frequency(str(token)),
                            "suggestions": [sugg for sugg in spell.candidates(str(token))][:-1],
                            "manual": False
                        }

                        # Registering spellchecker
                        if dict_sugg["corrected"] is not None and len(
                                dict_sugg["suggestions"]) <= 1 and "^" not in list(dict_sugg["word"]):
                            dict_line[dict_sugg["word"]] = dict_sugg["corrected"]
                        # Add suggestion dict
                        else:
                            if dict_sugg["corrected"] is not None:
                                list_files.append(dict_sugg)
                    elif token.pos_ == "PROPN":
                        if check_geo(str(token)) is False:
                            dict_sugg = {
                                "word": str(token),
                                "type": str(token.pos_),
                                "citation": line_clean,
                                "file": str(file),
                                "line": n_line,
                                "corrected": spell.correction(str(token)) if spell.correction(str(token)) != str(
                                    token) else None,
                                "probability": spell.word_usage_frequency(str(token)),
                                "suggestions": [sugg for sugg in spell.candidates(str(token))][:-1],
                                "manual": False
                            }

                            # Registering spellchecker
                            if dict_sugg["corrected"] is not None and len(dict_sugg["suggestions"]) <= 1 and "^" not in list(dict_sugg["word"]):
                                dict_line[dict_sugg["word"]] = dict_sugg["corrected"]
                            # Add suggestion dict
                            else:
                                if dict_sugg["corrected"] is not None:
                                    list_files.append(dict_sugg)
                print(dict_line)
                xml.replacer(n_line, dict_line)

            # write new xml
            xml.xml_writer()

    with open(os.path.join(XML_CLEAN, "list_correction.json"), mode="w") as f:
        json.dump(list_files, f, indent=3, ensure_ascii=False)

    print("Finish !")

if __name__ == '__main__':
    word_parsing()

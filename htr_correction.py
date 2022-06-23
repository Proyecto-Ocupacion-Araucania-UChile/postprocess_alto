import json
import os

from tqdm import tqdm
import click
from lxml import etree
from spellchecker import SpellChecker

from src.opt.click import RequiredOption
from src.constants import CURRENT, XML_CLEAN, XML_NOCLEAN, GROUND_TRUTH, NLP
from src.opt.utils import journal_activity, cleaning_folder
from src.bin.data_dict import write_text
from src.bin.ner import check_geo


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

    cleaning_folder(os.path.join(CURRENT, XML_CLEAN))


    list_files = []

    if frequency:
        if text:
            print("writing data dictionary")
            write_text()
            print("finish !")
        try:
            text_parsing = os.path.join(CURRENT, GROUND_TRUTH, "data.txt")
            spell = SpellChecker(language=None, case_sensitive=True, distance=4)
            spell.word_frequency.load_text_file(text_parsing)
        except FileNotFoundError:
            return print("Data ground truth is not found. You can active option [text] to generate data for dictionary !")
    else:
        spell = SpellChecker(language='es', case_sensitive=True, distance=2)

    for file in os.listdir(os.path.join(CURRENT, XML_NOCLEAN)):
        if file.endswith(".xml"):
            with open(os.path.join(CURRENT, XML_NOCLEAN, file), 'r') as f:
                xml = etree.parse(f)
                root = xml.getroot()
                ns = {'alto': "http://www.loc.gov/standards/alto/ns-v4#"}
                text = root.xpath("//alto:String/@CONTENT", namespaces=ns)

                print("----" + str(file) + "----")
                for n_line, line in enumerate(tqdm(text)):
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
                            if dict_sugg["corrected"] is not None and len(dict_sugg["suggestions"]) <= 1 and "^" not in list(dict_sugg["word"]):
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


                    # pour PNOUN geo, regex capture les premieres mots dans dict, si plusieurs resultat utilse la nature en fonction des tokens precedent
                    # faire fonction a part, avec envoie de la ligne, du mot et autres afin d optimiser pour pas boucler
                    if len(dict_line) > 0:
                        for change in dict_line:
                            line_clean = line.replace(change, dict_line[change])
                            journal_activity(XML_CLEAN, "spellchecker", file, n_line, p_word=change, c_word=dict_line[change])
                        element = xml.find(f"//alto:String[@CONTENT='{line}']", namespaces=ns)
                        element.set("CONTENT", line_clean)

                # write new xml
                with open(os.path.join(CURRENT, XML_CLEAN, file), 'wb') as f_write:
                    xml.write(f_write, encoding="utf-8", xml_declaration=True, pretty_print=True)

    with open(os.path.join(XML_CLEAN, "list_correction.json"), mode="w") as f:
        json.dump(list_files, f, indent=3, ensure_ascii=False)

    print("Finish !")

if __name__ == '__main__':
    word_parsing()

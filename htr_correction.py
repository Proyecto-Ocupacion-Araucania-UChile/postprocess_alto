import os
import json

from tqdm import tqdm
import spacy
import click
from lxml import etree
from spellchecker import SpellChecker

from opt.click import RequiredOption

#contantes
current_folder = current_dir = os.path.dirname(os.path.abspath(__file__))
XML_NOCLEAN ="data/xml_no_clean/"
XML_CLEAN ="data/xml_clean/"
GROUND_TRUTH = "data/ground_truth/"

def suppress_char(line):
    punctuation = "!:;\",?’.⁋"
    for sign in punctuation:
        line = line.replace(sign, " ")
    return line

def write_text():
    """
    keep numbers because its can help to transcribe world. Ex: 1er
    :return:
    """

    lines = []

    for root, dirs, files in os.walk(GROUND_TRUTH):
        for directory in dirs:
            for file in os.listdir(os.path.join(GROUND_TRUTH, directory)):
                if file.endswith(".xml"):
                    with open(os.path.join(GROUND_TRUTH, directory, file), 'r') as f:
                        xml = etree.parse(f)
                        ns = {'alto': "http://www.loc.gov/standards/alto/ns-v4#"}
                        text = xml.xpath("//alto:String/@CONTENT", namespaces=ns)
                        for line in text:
                            lines.append(line)
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

def ner_geo(word: str):
    #TODO : remove stop zord ? lower word to normalization ? utiliser systeme comme foncion search app (get key)
    word_split = list(word)
    first_letter = word_split[0].upper()

    with open(os.path.join(current_folder, "dict/diccionario.json"), "r") as f:
        file = json.load(f)

        try:
            for name in file[0][first_letter]:
                if word in [w for w in name.split()]:
                    return True
                else:
                    return False
        except KeyError:
            pass


def journal_activity(path, file, n, p_word, c_word):
    """
    Journal logs to recover all actions to change text and people can verify it !
    :param path: str, path to folder
    :param file: str, name file
    :param n: int, line number
    :param p_word: str, word pre correction
    :param c_word: str, zord post correction
    :return: None
    """

    if os.path.isfile(f"{path}/logs.txt"):
        with open(f"{path}/logs.txt", "a") as f:
            f.write(f"action: {file}, l.{n} -> {p_word} change to {c_word}")
            f.write("\n")
    else:
        with open(f"{path}/logs.txt", "a") as f:
            f.write(f"action: {file}, l.{n} -> {p_word} change to {c_word}")
            f.write("\n")



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

    list_files = []

    nlp = spacy.load("es_core_news_md") #peut regarder le pos_ et si cést nom prop pon peut faire un if psecial pour tcheck dans un dico

    if frequency:
        if text:
            print("writing data dictionary")
            write_text()
            print("finish !")
        try:
            text_parsing = os.path.join(current_folder, GROUND_TRUTH, "data.txt")
            spell = SpellChecker(language=None, case_sensitive=True, distance=4)
            spell.word_frequency.load_text_file(text_parsing)
        except FileNotFoundError:
            return print("Data ground truth is not found. You can active option [text] to generate data for dictionary !")
    else:
        spell = SpellChecker(language='es', case_sensitive=True, distance=2)

    for file in os.listdir(os.path.join(current_folder, XML_NOCLEAN)):
        with open(os.path.join(current_folder, XML_NOCLEAN, file), 'r') as f:
            xml = etree.parse(f)
            root = xml.getroot()
            ns = {'alto': "http://www.loc.gov/standards/alto/ns-v4#"}
            text = root.xpath("//alto:String/@CONTENT", namespaces=ns)

            print("----" + file + "----")
            for n_line, line in enumerate(tqdm(text)):
                # clean lines
                line_clean = line.replace("  ", " ")
                line_clean = line_clean.replace("   ", " ")
                line_spe = line_clean.replace("⁋", "")

                # doc modele
                doc = nlp(str(line_spe))

                # dict to register modification
                dict_line = {}

                # tokenization
                for token in doc:
                    if token.pos_ != "PUNCT" and token.pos_ != "PROPN":
                        dict_sugg = {
                            "word": str(token),
                            "type": str(token.pos_),
                            "location": str(file) + ", line : " + str(n_line),
                            "corrected": spell.correction(str(token)) if spell.correction(str(token)) != str(
                                token) else None,
                            "probability": spell.word_usage_frequency(str(token)),
                            "suggestions": [sugg for sugg in spell.candidates(str(token))][:-1]
                        }

                        # Registering spellchecker
                        if dict_sugg["corrected"] is not None and dict_sugg["suggestions"] is None:
                            dict_line[dict_sugg["word"]] = dict_sugg["corrected"]
                        # Add suggestion dict
                        else:
                            if dict_sugg["corrected"] is not None:
                                list_files.append(dict_sugg)
                    elif token.pos_ == "PROPN":
                        if ner_geo(str(token)) is False:
                            dict_sugg = {
                                "word": str(token),
                                "type": str(token.pos_),
                                "location": str(file) + ", line : " + str(n_line),
                                "corrected": spell.correction(str(token)) if spell.correction(str(token)) != str(
                                    token) else None,
                                "probability": spell.word_usage_frequency(str(token)),
                                "suggestions": [sugg for sugg in spell.candidates(str(token))][:-1]
                            }

                            # Registering spellchecker
                            if dict_sugg["corrected"] is not None and dict_sugg["suggestions"] is None:
                                dict_line[dict_sugg["word"]] = dict_sugg["corrected"]
                            # Add suggestion dict
                            else:
                                if dict_sugg["corrected"] is not None:
                                    list_files.append(dict_sugg)


                # pour PNOUN geo, regex capture les premieres mots dans dict, si plusieurs resultat utilse la nature en fonction des tokens precedent
                # faire fonction a part, avec envoie de la ligne, du mot et autres afin d optimiser pour pas boucler
                if len(dict_line) > 0:
                    for change in dict_line:
                        print(change)
                        line_clean = line.replace(change, dict_line[change])
                        journal_activity(XML_CLEAN, file, n_line, p_word=change, c_word=dict_line[change])
                    element = xml.find(f"//alto:String[@CONTENT='{line}']", namespaces=ns)
                    element.set("CONTENT", line_clean)

            # write new csv
            with open(os.path.join(current_folder, XML_CLEAN, file), 'wb') as f_write:
                xml.write(f_write, encoding="utf-8", xml_declaration=True, pretty_print=True)

    with open(os.path.join(XML_CLEAN, "list_correction.json"), mode="w") as f:
        json.dump(list_files, f, indent=3, ensure_ascii=False)

if __name__ == '__main__':
    word_parsing()

import json
import os

import click
from lxml import etree
from PIL import Image

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

current_folder = current_dir = os.path.dirname(os.path.abspath(__file__))
XML_CLEAN ="data/output/"
IMG = "data/img"


def replacing(file, word_error, word_corrected, n):
    with open(os.path.join(current_folder, XML_CLEAN, file), 'w', encoding='utf-8') as f:
        xml = etree.parse(f)
        root = xml.getroot()
        ns = {'alto': "http://www.loc.gov/standards/alto/ns-v4#"}
        text = root.xpath("//alto:String/@CONTENT", namespaces=ns)
        for n_line, line in enumerate(text):
            if n == n_line:
                tokens = line.split()
                tokens = list(map(lambda x: x.replace(word_error, word_corrected), tokens))
                line_clean = ' '.join(tokens)
                element = xml.find(f"//alto:String[@CONTENT='{line}']", namespaces=ns)
                element.set("CONTENT", line_clean)
        xml.write(f, encoding="utf-8", xml_declaration=True, pretty_print=True)


def modify_prompt(element, security):
        print(element["citation"].replace(element["word"], "<--" + element["word"] + "-->"))
        print("Proposal : " + element["corrected"])
        information = input('Is the proposal correct ? [Y/N/info] : ')
        if information == "Y" or information == "y":
            return element["word"], element["corrected"]
        elif information == "N" or information == "n":
            corr = input('Correction : ')
            corr = corr.strip()
            if security is True:
                secu = input(f"""Are you sure to change f"{element["word"]}" by \"{str(corr)}\" ? [Y/N] : """)
                if secu == "Y" or secu == "y":
                    return element["word"], corr
                elif secu == "N" or secu == "n":
                    return modify_prompt(element, security)
            else:
                return element["word"], corr
        elif information == "info":
            p_json = json.dumps(element, indent=4, sort_keys=True)
            print(highlight(p_json, JsonLexer(), TerminalFormatter()))
            return modify_prompt(element, security)
        else:
            return modify_prompt(element, security)


@click.command()
@click.option("-i", "--image", "image", is_flag=True, show_default=True, default=False, help="To appear jpg associated in folder \"img\"")
@click.option("-s", "--security", "security", is_flag=True, show_default=True, default=False, help="Security confirmation to execute the change")
def correction(image, security):

    global img

    if security:
        security = True
    else:
        security = False

    with open(os.path.join(current_folder, XML_CLEAN, 'list_correction.json')) as json_file:
        data_corr = json.load(json_file)

    for file in os.listdir(os.path.join(current_folder, XML_CLEAN)):
        if file.endswith(".xml"):
            if image:
                try:
                    img = Image.open(os.path.join(current_folder, IMG, file.replace(".xml", ".jpg")))
                    img.show()
                except FileNotFoundError:
                    print("Img directory don't contain the image associated")
                    break
            for element in data_corr:
                if element["file"] == file and element["manual"] is False:
                    corr = modify_prompt(element, security)
                    replacing(file, corr[0], corr[1], element["line"])
                    element["manual"] = True
            if image:
                img.close()

if __name__ == '__main__':
    correction()
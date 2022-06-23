import json
import os

import click
from PIL import Image

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter

from constants import XML_CLEAN, IMG
from src.bin.parser import ParserXML

def prompt(element, security):
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
                    return prompt(element, security)
            else:
                return element["word"], corr
        elif information == "info":
            p_json = json.dumps(element, indent=4, sort_keys=True)
            print(highlight(p_json, JsonLexer(), TerminalFormatter()))
            return prompt(element, security)
        else:
            return prompt(element, security)


@click.command()
@click.option("-i", "--image", "image", is_flag=True, show_default=True, default=False, help="To appear jpg associated in folder \"img\"")
@click.option("-s", "--security", "security", is_flag=True, show_default=True, default=False, help="Security confirmation to execute the change")
def correction(image, security):

    global img

    with open(os.path.join(XML_CLEAN, 'list_correction.json')) as json_file:
        data_corr = json.load(json_file)

    for file in os.listdir(XML_CLEAN):
        if file.endswith(".xml"):
            with open(os.path.join(XML_CLEAN, file), mode='w') as f:
                xml = ParserXML(f)
                if image:
                    try:
                        img = Image.open(os.path.join(IMG, file.replace(".xml", ".jpg")))
                        img.show()
                    except FileNotFoundError:
                        print("Img directory don't contain the image associated")
                        break
                for element in data_corr:
                    if element["file"] == file and element["manual"] is False:
                        corr = prompt(element, security)
                        xml.replacer(element["line"], corr[0], corr[1])
                        element["manual"] = True
                if image:
                    img.close()

if __name__ == '__main__':
    correction()
import json
import os

import click
from PIL import Image

from constants import XML_CLEAN, IMG
from src.bin.parser import ParserXML
from src.bin.terminal import prompt


@click.command()
@click.option("-i", "--image", "image", is_flag=True, show_default=True, default=False,
              help="To appear jpg associated in folder \"img\"")
@click.option("-s", "--security", "security", is_flag=True, show_default=True, default=False,
              help="Security confirmation to execute the change")
def correction(image, security):
    """
    Cli function to do correction in mode manually. The function open json where data ambigus spe
    :param image: Boolean, to activate image screen
    :param security: Boolean, to activate confirmation mode of changement
    :return: None
    """
    global img

    # Open json correction missed
    with open(os.path.join(XML_CLEAN, 'list_correction.json')) as json_file:
        data_corr = json.load(json_file)
        print("There are " + str(len([element["manual"] for element in data_corr])) + " items left to correct")

    # File iteration
    for file in os.listdir(XML_CLEAN):
        if file.endswith(".xml"):
            #instanciation Parser
            xml = ParserXML(file=os.path.join(XML_CLEAN, file), mode="r+")
            # Print jpg
            if image:
                try:
                    img = Image.open(os.path.join(IMG, file.replace(".xml", ".jpg")))
                    img.show()
                except FileNotFoundError:
                    print("Img directory don't contain the image associated")
                    break
            #order json by file and line number
            data_corr.sort(key=lambda x: (x['file'], x['line']))

            line_prev = None

            for element in data_corr:
                if element["file"] == file and element["manual"] is False:
                    dict_line = {}
                    if line_prev == element["line"]:
                        corr = prompt(element, security)
                        dict_line[corr[0]] = corr[1]
                    elif line_prev is None:
                        corr = prompt(element, security)
                        dict_line[corr[0]] = corr[1]
                        line_prev = element["line"]
                    else:
                        xml.replacer(line_prev, dict_line)
                        line_prev = element["line"]
                    element["manual"] = True
                    with open(os.path.join(XML_CLEAN, 'list_correction.json'), "w") as json_write:
                        json.dump(data_corr, json_write, indent=3, ensure_ascii=False)
                xml.replacer()xml_writer
            if image:
                img.close()
        # Verify if all corrections are done
        #if all([element["manual"] for element in data_corr]):
            print("Correction is finished")
            #break


if __name__ == '__main__':
    correction()

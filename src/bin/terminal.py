import json

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


def prompt(element: dict, security: bool):
    print(element["citation"].replace(element["word"], "<--" + element["word"] + "-->"))
    print("Proposal : " + element["corrected"])
    information = input('Is the proposal correct ? [Y/N/info] : ')
    if information == "Y" or information == "y":
        return element["word"], element["corrected"]
    elif information == "N" or information == "n":
        corr = input('Correction : ')
        corr = corr.strip()
        if security is True:
            secu = input(f"""Are you sure to change "{element["word"]}" by \"{str(corr)}\" ? [Y/N] : """)
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

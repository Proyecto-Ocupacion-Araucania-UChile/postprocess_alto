import os
import shutil

from constants import LOGS, TXT_LOGS
from ..bin.parser import ParserXML


def suppress_char(line):
    """
    Function to remove special characters
    :param line: str, line to need cleanup
    :return: str, line
    """
    punctuation = "!:;\",?’.⁋"
    for sign in punctuation:
        line = line.replace(sign, " ")
    return line


def cleaning_folder(path):
    """
    clean folder
    :param path:
    :return: None
    """
    for filename in os.listdir(path):
        if filename != "readme.md":
            file_path = os.path.join(path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))


class Journal(ParserXML):
    action = ["automatic", "manuel"]
    json_dir = LOGS
    txt_dir = TXT_LOGS

    def __init__(self, n_line, correction, file):
        super().__init__(file)
        self.n_line = n_line
        self.correction = correction

    def export_text(self, line: str):
        """
        Journal logs to recover all actions to change text and people can verify it !
        :return: None
        """

        if os.path.isfile(self.txt_dir):
            with open(self.txt_dir, "a") as f:
                for change in self.correction:
                    f.write(f"""{self.action[0] if self.mode == "r" else self.action[1]}: {self.filename}, \
                    l.{self.n_line} -> {change} change to {self.correction[change]} \n\t"{line}" """)
                    f.write("\n")
        else:
            with open(self.txt_dir, "w") as f:
                for change in self.correction:
                    f.write(f"""{self.action[0] if self.mode == "r" else self.action[1]}: {self.filename}, \
                    l.{self.n_line} -> {change} change to {self.correction[change]} \n\tline original : "{line}" """)
                    f.write("\n")

    def export_json(self):
        asset = {
            "action": self.action[0] if self.mode == "r" else self.action[1],
            "filename": self.filename,
            "n_line": self.n_line,
            "word_error": [element for element in self.correction.keys],
            "word_correction": [element for element in self.correction.values]
        }

        if os.path.isfile(self.txt_dir):
            with open(self.txt_dir, "a") as f:



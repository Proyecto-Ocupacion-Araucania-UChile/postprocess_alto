from lxml import etree
import os
import json
import datetime

from constants import XML_CLEAN, LOGS, TXT_LOGS


class ParserXML(object):
    ns = {'alto': "http://www.loc.gov/standards/alto/ns-v4#"}

    def __init__(self, file, encode="utf-8", mode="r"):
        self.file = file
        self.encode = encode
        self.mode = mode
        self.filename = ParserXML._filename_(self)
        self.xml = ParserXML._opener_(self)
        self.root = self.xml.getroot()
        self.text = self.root.xpath("//alto:String/@CONTENT", namespaces=self.ns)

    def __repr__(self):
        return f'ParserXML("{self.filename}","{self.encode}","{self.ns}","{self.mode}")'

    def __str__(self):
        return f'({self.filename},{self.encode},{self.ns},{self.mode})'

    def _opener_(self):
        with open(self.file, mode=self.mode, encoding=self.encode) as f:
            xml = etree.parse(f)
        return xml

    def _filename_(self) -> str:
        return str(os.path.basename(self.file))

    def collect(self) -> list:
        return [line for line in self.text]

    def replacer(self, n, word: dict):
        for n_line, line in enumerate(self.text):
            ex_line = line
            if n == n_line:
                for change in word:
                    tokens = list(map(lambda x: x.replace(change, word[change]), line.split()))
                    line = ' '.join(tokens)
                    if line[0] == '⁋':
                        list_line = list(line)
                        list_line[1] = list_line[1].upper()
                        line = ''.join(list_line)
                    print(line)
                element = self.xml.find(f"//alto:String[@CONTENT='{ex_line}']", namespaces=self.ns)
                element.set("CONTENT", line)
                #Register
                journal = Journal(n_line=n_line, correction=word, file=self.file)
                journal.export_text(ex_line)
                journal.export_json()

    def xml_writer(self, mode='wb'):
        if self.mode == "r":
            print("hello")
            with open(os.path.join(XML_CLEAN, self.filename), mode) as f_write:
                self.xml.write(f_write, encoding=self.encode, xml_declaration=True, pretty_print=True)
        else:
            self.xml.write(self.filename, encoding=self.encode, xml_declaration=True, pretty_print=True)


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
                    f.write(f"""{self.action[0] if self.mode == "r" else self.action[1]}: {self.filename}, l.{self.n_line} -> {change} change to {self.correction[change]} \n\t"{line}" """)
                    f.write("\n")
        else:
            with open(self.txt_dir, "w") as f:
                for change in self.correction:
                    f.write(f"""{self.action[0] if self.mode == "r" else self.action[1]}: {self.filename}, l.{self.n_line} -> {change} change to {self.correction[change]} \n\tline original : "{line}" """)
                    f.write("\n")

    def export_json(self):
        asset = {
            "date": str(datetime.datetime.now()),
            "action": self.action[0] if self.mode == "r" else self.action[1],
            "n_line": self.n_line,
            "word_error": [element for element in self.correction],
            "word_correction": [self.correction[element] for element in self.correction]
        }

        if os.path.isfile(self.json_dir):
            with open(self.json_dir, "r", encoding="utf-8") as f:
                data = json.load(f)
                if self.filename in data:
                    data[self.filename] = data[self.filename] + [asset]
                else:
                    data[self.filename] = [asset]
            with open(self.json_dir, "w", encoding="utf-8") as f_write:
                json.dump(data, f_write, indent=3, ensure_ascii=False)
        else:
            with open(self.json_dir, "w", encoding="utf-8") as f:
                json.dump({self.filename: [asset]}, f, indent=3, ensure_ascii=False)

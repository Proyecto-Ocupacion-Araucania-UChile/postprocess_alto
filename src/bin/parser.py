from lxml import etree
import os

from constants import XML_CLEAN

from ..opt.utils import journal_activity


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
        with open(self.file, mode=self.mode, encoding=self.encode) as f:
            filename = f.name
        return filename

    def collect(self) -> list:
        return [line for line in self.text]

    def replacer(self, n, word: dict):
        for n_line, line in enumerate(self.text):
            ex_line = line
            if n == n_line:
                for change in word:
                    tokens = list(map(lambda x: x.replace(change, word["change"]), line.split()))
                    line = ' '.join(tokens)
                element = self.xml.find(f"//alto:String[@CONTENT='{line}']", namespaces=self.ns)
                element.set("CONTENT", line)

    def xml_writer(self, mode='wb'):
        if self.mode == "r":
            with open(os.path.join(XML_CLEAN, self.filename), mode) as f_write:
                self.xml.write(f_write, encoding=self.encode, xml_declaration=True, pretty_print=True)
        else:
            self.xml.write(self.filename, encoding=self.encode, xml_declaration=True, pretty_print=True)

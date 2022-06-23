from lxml import etree
import os

from constants import XML_CLEAN


class ParserXML:
    ns = {'alto': "http://www.loc.gov/standards/alto/ns-v4#"}

    def __init__(self, file, encode="utf-8"):
        self.encode = encode
        self.mode = file.mode
        self.filename = file.name
        self.xml = etree.parse(file)
        self.root = self.xml.getroot()
        self.text = self.root.xpath("//alto:String/@CONTENT", namespaces=self.ns)

    def __repr__(self):
        return f'ParserXML("{self.filename}","{self.encode}","{self.ns}","{self.mode}")'

    def __str__(self):
        return f'({self.filename},{self.encode},{self.ns},{self.mode})'

    def replacer(self, n, word_error, word_corrected):
        for n_line, line in enumerate(self.text):
            if n == n_line:
                tokens = line.split()
                tokens = list(map(lambda x: x.replace(word_error, word_corrected), tokens))
                line_clean = ' '.join(tokens)
                element = self.xml.find(f"//alto:String[@CONTENT='{line}']", namespaces=ParserXML.ns)
                element.set("CONTENT", line_clean)

    def xml_writer(self, mode='wb'):
        if self.mode == "r":
            with open(os.path.join(XML_CLEAN, self.filename), mode) as f_write:
                self.xml.write(f_write, encoding=self.encode, xml_declaration=True, pretty_print=True)
        else:
            self.xml.write(self.filename, encoding=self.encode, xml_declaration=True, pretty_print=True)

# Spellchecker XML-ALTO

## Summary

CLI to automatically correct the spelling in XML-ALTO files in `input/` . The correction is based on the Levenshtein distance and the PySpellChecker library. The proper names (geographical) are checked in the file `diccionario.json`.

`htr_correction.py` : automatic correction. The `-t` option allows to create a text file from the present ground `data/ground_truth/` and the `-f` option allows to execute the correction from the ground data

`manual_corr.py` : manual correction CLI. It is possible to display an image with the `-i` option, and to activate a confirmation system with the `-s` option. Some bugs are still present, it is advised to be careful

All the corrections made are listed in the logs folder in JSON format. The temporary data are directly present with the corrected files in `output/`.

## Tree

```
Project
|
├── data
│   ├── dict
│   │   └── diccionario.json
│   └── ground_truth
|
├── constants.py
├── htr_correction.py
├── manual_corr.py
├── requirements.txt
|
|
├── src
│   ├── __init__.py
|   |
│   ├── bin
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   ├── terminal.py
│   │   └── tools.py
|   |
│   ├── opt
│      ├── click.py
│      ├── __init__.py
│      └── utils.py
|
|
└── transfo
    ├── img
    ├── input
    ├── logs
    │   ├── activity.json
    └── output
        ├── activity.txt
        ├── list_correction.json
 ```


## App
PySpellCheker : https://github.com/barrust/pyspellchecker
Spacy : https://github.com/explosion/spaCy

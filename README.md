# ocrd-page-to-alto

> Convert PAGE (v. 2019) to ALTO (v. 2.0 - 4.2)

[![image](https://circleci.com/gh/kba/page-to-alto.svg?style=svg)](https://circleci.com/gh/kba/page-to-alto)


## Introduction

This software converts PAGE XML files to the ALTO XML OCR result format. It
enables using PAGE XML generating software in a context where ALTO is needed
to display the results, i.e. in libraries.

## Installation

In a Python virtualenv:
```
make install     # or pip install .
```

## Usage

To convert the PAGE XML document `example.xml` to ALTO:
```
page-to-alto example.xml > example.alto.xml
```

To process an OCR-D workspace, use
[ocrd_fileformat](https://github.com/OCR-D/ocrd_fileformat):
```
ocrd-fileformat-transform -I OCRD-OCR-OUTPUT-PAGE -O OCRD-OCR-OUTPUT-ALTO
```


## TODO

* [ ] AlternativeImage
* [ ] unmappable regions
* [x] handle Border
* [x] TextStyle
* [x] ParagraphStyle
* [x] table regions
* [ ] recursive regions for *Region
* [x] Set `PAGECLASS` from `pc:Page/@type` #4
* [ ] Layers / z-level via `StructureTag`? #4
* [x] `<SP/>`
* [ ] `<HYP/>`
* [ ] rotation
* [x] reading order
* [x] input PAGE-XML not having words #5
* [x] multiple pc:TextEquivs
* [x] language
* [X] ~~script~~ no equivalent in ALTO :(
* [X] ~~kerning~~ no equivalent in ALTO :(
* [X] ~~underlineStyle~~ no equivalent in ALTO :(
* [X] ~~bgColour~~ no equivalent in ALTO :(
* [X] ~~bgColourRgb~~ no equivalent in ALTO :(
* [X] ~~reverseVideo~~ no equivalent in ALTO :(
* [X] ~~xHeight~~ no equivalent in ALTO :(
* [X] ~~letterSpaced~~ no equivalent in ALTO :(
* [x] ProcessingStep
* [x] differentiate/select ALTO versions

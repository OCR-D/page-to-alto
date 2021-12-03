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
# or to install from PyPI
pip install ocrd_page_to_alto
```

## Usage

To convert the PAGE XML document `example.xml` to ALTO:

    page-to-alto example.xml > example.alto.xml

You can get an exhaustive list of page-to-alto's many options with `--help`:
<details><summary>CLI</summary>
<p>
<pre>
Usage: page-to-alto [OPTIONS] FILENAME
  Convert PAGE to ALTO
Options:
  -l, --log-level [OFF|ERROR|WARN|INFO|DEBUG|TRACE]
                                  Log level
  --alto-version [4.2|4.1|4.0|3.1|3.0|2.1|2.0]
                                  Choose version of ALTO-XML schema to produce
                                  (older versions may not preserve all
                                  features)
  --check-words / --no-check-words
                                  Check whether PAGE-XML contains any Words
                                  and fail if not
  --check-border / --no-check-border
                                  Check whether PAGE-XML contains Border or
                                  PrintSpace
  --skip-empty-lines / --no-skip-empty-lines
                                  Whether to omit or keep empty lines in PAGE-
                                  XML
  --trailing-dash-to-hyp / --no-trailing-dash-to-hyp
                                  Whether to add a <HYP/> element if the last
                                  word in a line ends in "-"
  --dummy-textline / --no-dummy-textline
                                  Whether to create a TextLine for regions
                                  that have TextEquiv/Unicode but no TextLine
  --dummy-word / --no-dummy-word  Whether to create a Word for TextLine that
                                  have TextEquiv/Unicode but no Word
  --textequiv-index INTEGER       If multiple textequiv, use the n-th
                                  TextEquiv by @index
  --textequiv-fallback-strategy [raise|first|last]
                                  What to do if nth textequiv isn't available.
                                  'raise' will lead to a runtime error,
                                  'first' will use the first TextEquiv, 'last'
                                  will use the last TextEquiv on the element
  -O, --output-file FILE          Output filename (or "-" for standard output,
                                  the default)
  -h, --help                      Show this message and exit.
</pre>
</p>
</details>

To process an OCR-D workspace, use
[ocrd_fileformat](https://github.com/OCR-D/ocrd_fileformat), which uses
page-to-alto by default:
```
ocrd-fileformat-transform -I OCRD-OCR-OUTPUT-PAGE -O OCRD-OCR-OUTPUT-ALTO \
  -P script-args "--dummy-word --no-check-words --no-check-border"
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
* [X] `<HYP/>`
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

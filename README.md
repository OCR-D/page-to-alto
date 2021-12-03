# ocrd-page-to-alto

> Convert PAGE (v. 2019) to ALTO (v. 2.0 - 4.2)

[![image](https://circleci.com/gh/kba/page-to-alto.svg?style=svg)](https://circleci.com/gh/kba/page-to-alto)

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

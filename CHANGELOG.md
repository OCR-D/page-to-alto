Change Log
==========

Versioned according to [Semantic Versioning](http://semver.org/).

## Unreleased

## [2.2.10] - 2026-06-05

Changed:

  * Update docker base image to OCR-D/core v3.13.0

## [2.2.9] - 2026-05-05

Fixed:

  * PyPI CD: use python 3.9 for now

## [2.2.8] - 2026-05-05

Changed:

  * Cleaned up Docker and PyPI CD

## [2.2.7] - 2026-05-05

Changed:

  * Update docker base image to OCR-D/core v3.13.0

## [2.2.6] - 2026-05-05

Fixed:

  * Docker CD: Typo (debug sleep stmt instead of docker push)

## [2.2.5] - 2026-05-05

Fixed:

  * Docker CD: Typo (extra semicolon)

## [2.2.4] - 2026-05-05

Fixed:

  * Docker CD: Typo {,docker}-smoke-test

## [2.2.3] - 2026-05-05

Fixed:

  * Docker CD: Run smoke test on versioned image too
  * Docker CD: cannot use docker push in parallel directly

## [2.2.2] - 2026-05-05

Fixed:

  * Docker CD: Push the git-tag-versioned images instead of `latest`

## [2.2.1] - 2026-05-05

Fixed:

  * Dockerfile had a typo (missing `v` in front of `3.12.3`)

## [2.2.0] - 2026-05-05

Changed:

  * Propagate coordinates down from `TextLine` to `String` for empty lines, #49
  * Docker image now based on OCR-D/core 3.12.3
  * Docker releases now tagged by version if possible

## [2.1.0] - 2025-05-06

Changed:

  * `make docker`: Overrideable `$(DOCKER)` command and base on `latest` OCR-D/core, #48

## [2.0.1] - 2025-04-17

Fixed:

  * Assertion on `self.parameter` being a `dict` was too strict (it's a `frozendict`), #47

## [2.0.0] - 2025-04-16

Changed:

  * :fire: convert OCR-D processor to v3 API, #40

## [1.5.0] - 2025-03-04

Fixed:

  * text from table regions only converted once, #45
  * empty lines no longer lead to text loss when `--skip-empty-lines` option is set, #45
  * langcodes dependency for Python <= 3.8 version-pinned, #45

Changed:

  * `--no-check-border` is now the default, enable check explicitly with `--check-border`, #45
  * set proper `steps` in `ocrd-tool.json` (`postprocessing/format-conversion`), OCR-D/spec#261

## [1.4.1] - 2024-10-10

Fixed:

  - Dockerfile un-broken after switch to src-layout

## [1.4.0] - 2024-10-10

Added:

  - OCR-D processor `ocrd-page2alto-transform` as a faster way for PAGE-ALTO conversion than ocrd_fileformat, #42
  - Dockerfile and `make docker` command, #41

Changed:

  - Converted codebase to src-layout and replace `setup.py` with `pyproject.toml`, #42

## [1.3.0] - 2024-01-11

Added:

  * support for `alto:processingDateTime` mapped from `pc:Created` or `pc:LastChange`, #36, #37

## [1.2.0] - 2022-09-13

Changed:

  * `--textequiv-fallback-strategy`: default to `first`, not `last`, #32
  * `--textequiv-index` now properly respected, #31, #32

Added:

  * `--textline-order` option to allow iterating `pc:TextLine` in document or `@index` order, #2, #29

## [1.1.0] - 2022-02-01

Added:

  * Add `¬` as a potential hyphenation character, #24
  * Add "&shy;" (soft hyphen) as a potential hyphenation character, #26
  * Optionally output ALTO according to `pc:ReadingOrder`, #27

Fixed:

  * Create `alto:Printspace` after `alto:*Margin`, #22, #23
  * Properly handle all cases for print space, border and margin, #28

## [1.0.1] - 2021-11-09

Fixed:

  * forgot to update setup.py

## [1.0.0] - 2021-11-09

Initial release

<!-- link-labels -->
[2.2.10]: ../../compare/v2.2.10...v2.2.9
[2.2.9]: ../../compare/v2.2.9...v2.2.8
[2.2.8]: ../../compare/v2.2.8...v2.2.7
[2.2.7]: ../../compare/v2.2.7...v2.2.6
[2.2.6]: ../../compare/v2.2.6...v2.2.5
[2.2.5]: ../../compare/v2.2.5...v2.2.4
[2.2.4]: ../../compare/v2.2.4...v2.2.3
[2.2.3]: ../../compare/v2.2.3...v2.2.2
[2.2.2]: ../../compare/v2.2.2...v2.2.1
[2.2.1]: ../../compare/v2.2.1...v2.2.0
[2.2.0]: ../../compare/v2.2.0...v2.1.0
[2.1.0]: ../../compare/v2.1.0...v2.0.1
[2.0.1]: ../../compare/v2.0.1...v2.0.0
[2.0.0]: ../../compare/v2.0.0...v1.5.0
[1.5.0]: ../../compare/v1.5.0...v1.4.1
[1.4.1]: ../../compare/v1.4.1...v1.4.0
[1.4.0]: ../../compare/v1.4.0...v1.3.0
[1.3.0]: ../../compare/v1.3.0...v1.2.0
[1.2.0]: ../../compare/v1.2.0...v1.1.0
[1.1.0]: ../../compare/v1.1.0...v1.0.1
[1.0.1]: ../../compare/v1.0.1...v1.0.0
[1.0.0]: ../../compare/HEAD...v1.0.`0

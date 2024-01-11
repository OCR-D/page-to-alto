Change Log
==========

Versioned according to [Semantic Versioning](http://semver.org/).

## Unreleased

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
[1.3.0]: ../../compare/v1.3.0...v1.2.0
[1.2.0]: ../../compare/v1.2.0...v1.1.0
[1.1.0]: ../../compare/v1.1.0...v1.0.1
[1.0.1]: ../../compare/v1.0.1...v1.0.0
[1.0.0]: ../../compare/HEAD...v1.0.0

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Upgraded [sqlglot](https://github.com/tobymao/sqlglot) to versions >= 13.0.0 ([#1642](https://github.com/moj-analytical-services/splink/pull/1642))
- Improved logging output from settings validation ([#1636](https://github.com/moj-analytical-services/splink/pull/1636))
- Emit a warning when using a default (i.e. non-trained) value for `probability_two_random_records_match` ([#1653](https://github.com/moj-analytical-services/splink/pull/1653))

### Fixed

- Fixed issue causing occasional SQL errors with certain database and catalog combinations ([#1558](https://github.com/moj-analytical-services/splink/pull/1558))
- Fixed issue where comparison vector grid not synced with corresponding histogram values in comparison viewer dashboard ([#1652](https://github.com/moj-analytical-services/splink/pull/1652))
- Fixed issue where composing null levels would mistakenly sometimes result in a non-null level ([#1672](https://github.com/moj-analytical-services/splink/pull/1672))
- Labelling tool correctly works even when offline ([#1646](https://github.com/moj-analytical-services/splink/pull/1646))

## [3.9.8] - 2023-10-05

### Added

- Added ability to delete tables with Spark when working in Databricks ([#1526](https://github.com/moj-analytical-services/splink/pull/1526))

### Changed

- Re-added support for python 3.7 (specifically >= 3.7.1) and adjusted dependencies in this case ([#1622](https://github.com/moj-analytical-services/splink/pull/1622))

### Fixed

- Fix behaviour where using `to_csv` with Spark backend wouldn't overwrite files even when instructed to ([#1635](https://github.com/moj-analytical-services/splink/pull/1635))
- Corrected path for Spark `.jar` file containing UDFs to work correctly for Spark < 3.0 ([#1622](https://github.com/moj-analytical-services/splink/pull/1622))
- Spark UDF `damerau_levensthein` is now only registered for Spark >= 3.0, as it is not compatible with earlier versions ([#1622](https://github.com/moj-analytical-services/splink/pull/1622))

[unreleased]: https://github.com/moj-analytical-services/splink/compare/v3.9.8...HEAD
[3.9.8]: https://github.com/moj-analytical-services/splink/compare/v3.9.7...v3.9.8

# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
## [9.0.0] - 2024-09-18
## Added
- pyproject.toml
- Documentation on how to use transaction test case when using pytest. PR [#108] from [@pavel-kalmykov](https://github.com/pavel-kalmykov).

### Changed
- Update to remove specific version references, since there haven't been significant changes the approach on versioning will change. The version will no longer update when only tests or supported versions are updated.
- Updated lock thread version and update job to not run at contested times to avoid github rate limiting errors.
- Updated ci build action versions.
- Move isort and pytest settings to toml file.
- Simplify tox.ini and github actions CI job.
- Update a getattr call to remove unnecessary default of None so it will fail on an attribute error.
- Change from .format() to f-strings.

### Removed
- Removed setup.py/setup.cfg

## [8.1.0] - 2024-01-28
### Added
- Run tests for django 5.0 and python 3.12.

## [8.0.0] - 2023-06-14
### Added
- Run tests for django 4.2. PR [#100] from [@johnthagen](https://github.com/johnthagen).

### Removed
- Dropped support for django 4.0.

## [7.0.0] - 2023-02-11
### Added
- Run tests for django 4.1.
- Run tests on python 3.11 with django 4.1.
- Select mode, with the ability to only cleanup selected models using a `select` decorator. Resolves issue [#75] for [@daviddavis](https://github.com/daviddavis).
- Documentation on the known limitations of referencing a file by multiple model instances. Resolves issue [#98] for [@Grosskopf](https://github.com/Grosskopf)

## Changed
- Pass more data to the cleanup_pre_delete and cleanup_post_delete signals. Resolves issue [#96] for [@NadavK](https://github.com/NadavK).

### Removed
- Dropped support for django 2.2 and python 3.5.

## [6.0.0] - 2022-01-24
### Added
- Update to run tests for python 3.10. PR [#88] from [@johnthagen](https://github.com/johnthagen).
- GitHub Actions. Resolves issue [#89] for [@johnthagen](https://github.com/johnthagen).

### Changed
- Fix default_app_config deprecation. PR [#86] from [@nikolaik](https://github.com/nikolaik).

### Removed
- Dropped support for django 3.0 and 3.1.
- Travis configuration.

## [5.2.0] - 2021-04-18
### Added
- New test to ensure cache is reset on create. PR [#81] from [@Flauschbaellchen](https://github.com/Flauschbaellchen).

### Changed
- Update to run tests for django 3.2.
- Update to document support for django 3.2.
- Update to run tests for python 3.9. PR [#80] from [@D3X](https://github.com/D3X).
- Reset cache for created instances in the post_save handler. PR [#81] from [@Flauschbaellchen](https://github.com/Flauschbaellchen).

## [5.1.0] - 2020-09-15
### Added
- This change log. Resolves issue [#73] for [@DmytroLitvinov](https://github.com/DmytroLitvinov).

### Changed
- Update to run tests for django 3.1. PR [#76] from [@johnthagen](https://github.com/johnthagen).
- Update to document support for django 3.1. PR [#76] from [@johnthagen](https://github.com/johnthagen).

### Removed
- Removed providing_args kwarg from Signal construction. PR [#74] from [@coredumperror](https://github.com/coredumperror).

## [5.0.0] - 2020-06-07
## [4.0.1] - 2020-06-06
## [4.0.0] - 2019-07-13
## [3.2.0] - 2019-02-17
## [3.1.0] - 2019-02-05
## [3.0.1] - 2018-11-18
## [3.0.0] - 2018-11-18
## [2.1.0] - 2017-12-30
## [2.0.0] - 2017-12-27
## [1.1.0] - 2017-12-27
## [1.0.1] - 2017-07-14
## [1.0.0] - 2017-06-30
## [0.4.2] - 2015-12-17
## [0.4.1] - 2015-12-02
## [0.4.0] - 2015-10-06
## [0.3.1] - 2015-06-25
## [0.3.0] - 2015-05-12
## [0.2.1] - 2015-03-07
## [0.2.0] - 2015-03-06
## [0.1.13] - 2015-02-21
## [0.1.12] - 2015-02-08
## [0.1.11] - 2015-02-01
## [0.1.10] - 2014-04-29
## [0.1.9] - 2014-04-29
## [0.1.8] - 2013-04-07
## [0.1.7] - 2013-04-03
## [0.1.6] - 2013-02-12
## [0.1.5] - 2012-08-17
## [0.1.4] - 2012-08-16
## [0.1.0] - 2012-08-14

[Unreleased]: https://github.com/un1t/django-cleanup/compare/9.0.0...HEAD
[9.0.0]: https://github.com/un1t/django-cleanup/compare/8.1.0...9.0.0
[8.1.0]: https://github.com/un1t/django-cleanup/compare/8.0.0...8.1.0
[8.0.0]: https://github.com/un1t/django-cleanup/compare/7.0.0...8.0.0
[7.0.0]: https://github.com/un1t/django-cleanup/compare/6.0.0...7.0.0
[6.0.0]: https://github.com/un1t/django-cleanup/compare/5.2.0...6.0.0
[5.2.0]: https://github.com/un1t/django-cleanup/compare/5.1.0...5.2.0
[5.1.0]: https://github.com/un1t/django-cleanup/compare/5.0.0...5.1.0
[5.0.0]: https://github.com/un1t/django-cleanup/compare/4.0.1...5.0.0
[4.0.1]: https://github.com/un1t/django-cleanup/compare/4.0.0...4.0.1
[4.0.0]: https://github.com/un1t/django-cleanup/compare/3.2.0...4.0.0
[3.2.0]: https://github.com/un1t/django-cleanup/compare/3.1.0...3.2.0
[3.1.0]: https://github.com/un1t/django-cleanup/compare/3.0.1...3.1.0
[3.0.1]: https://github.com/un1t/django-cleanup/compare/3.0.0...3.0.1
[3.0.0]: https://github.com/un1t/django-cleanup/compare/2.1.0...3.0.0
[2.1.0]: https://github.com/un1t/django-cleanup/compare/2.0.0...2.1.0
[2.0.0]: https://github.com/un1t/django-cleanup/compare/1.1.0...2.0.0
[1.1.0]: https://github.com/un1t/django-cleanup/compare/1.0.1...1.1.0
[1.0.1]: https://github.com/un1t/django-cleanup/compare/1.0.0...1.0.1
[1.0.0]: https://github.com/un1t/django-cleanup/compare/0.4.2...1.0.0
[0.4.2]: https://github.com/un1t/django-cleanup/compare/0.4.1...0.4.2
[0.4.1]: https://github.com/un1t/django-cleanup/compare/0.4.0...0.4.1
[0.4.0]: https://github.com/un1t/django-cleanup/compare/0.3.1...0.4.0
[0.3.1]: https://github.com/un1t/django-cleanup/compare/0.3.0...0.3.1
[0.3.0]: https://github.com/un1t/django-cleanup/compare/0.2.1...0.3.0
[0.2.1]: https://github.com/un1t/django-cleanup/compare/0.2.0...0.2.1
[0.2.0]: https://github.com/un1t/django-cleanup/compare/0.1.13...0.2.0
[0.1.13]: https://github.com/un1t/django-cleanup/compare/0.1.12...0.1.13
[0.1.12]: https://github.com/un1t/django-cleanup/compare/0.1.11...0.1.12
[0.1.11]: https://github.com/un1t/django-cleanup/compare/0.1.10...0.1.11
[0.1.10]: https://github.com/un1t/django-cleanup/compare/0.1.9...0.1.10
[0.1.9]: https://github.com/un1t/django-cleanup/compare/0.1.8...0.1.9
[0.1.8]: https://github.com/un1t/django-cleanup/compare/0.1.7...0.1.8
[0.1.7]: https://github.com/un1t/django-cleanup/compare/0.1.6...0.1.7
[0.1.6]: https://github.com/un1t/django-cleanup/compare/0.1.5...0.1.6
[0.1.5]: https://github.com/un1t/django-cleanup/compare/0.1.4...0.1.5
[0.1.4]: https://github.com/un1t/django-cleanup/compare/0.1.0...0.1.4
[0.1.0]: https://github.com/un1t/django-cleanup/releases/tag/0.1.0

[#108]: https://github.com/un1t/django-cleanup/pull/108
[#100]: https://github.com/un1t/django-cleanup/pull/100
[#98]: https://github.com/un1t/django-cleanup/issues/98
[#96]: https://github.com/un1t/django-cleanup/issues/96
[#89]: https://github.com/un1t/django-cleanup/issues/89
[#88]: https://github.com/un1t/django-cleanup/pull/88
[#86]: https://github.com/un1t/django-cleanup/pull/86
[#81]: https://github.com/un1t/django-cleanup/pull/81
[#80]: https://github.com/un1t/django-cleanup/pull/80
[#76]: https://github.com/un1t/django-cleanup/pull/76
[#75]: https://github.com/un1t/django-cleanup/issues/75
[#74]: https://github.com/un1t/django-cleanup/pull/74
[#73]: https://github.com/un1t/django-cleanup/issues/73

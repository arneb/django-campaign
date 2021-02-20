# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.1] - 2021-02-20
### Added
- Added 'campaign_sent' signal, triggered whenever a Campaign is sent

### Fixed
- Use hardcoded app_label 'campaign' in template resolution so app_label overrides via custom AppConfig don't interfere with our admin template overrides.

## [0.5.0] - 2021-01-29
### Added
- Validation of SubscriberList filter condition
- Validation of SubscriberList email field name
- Preview of SubscriberList recipients
- Basic skeleton for a test suite

## [0.4.1] - 2019-05-21
### Fixed
- Fix a packaging problem

## [0.4.0] - 2019-05-21 [YANKED]
### Added
- Management command to fetch bounces from Mailgun
- Introduced a "send_campaign" permission
- Support for Python 3

### Changed
- Compatiblity for more Django versions
- Use DISTINCT in subscriber query

## Start of Changelog

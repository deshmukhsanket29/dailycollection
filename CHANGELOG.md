# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial production-ready release
- Multi-agent authentication system
- Loan and savings customer management
- Real-time dashboards with Chart.js-style aggregation
- Daily datewise reports with PDF export
- Full transaction history reports with PDF export
- Customer photo upload with secure filename handling
- Block/unblock customer functionality
- Advanced search and status filtering
- Database migration from legacy `agent` and `customer` tables
- CSRF protection on all forms
- Responsive sidebar layout with mobile breakpoints
- Flash messaging for user feedback
- Comprehensive input validation (mobile, Aadhaar, required fields)
- Duplicate entry prevention
- Environment variable configuration

## [1.0.0] - 2024-01-01

### Added
- Initial scaffolded release with core CRUD operations
- SQLite database with SQLAlchemy ORM
- Basic Flask routing and Jinja2 templating

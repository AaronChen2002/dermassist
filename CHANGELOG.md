# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - YYYY-MM-DD

### Added
- Unit and integration testing framework using `pytest`.
- Tests for API security, health check, and classification endpoints.
- A `/health` endpoint for application monitoring.
- Created a dedicated `dermassist` conda environment for local development.

### Fixed
- Resolved `ModuleNotFoundError` for `torchcam` by adding it to dependencies.
- Fixed test failures by ensuring the application's startup events are triggered correctly by the `TestClient`.
- Corrected expected status code in security tests to align with FastAPI's default behavior. 
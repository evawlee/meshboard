# meshboard

Multi-tenant network fabric management dashboard.

## Modules

- `meshboard.api.auth` — token resolution and role-based access decorators
- `meshboard.api.sites` — branch-site CRUD with tenant scoping
- `meshboard.api.admin` — admin endpoints for users and peer registry
- `meshboard.reports` — file-serving reports API
- `meshboard.licensing` — smart-licensing manifest upload and listing
- `meshboard.store` — per-subsystem persistent state (sites, configs, licensing, reports, audit)
- `meshboard.util` — shared helpers

## Install

```
pip install -e ".[dev]"
```

Editable install with the `dev` extra, which pulls in `pytest`.

## Test

```
pytest tests/
```

The test suite exercises the multi-tenant API surface, file-serving reports, smart-licensing upload, and the per-subsystem stores.

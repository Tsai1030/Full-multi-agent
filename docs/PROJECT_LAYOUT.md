# Project Layout

## Top-level folders

- `backend/`: Python backend entrypoints, core source code, and MCP server files.
- `frontend/`: React frontend application and frontend public assets.
- `tests/`: test scripts and validation utilities.
- `scripts/`: setup, debug, demo, and maintenance scripts.
- `public/`: shared static assets, HTML previews, screenshots, and reference files.
- `docs/`: architecture notes, setup guides, reports, and code analysis documents.

## Backend layout

- `backend/main.py`: main backend application entrypoint.
- `backend/api_server.py`: FastAPI server entrypoint.
- `backend/performance_config.py`: backend performance presets.
- `backend/src/`: backend source modules.
- `backend/mcp-server/`: MCP server package files.

## Notes

- Use `python -m backend.api_server` to start the backend from the repository root.
- Test and script imports now target `backend...` paths.

#!/usr/bin/env bash
set -euo pipefail

exec uv run gunicorn --bind 0.0.0.0:3001 --workers 2 --preload --access-logfile - app:app

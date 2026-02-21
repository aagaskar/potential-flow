#!/usr/bin/env bash
set -euo pipefail

exec uv run gunicorn --bind 0.0.0.0:3001 app:app

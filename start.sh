#!/usr/bin/env bash
set -euo pipefail

exec gunicorn --bind 0.0.0.0:3001 app:app

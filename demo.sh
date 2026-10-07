#!/usr/bin/env bash
set -e
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ -x .venv/Scripts/python.exe ]]; then
    python_path=.venv/Scripts/python.exe
elif [[ -x .venv/bin/python ]]; then
    python_path=.venv/bin/python
else
    printf '%s\n' 'The project environment is missing. Follow the setup in README.md first.' >&2
    exit 1
fi
exec "$python_path" demo.py --warmup "$@"

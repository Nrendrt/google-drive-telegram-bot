#!/bin/sh
set -e
cd "$(dirname "$0")"

if [ ! -x ./venv/bin/python ]; then
  python3 -m venv venv
  ./venv/bin/pip install --upgrade pip
  ./venv/bin/pip install -r requirements.txt
  # Pyrogram 1.0.1 pins async-lru 1.0.2, which does not run on Python 3.11.
  ./venv/bin/pip install 'async-lru>=2.0.4'
fi

mkdir -p downloads data
exec ./venv/bin/python -m bot

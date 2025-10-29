#!/bin/bash

if [ ! -f ./.venv/bin/activate ]; then
  ./install.sh
fi

source python3 -m venv .venv
python3 Main.py
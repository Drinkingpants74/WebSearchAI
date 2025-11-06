#!/bin/bash

if [ ! -f ./.venv/bin/activate ]; then
  echo "Virtual Environment Not Found. Running Installer..."
  ./install.sh
fi

echo "Updating Application..."
git pull

source python3 -m venv .venv
python3 Main.py
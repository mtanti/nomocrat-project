#!/bin/bash
set -e

conda create --prefix venv/ --yes python=3.9
conda shell.bash activate venv/

pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121
pip install -r requirements_dev.txt
pip install -e .

#!/bin/bash
set -e

conda shell.bash activate venv/

echo "#########################################"
echo "mypy"
echo "..checking tools"
python -m mypy tools/
echo "..checking bin"
python -m mypy bin/
echo "..checking nomocrat_project"
python -m mypy src/nomocrat_project/
echo ""

echo "#########################################"
echo "pylint"
echo "..checking tools"
python -m pylint tools/
echo "..checking bin"
python -m pylint bin/
echo "..checking nomocrat_project"
python -m pylint src/nomocrat_project/
echo ""

echo "#########################################"
echo "sphinx api documentation"
python tools/sphinx_api_doc_maker.py
echo ""

echo "#########################################"
echo "project validation"
python tools/validate_project.py
echo ""

echo "#########################################"
echo "sphinx"
cd docs
make html
cd ..
echo ""

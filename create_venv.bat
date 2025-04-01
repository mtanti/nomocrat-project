@echo off

call conda create --prefix venv\ --yes python=3.9 || pause && exit /b
call conda activate venv\ || pause && exit /b

call pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cu121 || pause && exit /b
call pip install -r requirements_dev.txt || pause && exit /b
call pip install -e . || pause && exit /b

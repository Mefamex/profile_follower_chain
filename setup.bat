@echo off 

python.exe -m pip install -U pip
python.exe -m pip install -U uv

uv init
uv venv

uv add uv

uv sync --acvtive

pause
exit



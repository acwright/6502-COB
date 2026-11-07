#!/bin/zsh
# Makes the Python that reads and writes 3D models (build123d) in Tools/work/venv, which git ignores.
# make.py needs it for Plate.stl, and for the tops from the boards' STEP models. Python 3.10 or newer.
set -e
T=${0:A:h:h}
PY=${PYTHON:-$(command -v python3.12 || command -v python3.11 || command -v python3.10)}
[[ -n $PY ]] || { echo 'setup.sh needs Python 3.10 or newer (Homebrew: brew install python@3.12)'; exit 1 }
$PY -m venv $T/work/venv
$T/work/venv/bin/pip install -q --upgrade pip
$T/work/venv/bin/pip install -q 'build123d==0.13.0' 'shapely==2.2.0'
$T/work/venv/bin/python -c 'import build123d; print("build123d", build123d.__version__)'

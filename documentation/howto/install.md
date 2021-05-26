# Installation
## Prerequisites
- R >=3.5.3
- the R packrat module
- Python 3 >=3.5.3 with pip
- a compatible libpython shared library (installing python3-dev on Linux distributions should ensure this; see [this issue](https://github.com/rstudio/reticulate/issues/637))

Python and R versions other than 3.5.3 are unsupported due to some frozen dependencies being incompatible with later versions of R/Python.
Support for R 4.0.4 is being tested, although this may break compatibility with R 3.5.3.
Version support policy is not final and so no guarantees are made.
In general, newer versions will be prioritised over backwards-compatibility.

## Setup
- Clone the repo
- Source `setup.R` in an R session to restore the packrat environment
- Create a virtual environment called `reticulate-venv` in the root directory
- Install python dependencies from requirements.txt, with `source reticulate-venv/bin/activate && pip install -r requirements.txt` on Linux

For Linux platforms (and possibly others supporting Bash), `setup.sh` is provided to automate the steps after cloning.
Simply run `./setup.sh` in a terminal.

### Prerequisites
- R >=3.5.3
- Python 3 >=3.5.3
- a compatible libpython shared library (installing python3-dev on Linux distributions should ensure this; see [this issue](https://github.com/rstudio/reticulate/issues/637))
- python3 reticulate and venv modules

Python and R versions other than 3.5.3 remain untested, although more recent versions are likely to work

### Setup
- Clone the repo
- Source `setup.R` in an R session to restore the packrat environment
- Create a virtual environment called `reticulate-venv` in the root directory
- Install python dependencies from requirements.txt, with `source reticulate-venv/bin/activate && pip install -r requirements.txt` on Linux

For Linux platforms (and possibly others supporting Bash), `setup.sh` is provided to automate the steps after cloning.
Simply run `./setup.sh` in a terminal.

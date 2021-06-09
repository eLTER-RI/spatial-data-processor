# Installation
## Prerequisites
- R 4.0.4
- the R packrat module
- Python 3.8.5
- pip
- a compatible libpython shared library (installing python3-dev on Linux distributions should ensure this; see [this issue](https://github.com/rstudio/reticulate/issues/637))
- internet access to install python and R dependencies

The current policy is to only support the single versions of R and Python stated above.
Older versions of Python and R likely will not work due to dependencies, while newer versions may work despite being unsupported.
For now, the sole supported versions of R and Python will be updated to match the newest versions in [datalabs](https://datalab.datalabs.ceh.ac.uk/) as they become available, although this policy is not final.

## Setup
- Clone the repo
- Source `setup.R` in an R session to restore the packrat environment
- Create a virtual environment called `reticulate-venv` in the root directory
- Install python dependencies from requirements.txt, with `source reticulate-venv/bin/activate && pip install -r requirements.txt` on Linux

For Linux platforms (and possibly others supporting Bash), `setup.sh` is provided to automate the steps after cloning.
Simply run `./setup.sh` in a terminal.

## Running
Once installed, app.R can be treated as any other shiny deployment.
Running `Rscript app.R` will start a server on a random port, suitable for development.

R CMD BATCH setup.R &> /dev/null
python3 -m venv reticulate-venv
source ./reticulate-venv/bin/activate
pip install -r requirements.txt
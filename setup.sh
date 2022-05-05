mkdir -p {in,out}put/wf{1,2}
Rscript ./setup.R
python3 -m venv ./reticulate-venv
source ./reticulate-venv/bin/activate
pip install -r requirements.txt

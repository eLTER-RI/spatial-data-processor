mkdir -p {in,out}put/{wf1,wf2,fluxnet}
Rscript ./setup.R
python3 -m venv ./reticulate-venv
source ./reticulate-venv/bin/activate
pip install -r requirements.txt

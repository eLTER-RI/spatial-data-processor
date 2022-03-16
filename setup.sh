mkdir -p input/{wf1,wf2,fluxnet,icos} output/{wf1,wf2,wf3}
Rscript ./setup.R
python3 -m venv ./reticulate-venv
source ./reticulate-venv/bin/activate
pip install -r requirements.txt

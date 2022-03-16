sudo apt-get update
sudo apt-get install python3-venv
Rscript -e 'install.packages("packrat")'
source setup.sh
chmod 0777 input/{wf1,wf2,fluxnet,icos} output/{wf1,wf2,wf3} shapefiles/deims

sudo apt-get update
sudo apt-get install python3-venv
Rscript -e 'install.packages("packrat")'
source setup.sh
chmod 0777 {in,out}put/wf{1,2} shapefiles/deims

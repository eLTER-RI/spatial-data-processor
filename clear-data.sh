# WARNING - only run this from the root of the git
# repository as ./clear-data.sh, as there are no checks
# on working directory.
#
# remove all input and output of both workflows
rm -fv input/wf1/*
rm -fv input/wf2/*
rm -fv output/wf1/*
rm -fv output/wf2/*
rm -fv output/fluxnet/*

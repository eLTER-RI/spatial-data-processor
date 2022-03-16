# WARNING - only run this from the root of the git
# repository as ./clear-data.sh, as there are no checks
# on working directory.
#
# remove user input (wf1/wf2 only) and output of all workflows
rm -fv input/wf1/*
rm -fv input/wf2/*
rm -fv output/wf1/*
rm -fv output/wf2/*
rm -fv output/wf3/*

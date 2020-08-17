#setup the environmane to run the tools for this sub directory.
#
# Thsi __MUST_ be run from this sub diretory
# example: Bsh> source setup.sh
#
# Set python path Thsi code properl handles having
# a one element path (ie initially PYTHONPATH is null
PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}$PWD/lib"
export PYTHONPATH=$PYTHONPATH
echo $PYTHONPATH 2>/dev/stderr
pip install tabulate
pip install trailscraper
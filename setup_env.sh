# run as "source setup_env.sh"

# activate python3 environment (created using Anaconda python dist)
# containing Numpy & Pandas
source activate python3

LIBPATH="$HOME/Projects/OCEAN-CERTAIN/tredev/lib:/Users/work/Projects/OCEAN-CERTAIN/baleen/lib"
echo prepending $LIBPATH to PYTHONPATH
export PYTHONPATH=$LIBPATH:$PYTHONPATH


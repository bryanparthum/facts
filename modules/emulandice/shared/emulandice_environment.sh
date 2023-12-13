#! /bin/bash

# this script loads the modules
# required for emulandice to run on Amarel
#
# You may have to modify it for your system.

hs=`hostname`
if [ ${hs: -18} = 'amarel.rutgers.edu' ]; then
    if conda info --envs | grep -q r-base; then
         echo "r-base already exists"
    else
         #conda create -y -n r-base r-base cmake gcc libopenblas gfortran
         conda create -y -n r-base -c conda-forge r-base cmake gcc libopenblas gfortran
    fi
    conda activate r-base
fi

if [ "$1" == "--Rscript" ]; then
    Rscript -e "source('packrat/init.R')" -e "packrat::install_local('emulandice_1.1.0.tar.gz')"
fi

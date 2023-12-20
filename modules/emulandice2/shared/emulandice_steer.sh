#!/bin/bash

# check for results directory
#if [[ ! -d results ]]; then
#    mkdir results
#fi

# set up environment
source emulandice_environment.sh

# run emulandice

ice_source=$1 # Ice source: GIS, AIS or GLA
region=$2 # Ice source region: ALL for GIS/AIS and RGI01-RGI19 for GLA
emu_name=$3 # models_emulator_settings: e.g. "CISM_pow_exp_20", "CISM_IMAUICE_GISM_pow_exp_20"
climate_data_file=$4 # e.g. emulandice.ssp585.temperature.fair.temperature_climate.nc
scenario=$5 # e.g. ssp585 [could extract from filename instead?]

Rscript --vanilla -e "library(emulandice2)" -e "source('main.R')" $ice_source $region $emu_name $climate_data_file $scenario
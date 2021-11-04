#!/bin/bash

echo '------------------------------------------------------------------------'
echo 'This script is for configuring the osmnx-python3 environment using '
echo 'Anaconda. You should be in your target environment to install the correct'
echo '    packages for that environment.'
echo '------------------------------------------------------------------------'
read -p "Are you in your target conda environment? " -n 1 -r
echo    # (optional) move to a new line
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
echo '------------------------------------------------------------------------'
    echo 'To enter your target environment type: conda activate <env name> on '
    echo 'the command line. To list conda environments, type: conda info --envs.'
echo '------------------------------------------------------------------------'
    exit 1
fi
conda activate osmnx-python3
conda env update --file environment.yml --prune
pip install --upgrade ipyleaflet jupyterlab
jupyter labextension install jupyter-leaflet @jupyter-widgets/jupyterlab-manager
python -m ipykernel install --user --name osmnx-python3 --display-name "Python3 OSMNx"
conda deactivate

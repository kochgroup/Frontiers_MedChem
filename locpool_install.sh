#!/usr/bin/bash
set -e
cd $HOME
echo "################################################################################"
echo "Activate 'frontiers_medchem' environment"
echo "################################################################################"
source ~/.bashrc
conda activate frontiers_medchem
echo "################################################################################"
echo "Installing Maize"
echo "################################################################################"
pip install git+https://github.com/MolecularAI/maize.git
pip install git+https://github.com/MolecularAI/maize-contrib.git

echo "################################################################################"
echo "Change line to fix error"
echo "################################################################################"
TARGET_FILE="$HOME/.local/lib/python3.10/site-packages/maize/steps/mai/misc/reinvent.py"
#old path: $CONDA_PREFIX/lib/python3.10/site-packages/maize/steps/mai/misc/reinvent.py
MATCH_STR='"property": "predictions",'
if ! sed -n '138p' "$TARGET_FILE" | grep -q "$MATCH_STR"; then
    sed -i "137a \            $MATCH_STR" "$TARGET_FILE"
    echo "  added 'property' key to _patch_config"
else
    echo "  'property' key already in _patch_config"
fi

echo "################################################################################"
echo "Installing additional packages"
echo "################################################################################"
pip install mols2grid graphviz
pip install ipython jupyter

echo "################################################################################"
echo "Install REINVENT4"
echo "################################################################################"
git clone https://github.com/MolecularAI/REINVENT4.git
cd REINVENT4
python install.py cpu
cd $HOME

echo "################################################################################"
echo "Install workshop repo"
echo "################################################################################"
if [ -d "Frontiers_MedChem" ]; then
    echo "The folder exists already, skipping clone"
else
    git clone https://github.com/kochgroup/Frontiers_MedChem.git
fi
cd Frontiers_MedChem
pip install -e .
cd $HOME

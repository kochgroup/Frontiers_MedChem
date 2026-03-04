# Frontiers in Medicinal Chemistry (2026): REINVENT4 & CSD GOLD Workshop

Welcome to the workshop! This repository contains all the tutorials, scripts, and custom Maize nodes needed to link REINVENT4 de novo molecule generation with CCDC GOLD docking.

## ⚠️ Prerequisites
Before you begin, ensure you have:
1. **Mamba** (or Conda) installed on your system.
2. A valid **CCDC License** (required for the GOLD docking API).
3. **Git** installed.

---

## Step 1: Clone this Repository
First, download the workshop materials to your local machine and enter the directory:

``` bash
git clone https://github.com/mehmetaliyucel/Frontiers_MedChem.git
cd Frontiers_MedChem
```
Step 2: Download the Prior Models

The REINVENT4 generators are too large for GitHub. Download generators that you want to use from Zenodo: https://zenodo.org/records/15641297 (This link may change in the future, always check from source)
Extract the files and move all .prior files into the priors/ folder inside this repository:
Frontiers_MedChem/priors/

Step 3: Environment Setup

We will use mamba to create the environment and install the required packages. Run these commands sequentially in your terminal:
```bash
# 1. Create and activate the base environment
mamba create -n frontiers_medchem python=3.10 -y
mamba activate frontiers_medchem

# 2. Install the CSD Python API (Requires CCDC License) for more installation options please check the the website https://downloads.ccdc.cam.ac.uk/documentation/API/installation_notes.html#installation
conda install --channel=https://conda.ccdc.cam.ac.uk csd-python-api


# 3. Install Maize and Maize-Contrib from GitHub
pip install git+https://github.com/MolecularAI/maize.git
pip install git+https://github.com/MolecularAI/maize-contrib.git

# 4. Install REINVENT4
git clone https://github.com/MolecularAI/REINVENT4.git
cd REINVENT4
python install.py cpu
cd ..

# 6. Install the custom workshop package (Fixes Python import paths)
# Make sure you are in the main Frontiers_MedChem folder when you run this!
pip install -e .
```

# References

1. Loeffler, H.H., He, J., Tibo, A. et al. Reinvent 4: Modern AI–driven generative molecule design.  J Cheminform 16, 20 (2024). [https://doi.org/10.1186/s13321-024-00812-5](https://doi.org/10.1186/s13321-024-00812-5)
2. Verdonk ML, Cole JC, Hartshorn MJ, Murray CW, Taylor RD. Improved protein-ligand docking using GOLD. Proteins. 2003, 52, 609-23. doi: [10.1002/prot.10465](10.1002/prot.10465)
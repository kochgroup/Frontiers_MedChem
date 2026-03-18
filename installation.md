# Frontiers in Medicinal Chemistry (2026): REINVENT4 & CSD GOLD Workshop

This document describes how to set up your environment for the workshop. For an overview of the workshop and tutorials, please see [README.md](README.md)

## ⚠️ Prerequisites
Before you begin, ensure you have:
1. **Conda** (or Mamba) installed on your system.
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

In this repo, some prior models (reinvent and libinvent) of REINVENT4 are already uploaded but there more models provided by AstraZeneca. So if you need different models please visit the original [REINVENT repo](https://github.com/MolecularAI/REINVENT4).
You can find priors at Frontiers_MedChem/priors. If you download another model please move it in this directory. 

Step 3: Environment Setup

We will use mamba to create the environment and install the required packages. Run these commands sequentially in your terminal:
```bash
# 1. Create and activate the base environment
conda create -n frontiers_medchem python=3.10 -y
conda activate frontiers_medchem

# 2. Install the CSD Python API (Requires CCDC License) for more installation options please check the the website https://downloads.ccdc.cam.ac.uk/documentation/API/installation_notes.html#installation
conda install --channel=https://conda.ccdc.cam.ac.uk csd-python-api


# 3. Install Maize and Maize-Contrib from GitHub
pip install git+https://github.com/MolecularAI/maize.git
pip install git+https://github.com/MolecularAI/maize-contrib.git

# 4. Install REINVENT4
cd ..
git clone https://github.com/MolecularAI/REINVENT4.git
cd REINVENT4
python install.py cpu
# 5. Return to the Frontiers_MedChem directory
cd ~/Frontiers_MedChem
# 6. Install the custom workshop package (Fixes Python import paths). 
pip install -e .
#7. For visualaazitons 
pip install mols2grid graphviz
```

**Notes:** 
1. For step 6, You must be in the **Frontiers_MedChem**. 
2. If you run into installation or runtime errors, please see [potential_errors.md](potential_errors.md).


# References

1. Loeffler, H.H., He, J., Tibo, A. et al. Reinvent 4: Modern AI–driven generative molecule design.  J Cheminform 16, 20 (2024). [https://doi.org/10.1186/s13321-024-00812-5](https://doi.org/10.1186/s13321-024-00812-5)
2. Verdonk ML, Cole JC, Hartshorn MJ, Murray CW, Taylor RD. Improved protein-ligand docking using GOLD. Proteins. 2003, 52, 609-23. doi: [https://doi.org/10.1002/prot.10465](https://doi.org/10.1002/prot.10465)
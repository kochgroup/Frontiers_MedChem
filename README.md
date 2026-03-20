# Frontiers in Medicinal Chemistry (2026): REINVENT4 & CSD GOLD Workshop

This repository contains the **tutorials**, **scripts**, and **custom Maize Nodes** for [a workshop](https://veranstaltungen.gdch.de/microsite/index.cfm?l=11912&modus=) that links **REINVENT4** molecule generation tool with **CCDC GOLD** docking, using **Maize** as workflow manager. 

## Workshop overview 

By the end of this session, you will learn how to:

* Build and run **Maize** workflows (nodes, parameters, and connections).
* Explore useful chemistry functions within **maize-contrib**.
* Master common tasks in the **CSD Python API** (protein preparation, defining binding sites, etc.).
* Run **REINVENT4** to generate molecules and get comfortable with TOML configuration files.
* Connect **REINVENT** and **GOLD** into a single, automated **Maize** pipeline: *Generation → Docking → Scoring → Feedback to REINVENT*.


## Tutorials 

The tutorials are Jupyter notebooks in the ['tutorials'](tutorials/) directory. Run them in order. each builds on the previous one. 

| Tutorial | Description |
|---------|------|
| **[1 - Hello Maize](tutorials/1-%20hello_maize.ipynb)** | Check maize installation, define a custom node (parameters, output), and run a simple workflow. |
| **[2 - Maize Chemsitry](tutorials/2-%20maize_chem.ipynb)** | Load SMILES, and molecules, use RDKit descriptors and a custom 'CalcDesc' node within a Maize workflow. |
| **[3 - CSD GOLD](tutorials/3-%20csd_gold.ipynb)** | Use CCDC Python API, load a protein, prepare it, define a binding site ... |
| **[4 - REINVENT4](tutorials/4-%20reinvent_tutorial.ipynb)** | Check REINVENT4 installation, configure reinforcement learning (prior, agent, scoring, sampling) |
| **[5 - REINVENT + Maize + Gold](tutorials/5-%20reinvent_maize_gold.ipynb)** | The full pipeline with already created nodes. |

## Getting started 

1. **Install the environment**
    Follow the instructions in **[installation.md](installation.md)** 
2. **Config File:**
    Change the **[config.toml](/config.toml)**
    To do this you migh need to know the directory of the conda environment.
    If the environment is activated you can run this command to get the environment path on terminal:
    ``` bash
    echo $CONDA_PREFIX
    ```
    or if you need to get main conda directory:
    ``` bash
    conda info --base
    ```
3. **Run the tutorials** 
    Open the notebooks in **[tutorials](/tutorials/)** in order.
4. **Upps, something went wrong!**
    First of all, no worries. Luckily (for you), something went wrong for me as well, so check out **[potential_errors.md](potential_errors.md)**. See for common installation and runtime issues with potential solutions. If the error persists or the error is not listed, just look around you would see one of us hanging around there and we'll come rescue you. 

## References
1. Loeffler, H.H., He, J., Tibo, A. et al. Reinvent 4: Modern AI–driven generative molecule design. J Cheminform 16, 20 (2024). https://doi.org/10.1186/s13321-024-00812-5
    
2. Verdonk ML, Cole JC, Hartshorn MJ, Murray CW, Taylor RD. Improved protein-ligand docking using GOLD. Proteins. 2003, 52, 609-23. doi: https://doi.org/10.1002/prot.10465
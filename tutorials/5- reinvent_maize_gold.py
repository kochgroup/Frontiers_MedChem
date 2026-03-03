#%%
import os
conda_lib = "/nfs/home/myuecel3/miniforge3/envs/frontiers_medchem/lib"
old_path = os.environ.get("LD_LIBRARY_PATH", "")
os.environ["LD_LIBRARY_PATH"] = f"{conda_lib}:{old_path}"
from maize.core.workflow import Workflow
import numpy as np
from pathlib import Path
import os
import sys
from maize.steps.mai.molecule import Smiles2Molecules
from maize.steps.mai.misc import ReInvent
import sys
import os




from nodes import GOLDDocking, SaveIsomers, ScoreConverter




#%%
"""Create and execute the REINVENT-GOLD docking workflow"""
flow = Workflow(name='reinvent_dock')
flow.config.update(Path('/nfs/home/myuecel3/Frontiers_MedChem/config.toml'))

rnve = flow.add(ReInvent)
smi2mol = flow.add(Smiles2Molecules, loop=True)
save = flow.add(SaveIsomers, name='save_mol', parameters={'file': '/nfs/home/myuecel3/Frontiers_MedChem/data/output/vegfr_reinvent_mols_stage2.sdf'},loop=True)
gold = flow.add(GOLDDocking, loop=True)
converter = flow.add(ScoreConverter, loop=True)
#%%
# Set parameters
gold.output_file.set('/nfs/home/myuecel3/Frontiers_MedChem/data/output')
gold.protein_file.set('/nfs/home/myuecel3/Frontiers_MedChem/data/protein_ligand_4LQM_CHEMBL674017.mol2')
gold.ref_ligand.set('/nfs/home/myuecel3/Frontiers_MedChem/data/4lqm_ligand.mol2')

# Connect the nodes
flow.connect(rnve.out, smi2mol.inp)
flow.connect(smi2mol.out, save.inp)
flow.connect(save.out, gold.inp)
flow.connect(gold.out, converter.inp)
flow.connect(converter.out, rnve.inp) 
#%%
# REINVENT configuration
rnve_conf = Path('/nfs/home/myuecel3/Frontiers_MedChem/configs/reinvent.toml')

rnve.configuration.set(rnve_conf)
rnve.max_epoch.set(5)  


rnve.low.set(0.0)
rnve.high.set(120.0)
rnve.reverse.set(False)


# Number of molecules to generate each epoch
rnve.batch_size.set(16)

# Check and execute the workflow
flow.check()
#%%
viz_path = '/nfs/home/myuecel3/Frontiers_MedChem/workflow_visualization_vegfr2'
flow.visualize().render(viz_path, format='pdf')
print(f"Workflow visualization saved to: {viz_path}")
flow.execute()


# %%


from maize.core.node import Node
from maize.core.interface import Input, Output,Parameter
from maize.utilities.chem import IsomerCollection
from maize.utilities.chem import (IsomerCollection)
from maize.core.node import Node
from maize.core.interface import Input, Output, Parameter
import numpy as np
import rdkit
from rdkit import Chem
from rdkit.Chem import Descriptors
import math
class ScoreConverter(Node):
    """Extracts the highest docking score across all conformers for REINVENT."""
    
    inp: Input[list[IsomerCollection]] = Input()
    out: Output[np.ndarray] = Output()
    batch_size: Parameter[int] = Parameter(default=32)
    
    def run(self) -> None:
        mols = self.inp.receive()
        scores = []
        
        for mol in mols:

            if mol.molecules and len(mol.molecules) > 0:
                
                # 1. Get the score for EVERY conformer/isomer of this molecule
                all_conformer_scores = [isomer.get_tag("docking_score", 0.0) for isomer in mol.molecules]
                mw = mol.molecules[0].get_tag("Mol_Wt", 1.0)
                # 2. Find the absolute highest score among all poses
                best_conformer_score = max(all_conformer_scores)
                 
                final_score = float(best_conformer_score / math.sqrt(mw)) 
                scores.append(final_score)
                
            else:
                # If docking failed completely, punish with a 0.0
                scores.append(0.0)
    
        # Convert to a float32 array (REINVENT4's preferred format)
        score_array = np.array(scores, dtype=object)
        
        self.logger.info(f"Epoch progress: Batch of {len(score_array)} scores sent to REINVENT")
        self.out.send(score_array)
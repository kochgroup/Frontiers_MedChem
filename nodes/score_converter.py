
from maize.core.node import Node
from maize.core.interface import Input, Output,Parameter
from maize.utilities.chem import IsomerCollection
from maize.utilities.chem import (IsomerCollection)
from maize.core.node import Node
from maize.core.interface import Input, Output, Parameter
import numpy as np


class ScoreConverter(Node):
    """Extracts docking scores from IsomerCollection objects for ReInvent."""
    
    inp: Input[list[IsomerCollection]] = Input()
    out: Output[np.ndarray] = Output()
    batch_size: Parameter[int] = Parameter(default=32)
    
    def run(self) -> None:
        mols = self.inp.receive()
        scores = []
        
        # Extract scores from molecule tags
        for mol in mols:
            if mol.molecules and len(mol.molecules) > 0:
                # Get the score from the first isomer
                score = mol.molecules[0].get_tag("docking_score", 0.0)
                scores.append(score)
            else:
                scores.append(0.0)
        
        # Pad or truncate scores to match batch size
        if len(scores) < self.batch_size.value:
            mean_score = sum(scores) / len(scores) if scores else 0.0
            padded_scores = scores + [mean_score] * (self.batch_size.value - len(scores))
        else:
            padded_scores = scores[:self.batch_size.value]
        
        score_array = np.array(padded_scores)
        self.logger.info(f"Epoch progress: Current batch of scores being sent to REINVENT")

        self.out.send(score_array)
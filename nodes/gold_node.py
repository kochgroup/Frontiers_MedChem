from maize.core.node import Node
from maize.core.interface import Input, Output,Parameter, Flag, FileParameter
from maize.utilities.validation import SuccessValidator
from maize.utilities.chem import IsomerCollection, save_smiles
from pathlib import Path
import os
import sys

from maize.utilities.chem import (IsomerCollection, Isomer, load_sdf_library,save_sdf_library,merge_isomers)
from rdkit import Chem
from rdkit.Chem import Descriptors
from maize.core.node import Node
from maize.core.interface import Input, Output, Parameter
from pathlib import Path
from maize.utilities.validation import SuccessValidator
from scripts import gold_docking

class GOLDDocking(Node):
    """
    A node for running GOLD docking using the `run_gold` command.
    """

    required_callables = ['run_gold']
    
    inp: Input[Path] = Input()
    protein_file: Parameter[Path] = Parameter()
    ref_ligand: Parameter[Path] = Parameter()
    max_conformers: Parameter[int] = Parameter(default=10)
    scoring_function: Parameter[str] = Parameter(default='plp')
    output_file: FileParameter[Path] = FileParameter()
    out: Output[list[IsomerCollection]] = Output() 
    
    def run(self) -> None:
        ligand_path = self.inp.receive()
        protein_file = self.protein_file.value
        ref_ligand = self.ref_ligand.value
        output_file = self.output_file.filepath
        max_conformers = self.max_conformers.value
        scoring_function = self.scoring_function.value

        command = f"{self.runnable['run_gold']} --p {protein_file} --r {ref_ligand} --l {ligand_path} --o {output_file} --max_conformers {max_conformers} --scoring_function {scoring_function}"
        res = self.run_command(command)
        
        input_mols = load_sdf_library(ligand_path)
        result_mols = []
        
        if res.stdout:
            stdout_str = res.stdout.decode('utf-8')
            self.logger.info(f"Command output: {stdout_str}")
            
            # Extract scores
            scores = []
            for line in stdout_str.split('\n'):
                if 'fitness scores:' in line.lower():
                    scores_str = line.split(':')[1].strip()
                    scores = [float(s) for s in scores_str.split(',')]
                    self.logger.info(f"Docking fitness scores: {scores}")
                    break
            
            # If no scores found in that format, try the single score format
            if not scores:
                for line in stdout_str.split('\n'):
                    if 'fitness score:' in line.lower():
                        score = float(line.split(':')[1].strip())
                        scores = [score]
                        self.logger.info(f"Single docking fitness score: {score}")
                        break
            
            # If still no scores found
            if not scores:
                self.logger.warning("No fitness scores found in output")
                scores = [0.0] * len(input_mols)
            
            # Attach scores to molecules as tags
            for i, mol in enumerate(input_mols):
                if i < len(scores):
                    for isomer in mol.molecules:
                        smiles = isomer.to_smiles()
                        mw = Descriptors.HeavyAtomMolWt(Chem.MolFromSmiles(smiles))
                        isomer.set_tag("docking_score", scores[i])
                        isomer.set_tag("Mol_Wt", mw)
                    
                    result_mols.append(mol)
                else:
                    for isomer in mol.molecules:
                        smiles = isomer.to_smiles()
                        mw = Descriptors.HeavyAtomMolWt(Chem.MolFromSmiles(smiles))
                        isomer.set_tag("docking_score", 0.0)
                        isomer.set_tag("Mol_Wt", mw)
                    result_mols.append(mol)
                    
            # Try to load docked conformations if available
            try:
                docked_path = Path(output_file) / "docked_ligands.mol2"
                if docked_path.exists():
                    docked_mols = load_sdf_library(docked_path)
                    # Merge the docked conformations with the original molecules
                    for i, mol in enumerate(result_mols):
                        if i < len(docked_mols):
                            # Add the docked conformations
                            for j, isomer in enumerate(docked_mols[i].molecules):
                                mol.molecules[j].add_conformer(isomer.conformer(0))
            except Exception as e:
                self.logger.warning(f"Could not load docked conformations: {e}")
        
        self.logger.info(f"Returning {len(result_mols)} molecules with docking scores")
        self.out.send(result_mols)
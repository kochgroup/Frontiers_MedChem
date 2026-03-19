import shutil
import tempfile
from typing import Optional
from uuid import uuid4

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
    
    inp: Input[list[IsomerCollection]] = Input()
    protein_file: Parameter[Path] = Parameter()
    prepare_protein : Parameter[Optional[bool]] = Parameter(default=False)
    ref_ligand: Parameter[Path] = Parameter()
    ndocking: Parameter[int] = Parameter(default=10)
    scoring_function: Parameter[str] = Parameter(default='plp')
    output_base_dir: Parameter[Path | None] = Parameter(default=None)
    binding_site_mode: Parameter[str] = Parameter(default='from_ligand')
    binding_site_residues: Parameter[str | None] = Parameter(optional=True)
    binding_site_radius: Parameter[float] = Parameter(default=8.0)

    out: Output[list[IsomerCollection]] = Output() 
    
    def run(self) -> None:
        mols = self.inp.receive()
        protein_file = self.protein_file.value
        ref_ligand = self.ref_ligand.value
        ndocking = self.ndocking.value
        binding_site_mode = self.binding_site_mode.value
        binding_site_radius = self.binding_site_radius.value  
        scoring_function = self.scoring_function.value

        output_base = self.output_base_dir.value if self.output_base_dir.is_set else None
        binding_site_residues = self.binding_site_residues.value if self.binding_site_residues.is_set else None
        prepare_protein = self.prepare_protein.value if self.prepare_protein.is_set else False



        #command = f"{self.runnable['run_gold']} --p {protein_file} --r {ref_ligand} --l {ligand_path} --o {output_base_dir} --ndocking {ndocking} --scoring_function {scoring_function}"
        #res = self.run_command(command)
        if binding_site_mode == 'from_residues' and not binding_site_residues:
            raise ValueError("The --residues argument is required when using 'from_residues' binding site mode.")
        if binding_site_mode == 'from_ligand' and not ref_ligand:
            raise ValueError("The --r argument is required when using 'from_ligand' binding site mode.")
        if not hasattr(self, '_reinvent_step'):
            self._reinvent_step = 0
        self._reinvent_step += 1
        batch_id = f'step{self._reinvent_step}'
        if output_base is not None:
            work_dir = Path(output_base) / f"gold_docking_{batch_id}"
            work_dir.mkdir(parents=True, exist_ok=True)
            cleanup = False
        else:
            work_dir = Path(tempfile.mkdtemp())
            cleanup = True
        ligand_sdf = work_dir / "ligands.sdf"
        try:
            save_sdf_library(ligand_sdf, mols, conformers=False)
        except Exception as e:
            self.logger.error(f"Failed to save input molecules to SDF: {e}")
            if cleanup:
                try:
                    shutil.rmtree(work_dir)
                except Exception as cleanup_e:
                    self.logger.warning(f"Failed to clean up temporary directory: {cleanup_e}")
            for mol in mols:
                for isomer in mol.molecules:
                    smiles = isomer.to_smiles()
                    mw = Descriptors.HeavyAtomMolWt(Chem.MolFromSmiles(smiles))
                    isomer.set_tag("docking_score", 0.0)
                    isomer.set_tag("Mol_Wt", mw)
            self.out.send(mols)
            return
        cmd_parts = [
            self.runnable['run_gold'],
            '--p', str(protein_file),
            '--l', str(ligand_sdf),
            '--o', str(work_dir),
            '--ndocking', str(ndocking),
            '--scoring_function', scoring_function,
            '--binding_site_mode', binding_site_mode,
            '--binding_site_radius', str(binding_site_radius)

        ]
        if ref_ligand is not None:
            cmd_parts.extend(['--r', str(ref_ligand)])
        if prepare_protein:
            cmd_parts.append('--prepare_protein')
        if binding_site_mode == 'from_residues' and binding_site_residues:
            cmd_parts.extend(['--residues', binding_site_residues])
        command = ' '.join(cmd_parts)
        self.logger.info(f"Running GOLD docking with command: {command}")
        res = self.run_command(command)


        result_mols = []
        scores = []
        

        if res.stdout:
            stdout_str = res.stdout.decode('utf-8')
            self.logger.info(f"Command output: {stdout_str}")
            
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
                scores = [0.0] * len(mols)
            
            # Attach scores to molecules as tags    
            for i, mol in enumerate(mols):
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
                    
            if cleanup:
                try:
                    shutil.rmtree(work_dir, ignore_errors=True)
                except Exception as cleanup_e:
                    self.logger.warning(f"Failed to clean up temporary directory: {cleanup_e}")
        self.logger.info(f"Returning {len(result_mols)} molecules with docking scores batch id {batch_id}")
        self.out.send(result_mols)
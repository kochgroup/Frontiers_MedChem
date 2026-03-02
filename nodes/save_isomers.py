

from maize.core.interface import Input, Output, Parameter, FileParameter, Suffix, Flag, MultiInput
from maize.core.node import Node

from maize.utilities.chem import (IsomerCollection, save_sdf_library)
from maize.steps.mai.molecule import SaveMolecule
from typing import Annotated


from pathlib import Path


class SaveIsomers(Node):
    """Save a list of molecules to a single SDF file."""

    tags = {"chemistry", "utility", "saving"}

    inp: Input[list[IsomerCollection]] = Input()
    """Molecule library input"""

    file: FileParameter[Annotated[Path, Suffix("sdf")]] = FileParameter(exist_required=False)
    """Location of the SDF library file"""

    append: Flag = Flag(default=False)
    """Whether to append to the file instead of overwriting"""
    out: Output[Path] = Output()

    def run(self) -> None:
        mols = self.inp.receive()
        save_sdf_library(self.file.filepath, mols, conformers=False, append=self.append.value)
        self.logger.info("Saved %s molecules to %s", len(mols), self.file.filepath)
        self.out.send(self.file.filepath)
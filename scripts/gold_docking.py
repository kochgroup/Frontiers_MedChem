from ccdc.docking import Docker
from ccdc.io import MoleculeReader, EntryReader
from ccdc import conformer
from ccdc.io import MoleculeWriter
from ccdc.protein import Protein
import tempfile
import argparse
import os

def _prepare_protein(protein_file, output_dir):
    protein = Protein.from_file(protein_file)
    protein.remove_all_waters()
    protein.remove_unknown_atoms()
    protein.add_hydrogens()
    for lig in protein.ligands:
        protein.remove_ligand(lig)
    prep_path = os.path.join(output_dir, 'prepared_protein.mol2')
    with MoleculeWriter(prep_path) as w:
        w.write(protein)
    return prep_path

def gold_docking(protein_file, ligand_file, output_dir, ndocking=10, scoring_function='plp',prepare_protein = False, binding_site_mode = 'from_ligand',  ref_ligand_file = None, binding_site_residues = None,binding_site_radius = 8 ):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    if prepare_protein:
        print("Preparing protein...")
        protein_file = _prepare_protein(protein_file, output_dir)
        print(f"Protein prepared and saved to {protein_file}")
    else:
        protein_path = protein_file
    # Read reference ligand and protein once
    #ref_ligand_mol = MoleculeReader(ref_ligand_file)[0]
    #protein_mol = MoleculeReader(protein_file)[0]
    
    # Read all entries from the ligand file
    try:
        ligand_entries = list(EntryReader(ligand_file))
        print(f"Found {len(ligand_entries)} molecules in {ligand_file}")
    except Exception as e:
        print(f"Error reading molecules from {ligand_file}: {e}")
        return [0.0]
    
    fitness_scores = []
    
    # Process each molecule (whatever number you have)
    for i, ligand_entry in enumerate(ligand_entries):
        try:
            print(f"Processing molecule {i+1}/{len(ligand_entries)}")
            
            # Prepare the ligand
            lig_prep = Docker.LigandPreparation()
            lig_prep.add_hydrogens = True
            lig_prep.add_charges = True
            lig_prep.add_torsions = True
            
            prep_lig = lig_prep.prepare(ligand_entry)
            
            # Write the prepared molecule to a temporary file
            prep_ligand_path = os.path.join(output_dir, f'prep_ligand_{i}.mol2')
            with MoleculeWriter(prep_ligand_path) as w:
                w.write(prep_lig.molecule)
               
            # Set up docking for this molecule
            docking = Docker()
            settings = docking.settings
            settings.add_ligand_file(prep_ligand_path, ndocks=ndocking)
            settings.add_protein_file(protein_file)
            settings.torsion_distribution_file = '/appl/ccdc/CSDS2022/Discovery_2022/GOLD/gold/gold.tordist'

            protein_obj = settings.proteins[0]
            if binding_site_mode=='from_residues' and binding_site_residues:

                residue = [res for res in protein_obj.residues if res.identifier in binding_site_residues][0]
                if not residue:
                    raise ValueError(f"No residues found matching identifiers: {binding_site_residues}. Format should be e.g., A:HIS123 or HIS123.")
                settings.binding_site = settings.BindingSiteFromResidue(protein_obj, residue, binding_site_radius)
            else:
                if not ref_ligand_file:
                    raise ValueError("Reference ligand file must be provided when using 'from_ligand' binding site mode.")
                ref_ligand_mol = MoleculeReader(ref_ligand_file)[0]

                settings.binding_site = settings.BindingSiteFromLigand(protein_obj, ref_ligand_mol, binding_site_radius)
            settings.fitness_function = scoring_function
            settings.autoscale = 10.
            
            # Set up output
            #batch_tempdir = tempfile.mkdtemp()
            #settings.output_directory = batch_tempdir
            #settings.output_file = f'docked_ligands_{i}.mol2'
            mol_output_dir = os.path.join(output_dir, f'mol_{i}')
            os.makedirs(mol_output_dir, exist_ok=True)
            settings.output_directory = mol_output_dir
            settings.output_file = 'docked_ligands.mol2'
            # Run docking
            result = docking.dock()
            
            # Process results
            batch_conf_file = settings.conf_file
            result_settings = Docker.Settings.from_file(batch_conf_file)
            results = Docker.Results(result_settings)
            ligands = result.ligands
            
            if ligands and len(ligands) > 0:
                fitness = ligands[0].fitness(settings.fitness_function)
                fitness_scores.append(fitness)
                print(f"Molecule {i+1} fitness score: {fitness}")
            else:
                fitness_scores.append(0.0)
                print(f"No docked poses found for molecule {i+1}, using score 0.0")
                
        except Exception as e:
            print(f"Error docking molecule {i+1}: {e}")
            fitness_scores.append(0.0)
    
    # If no molecules were successfully docked, return a default score
    if not fitness_scores:
        fitness_scores = [0.0]
    
    # Print all scores in a format that can be parsed
    print(f"Fitness scores: {','.join(str(score) for score in fitness_scores)}")
    return fitness_scores

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Dock multiple molecules using GOLD.")
    parser.add_argument('--p', type=str, required=True, help="Path to the protein file.")
    parser.add_argument('--l', type=str, required=True, help="Path to the ligand file (SDF with multiple molecules).")
    parser.add_argument('--o', type=str, required=True, help="Path to the output directory.")
    parser.add_argument('--ndocking', type=int, default=10, help="Maximum number of docking runs.")
    parser.add_argument('--scoring_function', type=str, default='plp', help="Scoring function to use.")
    parser.add_argument('--prepare_protein', action='store_true', help="Whether to prepare the protein by adding hydrogens and removing waters.")
    parser.add_argument('--binding_site_mode', type=str, default='from_ligand', choices=['from_ligand', 'from_residues'], help="Method to define the binding site.")
    parser.add_argument('--residues', type=str, help="Comma-separated list of residue identifiers for 'from_residues' binding site mode (e.g., A:HIS123,A:ASP45).")
    parser.add_argument('--r', type=str, default=None, help="Path to the reference ligand file.")
    parser.add_argument('--binding_site_radius', type=float, default=8.0, help="Radius for defining the binding site around the reference ligand (in Angstroms).")

    args = parser.parse_args()
    if args.binding_site_mode == 'from_residues' and not args.residues:
        parser.error("The --residues argument is required when using 'from_residues' binding site mode.")
    if args.binding_site_mode == 'from_ligand' and not args.r:
        parser.error("The --r argument is required when using 'from_ligand' binding site mode.")

    scores = gold_docking(args.p, args.l, args.o, args.ndocking, args.scoring_function, args.prepare_protein, args.binding_site_mode, args.r, args.residues, args.binding_site_radius)

    print(f"Fitness scores: {','.join(str(score) for score in scores)}")
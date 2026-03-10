from ccdc.docking import Docker
from ccdc.io import MoleculeReader, EntryReader
from ccdc import conformer
from ccdc.io import MoleculeWriter
from ccdc.protein import Protein
import tempfile
import argparse
import os



def gold_docking(protein_file, ref_ligand_file, ligand_file, output_dir, ndocking=10, scoring_function='plp'):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Read reference ligand and protein once
    ref_ligand_mol = MoleculeReader(ref_ligand_file)[0]
    protein_mol = MoleculeReader(protein_file)[0]
    
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
            settings.torsion_distribution_file = '/appl/ccdc/CSDS2022/Discovery_2022/GOLD/gold/gold.tordist'  ### that might need to be changed depending on your GOLD installation
            settings.binding_site = settings.BindingSiteFromLigand(protein_mol, ref_ligand_mol, 8)
            settings.fitness_function = scoring_function
            settings.autoscale = 10.
            
            # Set up output
            batch_tempdir = tempfile.mkdtemp()
            settings.output_directory = batch_tempdir
            settings.output_file = f'docked_ligands_{i}.mol2'
            
            # Run docking
            result = docking.dock()
            
            # Process results
            batch_conf_file = settings.conf_file
            settings = Docker.Settings.from_file(batch_conf_file)
            results = Docker.Results(settings)
            ligands = results.ligands
            
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
    parser.add_argument('--r', type=str, required=True, help="Path to the reference ligand file.")
    parser.add_argument('--l', type=str, required=True, help="Path to the ligand file (SDF with multiple molecules).")
    parser.add_argument('--o', type=str, required=True, help="Path to the output directory.")
    parser.add_argument('--ndocking', type=int, default=10, help="Maximum number of docking runs.")
    parser.add_argument('--scoring_function', type=str, default='plp', help="Scoring function to use.")

    args = parser.parse_args()
    
    scores = gold_docking(args.p, args.r, args.l, args.o, args.ndocking, args.scoring_function)

    print(f"Fitness scores: {','.join(str(score) for score in scores)}")
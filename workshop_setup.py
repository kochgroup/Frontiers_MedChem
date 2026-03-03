import os 

import os
import site

def init_workshop_environment():
    """Sets up the required environment variables for the CSD Python API and REINVENT4."""
    
    # 1. Fix the CCDC Mogul Initialization Path
    try:
        # Find the active conda environment's site-packages
        current_env_site_packages = site.getsitepackages()[0]
        correct_mogul_path = os.path.join(current_env_site_packages, 'ccdc', 'parameter_files', 'mogul.ini')
        
        # Force overwrite any global .bashrc settings
        os.environ['CCDC_MOGUL_INITIALISATION_FILE'] = correct_mogul_path
    except Exception as e:
        print(f"Warning: Could not configure CCDC Mogul path. {e}")

    MAIN_DIR = os.path.dirname(os.path.abspath(__file__))
    os.chdir(MAIN_DIR)  # Ensure we're in the main directory for relative paths to work
    # 2. Fix the LD_LIBRARY_PATH for C++ binaries (prevents REINVENT4/Tensorboard crashes)
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        conda_lib = os.path.join(conda_prefix, "lib")
        old_path = os.environ.get("LD_LIBRARY_PATH", "")
        
        # Only inject it if it isn't already there
        if conda_lib not in old_path:
            os.environ["LD_LIBRARY_PATH"] = f"{conda_lib}:{old_path}" if old_path else conda_lib
    else:
        print("Warning: CONDA_PREFIX not found. Are you running this inside a Conda environment?")

# Automatically run the setup the moment this script is imported
init_workshop_environment()
print("Workshop environment variables successfully configured!")
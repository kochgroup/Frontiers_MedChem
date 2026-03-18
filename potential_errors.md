## 🛠️ 1. Installation & Environment Errors

### Error: Missing C++ ABI
> `ImportError: /lib64/libstdc++.so.6: version 'CXXABI_1.3.15' not found`

**Why it happens:** Your operating system's default C++ compiler libraries are too old for the newer Python packages we are using.
**Solution:** 
   1. Install the updated libraries directly into your conda environment:
   ```bash
   conda install -c conda-forge libstdcxx-ng libgcc-ng
   ```
   2. If it is already installed and still failing, you need to explicitly tell your system where to look by exporting the library path. Run this in your terminal:
   ```bash
   export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
   ```
### Error: Maize bad interpreter
> `/nfs/home/myuecel3/miniforge3/envs/frontiers_medchem/bin/maize: /nfs/home/myuecel3/miniforge3/envs/frontiers_medchem/bin/python3.14: bad interpreter: No such file or directory`

**Why it happens:** The maize command is trying to use a Python interpreter path that doesn't exist (sometimes caused by moving conda environments).

**Solution:** 
   1. Reinstall the Maize packages to force them to link to your current active Python interpreter.
   ```bash
   pip uninstall -y maize maize-contrib
   pip install git+https://github.com/MolecularAI/maize.git
   pip install git+https://github.com/MolecularAI/maize-contrib.git
   ```
## 2. REINVENT4 Errors 

### Error: Tensorboard pkg_resources
> ` ModuleNotFoundError: No module named 'pkg_resources' (when running Tensorboard)`   

**Why it happens:** Newer versions of the setuptools Python package completely removed the legacy pkg_resources module, but Tensorboard still looks for it.

**Solution:**  
   1. Downgrade setuptools to a compatible version:
   ```bash
   pip install "setuptools<82"
   ```
### Error: Pydantic erros
> `pydantic errors "pydantic_core._pydantic_core.ValidationError: 1 validation error for Parameters" and "maize.utilities.execution.ProcessError: Command /nfs/home/myuecel3/miniforge3/envs/frontiers_medchem/bin/python /nfs/home/myuecel3/miniforge3/envs/frontiers_medchem/bin/reinvent --log-filename reinvent.log -f toml config.toml failed with returncode 1"`

**Why it happens:** There is a slight mismatch between what the newest version of REINVENT expects and what Maize is sending it in the background configuration.

**Solution:** 
   1. We need to manually add one line of code to Maize's internal Python files.
   * Open this specific file in your text editor (note that $CONDA_PREFIX represents the path to your conda environment):
   > `$CONDA_PREFIX/lib/python3.10/site-packages/maize/steps/mai/misc/reinvent.py`
   * Find the _path_config function.
   * Add the "property": "predictions" line to the score_conf dictionary so it looks exactly like this:
   ```python
   score_conf = {
     "name": "maize",
     "weight": weight,
     "params": {
         "executable": "./intercept.py",
         "args": "",
         "property": "predictions",  # <--- ADD THIS EXACT LINE
     }
   }
   ```

## 3. CSD Python API (GOLD) Errors

### Error: Mogul Initialisation Error

**Why it happens:** The CCDC API doesn't always automatically know where the main CSDS software suite was installed on your machine.
**Solution:** 
   1. You need to point the API to your local installation paths by setting environment variables in your Python script or Jupyter Notebook.Add this block to the very top of your docking script/notebook:
   (⚠️ CRITICAL: You must change the GOLD_DIR and CCDC_MOGUL_DATA paths below to match exactly where CCDC is installed on YOUR specific machine!)
   ```python
   import os
   # 1. Point to the Mogul initialization file inside your active conda environment
   os.environ['CCDC_MOGUL_INITIALISATION_FILE'] = os.path.expandvars('$CONDA_PREFIX/lib/python3.10/site-packages/ccdc/parameter_files/mogul.ini')

   # 2. Point to your local CCDC suite installations (REPLACE THESE PATHS WITH YOUR OWN!)
   os.environ['GOLD_DIR'] = '/path/to/your/local/ccdc/CSDS2022/Discovery_2022/GOLD'
   os.environ['CCDC_MOGUL_DATA'] = '/path/to/your/local/ccdc/CSDS2022/CSD_2022/data'
   ```
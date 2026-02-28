Potential Installation Errors:
- ImportError: /lib64/libstdc++.so.6: version `CXXABI_1.3.15' not found (required by /nfs/home/myuecel3/miniforge3/envs/frontiers_medchem/lib/python3.10/lib-dynload/../.././libicui18n.so.78)
Solution: This error indicates that the required version of the C++ ABI (Application Binary Interface) is not found. To resolve this issue, you can try the following steps:
1. you can install the libstdcxx-ng libgcc-ng with this command 'conda install -c conda-forge libstdcxx-ng libgcc-ng' or with mamba 'mamba install -c conda-forge libstdcxx-ng libgcc-ng'
2. If the above step does not resolve the issue or already installed, you may need to export LD_LIBRARY_PATH to include the path to the correct version of libstdc++.so.6. You can do this by running the following command in your terminal:
   export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
- command maize --help
   error message bash: /nfs/home/myuecel3/miniforge3/envs/frontiers_medchem/bin/maize: /nfs/home/myuecel3/miniforge3/envs/frontiers_medchem/bin/python3.14: bad interpreter: No such file or directory
Solution: This error indicates that the maize command is trying to use a Python interpreter that does not exist. To resolve this issue, you can try the following steps:
1. reinstall the maize package using pip or conda to ensure that it is correctly installed and linked to the correct Python interpreter. You can do this by running the following command in your terminal:
   pip uninstall -y maize
   pip install git+https://github.com/MolecularAI/maize-contrib.git

Reinvent Errors:
- tensorboard error "no module named pkg_resources"
Solution: This error indicates that the pkg_resources module is not found. To resolve this issue, you can try the following steps:
1. pip install "setuptools<82"
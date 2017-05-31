import os
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "../version")) as fi:
    __version__ = fi.read().strip()

models_list =  ["Liem2016__OCI_norm", "Liem2016__full_2samp_training"]

__changes__ = """
* 0.1.4.dev: circleci integration
* 0.1.3.dev: hotfixed long behavior
* 0.1.2.dev: fixed long behavior
* 0.1.1.dev: renamed package
"""

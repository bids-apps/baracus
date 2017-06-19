import os
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(dir_path, "../version")) as fi:
    __version__ = fi.read().strip()

models_list =  ["Liem2016__OCI_norm", "Liem2016__full_2samp_training"]

__changes__ = """
* 0.9.4: fixed models in brain_age_files
* 0.9.3: fix tagging issue
* 0.9.2: fixed typo, -v flag

"""

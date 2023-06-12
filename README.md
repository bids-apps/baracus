# BARACUS: Brain-Age Regression Analysis and Computation Utility Software

[![CircleCI](https://circleci.com/gh/BIDS-Apps/baracus.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/BIDS-Apps/baracus)
[![DOI](https://zenodo.org/badge/93560323.svg)](https://zenodo.org/badge/latestdoi/93560323)

This [BIDS App](http://bids-apps.neuroimaging.io/) predicts brain age,
based on data from Freesurfer 5.3.
It combines data from cortical thickness, cortical surface area, and
subcortical information (see Liem et al., 2017).

## Requirements
Your data has to be organized according to the
[BIDS standard](http://bids.neuroimaging.io) and each subject needs at
least one T1w image.
In a first step, BARACUS runs [FreeSurfer's](http://freesurfer.net)
`recon-all` command and saves the output in `{out_dir}/freesurfer/`
If the data has previously been analyzed with FreeSurfer version 5.3.0,
and BARACUS finds them in `--freesurfer_dir` this step is skipped.

**Important:** if you use previously processed FreeSurfer data

1. the data has to be preprocessed with
Freesurfer's 5.3.0 installation, not the 5.3.0-HCP installation;
2. FreeSurfer data needs to be BIDS-formatted, i.e. subject folders
should be named *sub-<subject_label>*, (e.g., sub-01, sub-02...)

**Also important:** if you are comparing groups regarding brain-age,
make sure that the groups are well matched (e.g. regarding ethnicity;
see [here](https://github.com/BIDS-Apps/baracus/issues/10)).

## Acknowledgements
If you use BARACUS in your work please cite:

1. Liem et al. (2017),
1. the [zenodo DOI](https://zenodo.org/badge/latestdoi/93560323)
of the BARACUS version you used, and
1. The [FreeSurfer tool](https://surfer.nmr.mgh.harvard.edu/fswiki/FreeSurferMethodsCitation)

Liem et al. (2017). Predicting brain-age
from multimodal imaging data captures cognitive impairment.
Neuroimage, 148:179–188,
[doi: 10.1016/j.neuroimage.2016.11.005](http://www.sciencedirect.com/science/article/pii/S1053811916306103).
[\[preprint\]](http://www.biorxiv.org/content/early/2016/11/07/085506)


## Models
**Liem2016__OCI_norm**: Model trained on subjects that have no
objective cognitive impairment (OCI) (*OCI norm* in Liem et al., 2017).
Sample: N = 1166, 566f/600m, age: M = 59.1, SD = 15.2, 20-80y

**Liem2016__full_2samp_training**: Model trained on subjects that have no
objective cognitive impairment (OCI) (*full LIFE 2sample training* in Liem et al., 2017).
Sample: N = 2377, 1133f/1244m, age: M=58.4, SD=15.4, 18-83y;
containing data from the LIFE and NKI studies.

Models were trained as part of Liem et al. (2017) and the training code is available
[here](https://github.com/fliem/LeiCA_LIFE).

## Modes
It can be run in **BIDS mode** (recommended) and in in **FILE mode**.

In BIDS mode the input is a BIDS formatted Freesurfer folder.

In FILE mode the input is provided as surface and aseg files.
Surface files need to be sampled to fsaverage4 space,
aseg files extracted via asegstats2table.




## BIDS mode
### Example
These examples demonstrate how to run the `bids/baracus` docker container.
For a brief introduction how to run BIDS Apps see
[this site](http://bids-apps.neuroimaging.io/tutorial/).
In the examples `/project/bids_sourcedata` and
`/project/baracus` are directories on your hard drive, which are mapped
into the docker container directories `/data/in` and `/data/out`,
respectively, via the `-v` flag.

#### Participants

    docker run -ti --rm \
    -v /project/bids_sourcedata/:/data/in \
    -v /project/baracus:/data/out \
    bids/baracus /data/in /data/out participant \
    --license_key "XX"

#### Group

    docker run -ti --rm \
    -v /project/bids_sourcedata/:/data/in \
    -v /project/baracus:/data/out \
    bids/baracus /data/in /data/out group \
    --license_key "XX"

#### Participants with previously processed FreeSurfer data
If FreeSurfer data is already available, for example at
`/project/freesurfer/` running the follwing command will use the
previously processed data:

    docker run -ti --rm \
    -v /project/bids_sourcedata/:/data/in \
    -v /project/freesurfer/:/data/freesurfer \
    -v /project/baracus:/data/out \
    bids/baracus /data/in /data/out participant \
    --license_key "XX" --freesurfer_dir /data/freesurfer

### Usage

    usage: run_brain_age_bids.py [-h]
                                 [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                                 [--freesurfer_dir FREESURFER_DIR]
                                 [--models {Liem2016__OCI_norm,Liem2016__full_2samp_training} [{Liem2016__OCI_norm,Liem2016__full_2samp_training} ...]]
                                 --license_key LICENSE_KEY [--n_cpus N_CPUS] [-v]
                                 bids_dir out_dir {participant,group}

    BARACUS: Brain-Age Regression Analysis and Computation Utility Software. BIDS
    mode. You specify a BIDS-formatted freesurfer folder as input. All data is
    extracted automatiacally from that folder.

    positional arguments:
      bids_dir              The directory with the input dataset formatted
                            according to the BIDS standard.
      out_dir               Results are put into {out_dir}/baracus.
      {participant,group}   Level of the analysis that will be performed.
                            "participant": predicts single subject brain age,
                            "group": collects single subject predictions.

    optional arguments:
      -h, --help            show this help message and exit
      --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                            The label of the participant that should be analyzed.
                            The label corresponds to sub-<participant_label> from
                            the BIDS spec (so it does not include "sub-"). If this
                            parameter is not provided all subjects should be
                            analyzed. Multiple participants can be specified with
                            a space separated list.
      --freesurfer_dir FREESURFER_DIR
                            Folder with FreeSurfer subjects formatted according to
                            BIDS standard. If subject's recon-all folder cannot be
                            found, recon-all will be run. If not specified
                            freesurfer data will be saved to {out_dir}/freesurfer
      --models {Liem2016__OCI_norm,Liem2016__full_2samp_training} [{Liem2016__OCI_norm,Liem2016__full_2samp_training} ...]
      --skip_missing        Flag to skip not segmented subjects
      --license_key LICENSE_KEY
                            FreeSurfer license key - letters and numbers after "*"
                            in the email you received after registration. To
                            register (for free) visit
                            https://surfer.nmr.mgh.harvard.edu/registration.html
      --n_cpus N_CPUS       Number of CPUs/cores available to use.
      -v, --version         show program's version number and exit



## FILE mode
### Example
    docker run -ti --rm \
    -v /project/data/:/data/in \
    -v /project/out:/data/out \
    --entrypoint=run_brain_age_files.py \
    bids/baracus /data/out \
    --lh_thickness_file /data/in/s01/lh.thickness.mgh \
    --rh_thickness_file /data/in/s01/rh.thickness.mgh \
    --lh_area_file /data/in/s01/lh.area.mgh \
    --rh_area_file /data/in/s01/rh.area.mgh \
    --aseg_file /data/in/s01/aseg.txt


### Usage
    usage: run_brain_age_files.py [-h] [--participant_label PARTICIPANT_LABEL]
                                  [--models {Liem2016__OCI_norm,Liem2016__full_2samp_training} [{Liem2016__OCI_norm,Liem2016__full_2samp_training} ...]]
                                  --lh_thickness_file LH_THICKNESS_FILE
                                  --rh_thickness_file RH_THICKNESS_FILE
                                  --lh_area_file LH_AREA_FILE --rh_area_file
                                  RH_AREA_FILE --aseg_file ASEG_FILE
                                  out_dir

    BARACUS: Brain-Age Regression Analysis and Computation Utility Software. Files
    mode. You specify lh/rh thickness/area + aseg file (with
    --lh_thickness_file...). Surface files need to be sampled to fsaverage4 space,
    aseg files extracted via asegstats2table. Only one subject can be specified at
    a time.

    positional arguments:
      out_dir               Results are put here.

    optional arguments:
      -h, --help            show this help message and exit
      --participant_label PARTICIPANT_LABEL
                            will be written into output files and can be omitted
      --models {Liem2016__OCI_norm,Liem2016__full_2samp_training} [{Liem2016__OCI_norm,Liem2016__full_2samp_training} ...]
      --lh_thickness_file LH_THICKNESS_FILE
      --rh_thickness_file RH_THICKNESS_FILE
      --lh_area_file LH_AREA_FILE
      --rh_area_file RH_AREA_FILE
      --aseg_file ASEG_FILE

# BARACUS: Brain-Age Regression Analysis and Computation Utility Software

This package predicts brain age, based on data from Freesurfer 5.3.
It combines data from cortical thickness, cortical surface area, and
subcortical information (see Liem et al., 2017).


Liem et al. (2017). Predicting brain-age
from multimodal imaging data captures cognitive impairment.
Neuroimage, 148:179–188,
[doi: 10.1016/j.neuroimage.2016.11.005](http://www.sciencedirect.com/science/article/pii/S1053811916306103).
[\[preprint\]](http://www.biorxiv.org/content/early/2016/11/07/085506)


## Requirements
Before age prediction can be performed, [FreeSurfer's](http://freesurfer.net)
`recon-all` command has to be run with Freesurfer version 5.3.
Freesurfer data has to be in [BIDS format](http://bids.neuroimaging.io),
i.e. subject folders should be named
*sub-<subject_label>*, (e.g., sub-01, sub-02...).

## Models
**Liem2016__OCI_norm**: Model trained on subjects that have no
objective cognitive impairment (OCI) (*OCI norm* in Liem et al., 2017).
Sample: N = 1166, 566f/600m, age: M = 59.1, SD = 15.2, 20-80y

**Liem2016__full_2samp_training**: Model trained on subjects that have no
objective cognitive impairment (OCI) (*full LIFE 2sample training* in Liem et al., 2017).
Sample: N = 2377, 1133f/1244m, age: M=58.4, SD=15.4, 18-83y;
containing data from the LIFE and NKI studies.




## Modes
It can be run in **BIDS mode** and in in **FILE mode**.

In BIDS mode the input is a BIDS formatted Freesurfer folder.

In FILE mode the input is provided as surface and aseg files.
Surface files need to be sampled to fsaverage4 space,
aseg files extracted via asegstats2table.





## BIDS mode
### Example
Participants

    docker run -ti --rm \
    -v /project/freesurfer/:/data/in \
    -v /project/out:/data/out \
    bids/baracus /data/in /data/out participant

Group

    docker run -ti --rm \
    -v /project/freesurfer/:/data/in \
    -v /project/out:/data/out \
    bids/baracus /data/in /data/out group

### Usage

    usage: run_brain_age_bids.py [-h]
                                 [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                                 [--models {Liem2016__OCI_norm,Liem2016__full_2samp_training} [{Liem2016__OCI_norm,Liem2016__full_2samp_training} ...]]
                                 freesurfer_dir out_dir {participant,group}

    BARACUS: Brain-Age Regression Analysis and Computation Utility Software. BIDS
    mode. You specify a BIDS-formatted freesurfer folder as input. All data is
    extracted automatiacally from that folder.

    positional arguments:
      freesurfer_dir        Folder with freesurfer subjects formatted according to
                            BIDS standard.
      out_dir               Results are put here.
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
      --models {Liem2016__OCI_norm,Liem2016__full_2samp_training} [{Liem2016__OCI_norm,Liem2016__full_2samp_training} ...]



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

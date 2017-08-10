FROM bids/base_validator:latest

RUN apt-get update \
    && apt-get install -y wget tcsh

RUN wget -qO- https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/5.3.0/freesurfer-Linux-centos6_x86_64-stable-pub-v5.3.0.tar.gz | tar zxv -C /opt \
  --exclude='freesurfer/trctrain' \
  --exclude='freesurfer/subjects/fsaverage_sym' \
  --exclude='freesurfer/subjects/fsaverage3' \
  --exclude='freesurfer/subjects/fsaverage5' \
  --exclude='freesurfer/subjects/fsaverage6' \
  --exclude='freesurfer/subjects/cvs_avg35' \
  --exclude='freesurfer/subjects/cvs_avg35_inMNI152' \
  --exclude='freesurfer/subjects/bert' \
  --exclude='freesurfer/subjects/V1_average' \
  --exclude='freesurfer/average/mult-comp-cor' \
  --exclude='freesurfer/lib/cuda' \
  --exclude='freesurfer/lib/qt'


RUN /bin/bash -c 'touch /opt/freesurfer/.license'

ENV OS=Linux
ENV FS_OVERRIDE=0
ENV FIX_VERTEX_AREA=
ENV SUBJECTS_DIR=/opt/freesurfer/subjects
ENV FSF_OUTPUT_FORMAT=nii.gz
ENV MNI_DIR=/opt/freesurfer/mni
ENV LOCAL_DIR=/opt/freesurfer/local
ENV FREESURFER_HOME=/opt/freesurfer
ENV FSFAST_HOME=/opt/freesurfer/fsfast
ENV MINC_BIN_DIR=/opt/freesurfer/mni/bin
ENV MINC_LIB_DIR=/opt/freesurfer/mni/lib
ENV MNI_DATAPATH=/opt/freesurfer/mni/data
ENV FMRI_ANALYSIS_DIR=/opt/freesurfer/fsfast
ENV PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
ENV MNI_PERL5LIB=/opt/freesurfer/mni/lib/perl5/5.8.5
ENV PATH=/opt/freesurfer/bin:/opt/freesurfer/fsfast/bin:/opt/freesurfer/tktools:/opt/freesurfer/mni/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH

RUN sudo apt-get update && apt-get install -y tree htop unzip
RUN sudo apt-get update && apt-get install -y tcsh
RUN sudo apt-get update && apt-get install -y bc
RUN sudo apt-get update && apt-get install -y tar libgomp1 perl-modules

# make freesurfer python scripts python3 ready
RUN 2to3-3.4 -w $FREESURFER_HOME/bin/aparcstats2table
RUN 2to3-3.4 -w $FREESURFER_HOME/bin/asegstats2table
RUN 2to3-3.4 -w $FREESURFER_HOME/bin/*.py

# download models
RUN mkdir /code
RUN wget -qO models.zip https://www.dropbox.com/s/5xbqw8i2e7x0g02/models.zip?dl=0 && \
unzip models.zip && mv models /code/ && rm models.zip

# freesurfer repo
RUN wget https://github.com/bids-apps/freesurfer/archive/v6.0.0-5.tar.gz && \
tar xfz v6.0.0-5.tar.gz && rm -r v6.0.0-5.tar.gz && \
cd freesurfer-6.0.0-5 && mv run.py /code/run_freesurfer.py
# since we are using freesurfer-bids-app-run-code from FS6 and we run it with FS5.3,
# we need to remove the parallel flag of recon-all
RUN sed -e "s/-parallel //g" -i /code/run_freesurfer.py
RUN echo "FS5.3_BIDSAPPv6.0.0-5" > /code/version
ENV PATH=/code:$PATH


# Install anaconda
RUN echo 'export PATH=/usr/local/anaconda:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.continuum.io/archive/Anaconda3-4.2.0-Linux-x86_64.sh -O anaconda.sh && \
    /bin/bash anaconda.sh -b -p /usr/local/anaconda && \
    rm anaconda.sh

ENV PATH=/usr/local/anaconda/bin:$PATH

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8


RUN pip install nibabel
RUN pip install pybids
RUN pip install duecredit


COPY . /code/
RUN cd /code && ls && pip install -e .



ENTRYPOINT ["run_brain_age_bids.py"]

#############
Basic running
#############

The code works by a single script, ``run_suite.py`` which acts as the hub for the running of the code. There are several different modes the code can be run in, but within each mode, there are common options that are used, so most commands will look very similar except for minor differences.

Options that are always required is the analysis name and the working directory. The Analysis name is coded to many input files and configs specific to the analysis one is doing and the working directory is teh common place where output files are saved.

Below, each mode is describe in more depth. An important note is the output of each step flows into the other. One needs the output from ``analyze`` to run ``mva`` and one needs the output of ``mva`` to run ``plotting``

***********************
Analysis (``analyze``)
***********************

.. note::

    This is part of the code is a work in progress

Analyze runs the analysis code on the skimmed NanoAOD samples. This code works using ``farmoutAnalysisJobs`` which is a wisconsin specific script, so this is something that MUST be run on the ``login.hep.wisc.edu`` machines. Other steps can be run from any cmssw area.

Farmout works by either sending jobs based on a list of files or a directory in the hdfs area and a run file. Because of this, the analysis suite needs no python processing to setup the job like the rest of the suite, and thus the code is only the c++ files full of the TSelector. The actual run file is the ``analyze.py`` file.

One thing extremely important for processing using this framework: because very little can be sent as info to these jobs, the directories of the input files expresses information about the job. So in the eos area, the directory you run over MUST be in the format: ``<Analysis>_<Year>_<Optional Name>`` with the optional name as a way to identify info about the skim used or other info. The output files will be in a directory called ``<Analysis>_<Year>_<Optional Name>-analyze``.

*********************
BDT runner (``mva``)
*********************

Mva (probably misnamed) runs the code for training the BDT for samples. This portion of the code takes the newly made ntuples from the output of the ``analyze`` step and takes care of the rest of the processing, calculating any ancillary variables i.e. variables not directly used in the event selection such as centrality. The variables included in the training are kept in ``inputs.py`` and the functions that are used to create the variables are stored in ``commons/python/awkward_commons.py``.

The code has the ability to run in a binary mode and a multiclass mode which is also decided in the ``inputs.py`` file. NOTE: currently, the code does not store info about the ``inputs.py`` file, so it is possible to change the mode of the file after running and causing unexpected behavior. Hopefully a fix will come soon.

Mva also takes care of the weighting that is used for the plotting (and is one reason why it is needed to be done before the plotting). 

*******************
Plotting (``plot``)
*******************

Plotting

***************************
Setup Combine (``combine``)
***************************

.. note::

    This is part of the code is a work in progress

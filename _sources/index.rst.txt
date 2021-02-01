.. Analysis Suite documentation master file, created by
   sphinx-quickstart on Fri Jan 29 08:21:39 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Installation Guide
==================

This area requires python3 for all python scripts as well as ROOT, so you need to be in a CMSSW area with ROOT 6.20 or greater. At time of writing, ``CMSSW_11_2_0_pre`` fits the bill. You will also have to have certain packages not default for

.. code-block:: bash

   # Generic Area Setup
   cmsrel CMSSW_11_2_0_pre9
   cd CMSSW_11_2_0_pre9/src
   cmsenv
   git clone https://github.com/dteague/Analysis_suite
   cd analysis_suite

   # Building
   python3 -m pip install --user requirements.txt
   scram b -j 4

**Note**: After you scram, the python will compile, but this is not needed, it is also compiled at run time. Scram just sets up the links, so scram is not needed whenever python code is changed after the first run. HOWEVER, scram is needed to compile the cpp code!

Quick Start
===========

The code has several modes: ``analysis``, ``mva``, ``plot``, and ``combine``. There are many options needed for the code to run, and it is detailed more in the running section of this tutorial. The main options needed for all running is the analysis which corresponds to the cpp code used for analysis as well as the fileInfo used for getting sample information, and the Work Directory or where all the output files will be saved

.. code-block:: bash

   ./run_suite.py <mode> -a <Analysis> -d <Work Directory>

Or if you need more information, just run ``./run_suite.py --help``


Welcome to Analysis Suite's documentation!
==========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self
   code

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

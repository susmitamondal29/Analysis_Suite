import os
uwlogin = "uwlogin" in os.environ["HOSTNAME"] 
uw = "hep.wisc.edu" in os.environ["HOSTNAME"] 
info = {
    "DYm50" : {
        "file_path" : "/store/user/kelong/DileptonNanoSkims/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NanoPostprocessing-v2/*/*/*.root",
        "plot_group" : "dy"
    },
    "ttbar" : {
        # Don't do *.root because ROOT (e.g., TChain) can't handle this
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/TTTo2L2Nu_TuneCUETP8M2_ttHtranche3_13TeV-powheg-pythia8/*/*/*.root",
        "plot_group" : "ttbar"
    },
    "data_DoubleEG_Run2016B_ver2-Nano14Dec2018_ver2-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleEG/Run2016B_ver2-Nano14Dec2018_ver2-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleEG_Run2016C-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleEG/Run2016C-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleEG_Run2016D-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleEG/Run2016D-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleEG_Run2016E-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleEG/Run2016E-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleEG_Run2016F-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleEG/Run2016F-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleEG_Run2016G-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleEG/Run2016G-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleEG_Run2016H-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleEG/Run2016H-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleMuon_Run2016E-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleMuon/Run2016E-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleMuon_Run2016F-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleMuon/Run2016F-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleMuon_Run2016G-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleMuon/Run2016G-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleMuon_Run2016H-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleMuon/Run2016H-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_SingleElectron_Run2016B_ver2-Nano14Dec2018_ver2-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/SingleElectron/Run2016B_ver2-Nano14Dec2018_ver2-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_SingleElectron_Run2016C-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/SingleElectron/Run2016C-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
        },
    "data_SingleElectron_Run2016D-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/SingleElectron/Run2016D-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
        },
    "data_SingleElectron_Run2016E-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/SingleElectron/Run2016E-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
        },
    "data_SingleElectron_Run2016F-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/SingleElectron/Run2016F-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
        },
    "data_SingleElectron_Run2016G-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/SingleElectron/Run2016G-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
        },
    "data_SingleElectron_Run2016H-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/SingleElectron/Run2016H-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
        },
    "data_DoubleMuon_Run2016B_ver2-Nano14Dec2018_ver2-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleMuon/Run2016B_ver2-Nano14Dec2018_ver2-v1/*/*/*.root",
        "plot_group" : "data"
        },
    "data_DoubleMuon_Run2016C-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleMuon/Run2016C-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    },
    "data_DoubleMuon_Run2016D-Nano14Dec2018-v1" : {
        "file_path" : "/store/user/kelong/NanoAOD_DileptonSkims_06Jun2019/DoubleMuon/Run2016D-Nano14Dec2018-v1/*/*/*.root",
        "plot_group" : "data"
    }
}
if uwlogin:
    for key, value in info.iteritems():
        filelabels = value["file_path"].split("/")
        name = filelabels[5]
        if "data" in value["plot_group"]:
            name = "_".join(filelabels[5:7])
        value["file_path"] = "/".join(["/data", os.getlogin(), "NanoAODSkims/DileptonNanoSkims", name, "*"]) 

elif uw:
    for key, value in info.iteritems():
        value["file_path"] = "/hdfs" + value["file_path"]

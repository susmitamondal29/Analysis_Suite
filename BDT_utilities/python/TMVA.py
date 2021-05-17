#!/usr/bin/env python3

from ROOT import TMVA, TFile, TTree, TCut

import pandas as pd
import awkward1 as ak

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras.optimizers import SGD

from .dataholder import MLHolder

class TMVAMaker(MLHolder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_files(self, directory):
        arr_dict = self.get_final_dict(directory)
        outdf = pd.DataFrame()
        for group, samples in self.group_dict.items():
            for sample in samples:
                if sample not in arr_dict:
                    print(f'Could not found sample {sample}')
                    continue
                if len(arr_dict[sample].scale) == 0:
                    print(f'Sample {sample} has no events in it!')
                    continue
                arr = arr_dict[sample]
                df_dict = dict()
                for varname, func in self.use_vars.items():
                    df_dict[varname] = ak.to_numpy(eval(f'arr.{func}'))
                df_dict["scale_factor"] = ak.to_numpy(arr.scale)
                df = pd.DataFrame.from_dict(df_dict)
                df["groupName"] = sample
                outdf = pd.concat((outdf, df))

        self._write_uproot("blah.root", outdf)


    def train(self, workdir):
        # Setup TMVA
        TMVA.Tools.Instance()
        TMVA.PyMethodBase.PyInitialize()

        output = TFile.Open('TMVA.root', 'RECREATE')
        factory = TMVA.Factory('TMVARegression', output,
                               '!V:!Silent:Color:DrawProgressBar:Transformations=D,G:AnalysisType=Regression')
        # # Define model
        # model = Sequential()
        # model.add(Dense(64, activation='tanh', input_dim=2))
        # model.add(Dense(1, activation='linear'))

        # # Set loss and optimizer
        # model.compile(loss='mean_squared_error', optimizer=SGD(lr=0.01))

        # # Store model to file
        # model.save('model.h5')
        # model.summary()

        dataloader = TMVA.DataLoader('dataset')
        for var in self.use_vars.keys():
            dataloader.AddVariable(var)
        
        data = TFile.Open('blah.root')
        for key in data.GetListOfKeys():
            if key.GetName() in self.group_dict["Signal"]:
                dataloader.AddSignalTree(key.ReadObj(), 1.0)
            else:
                dataloader.AddBackgroundTree(key.ReadObj(), 1.0)

        

        dataloader.PrepareTrainingAndTestTree(TCut(''),
                'nTrain_Regression=4000:SplitMode=Random:NormMode=NumEvents:!V')

        # Book methods
        factory.BookMethod(dataloader, TMVA.Types.kPyKeras, 'PyKeras',
                           'H:!V:VarTransform=D,G:NumEpochs=20:BatchSize=32:FilenameModel=model.h5')
        factory.BookMethod(dataloader, TMVA.Types.kBDT, 'BDTG',
                           '!H:!V:VarTransform=D,G:NTrees=1000:BoostType=Grad:Shrinkage=0.1:UseBaggedBoost:BaggedSampleFraction=0.5:nCuts=20:MaxDepth=4')

        # # Run TMVA
        # factory.TrainAllMethods()
        # factory.TestAllMethods()
        # factory.EvaluateAllMethods()

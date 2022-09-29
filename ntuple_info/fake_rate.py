#!/usr/bin/env python3
from analysis_suite.commons.info import NtupleInfo
import analysis_suite.commons.user as user

sideband = NtupleInfo(
    # filename = user.hdfs_workspace / 'isolation_test/{year}/0914_mva/',
    # filename = user.hdfs_workspace / 'fake_rate/0916/{year}/',  #'isolation_test/{year}/0903/',# 'workspace/fake_rate/0701',
    filename = user.hdfs_workspace / 'fake_rate/{year}/{workdir}/',
    trees = ['SideBand'],
    region = 'SideBand',
    branches = [
        lambda vg : vg.mergeParticles("TightLepton", "TightMuon", "TightElectron"),
        lambda vg : vg.mergeParticles("Electron", "FakeElectron", "TightElectron"),
        lambda vg : vg.mergeParticles("Muon", "FakeMuon", "TightMuon"),
        lambda vg : vg.mergeParticles("AllLepton", "FakeMuon", "FakeElectron", "TightMuon", "TightElectron"),
    ]
)

measurement = NtupleInfo(
    # filename = user.hdfs_workspace / 'isolation_test/{year}/0914_mva/',
    # filename = user.hdfs_workspace / 'fake_rate/0916/{year}/', #'isolation_test/{year}/0903/',# 'workspace/fake_rate/0818',
    filename = user.hdfs_workspace / 'fake_rate/{year}/{workdir}/',
    trees = ['Measurement'],
    region = 'Measurement',
    branches = [
        lambda vg : vg.mergeParticles("Electron", "FakeElectron", "TightElectron"),
        lambda vg : vg.mergeParticles("Muon", "FakeMuon", "TightMuon"),
        lambda vg : vg.mergeParticles("TightLepton", "TightMuon", "TightElectron"),
        lambda vg : vg.mergeParticles("AllLepton", "FakeMuon", "FakeElectron", "TightMuon", "TightElectron"),
    ]
)

closure_tf = NtupleInfo(
    # filename = user.hdfs_workspace / 'isolation_test/{year}/0914_mva/',
    # filename = user.hdfs_workspace / 'fake_rate/0916/{year}/', #'fake_rate/0914/{year}/',
    filename = user.hdfs_workspace / 'fake_rate/{year}/{workdir}/',
    trees = ['Closure_TF'],
    region = 'Closure',
    branches = [
        lambda vg : vg.mergeParticles("Muon", "FakeMuon", "TightMuon"),
        lambda vg : vg.mergeParticles("Electron", "FakeElectron", "TightElectron"),
        lambda vg : vg.mergeParticles("TightLepton", "TightMuon", "TightElectron"),
        lambda vg : vg.mergeParticles("FakeLepton", "FakeMuon", "FakeElectron"),
        lambda vg : vg.mergeParticles("AllLepton", "TightMuon", "TightElectron", "FakeMuon", "FakeElectron"),
    ]
)

closure_tt = NtupleInfo(
    # filename = user.hdfs_workspace / 'isolation_test/{year}/0914_mva/',
    # filename = user.hdfs_workspace / 'fake_rate/0916/{year}/', #'fake_rate/0914/{year}/',
    filename = user.hdfs_workspace / 'fake_rate/{year}/{workdir}/',
    trees = ['Closure_FF', 'Closure_TF', 'Closure_TT'],
    region = 'Closure',
    branches = [
        lambda vg : vg.mergeParticles("Muon", "FakeMuon", "TightMuon"),
        lambda vg : vg.mergeParticles("Electron", "FakeElectron", "TightElectron"),
        lambda vg : vg.mergeParticles("TightLepton", "TightMuon", "TightElectron"),
        lambda vg : vg.mergeParticles("FakeLepton", "FakeMuon", "FakeElectron"),
        lambda vg : vg.mergeParticles("AllLepton", "TightMuon", "TightElectron", "FakeMuon", "FakeElectron"),
    ]
)
closure_tt.add_change('Closure_FF', {'data': 'nonprompt'})
closure_tt.add_ignore('Closure_FF', ['ttbar', 'ttbar_lep', 'wjets', 'wjet_ht'])
closure_tt.add_change('Closure_TF', {'data': 'nonprompt'})
closure_tt.add_ignore('Closure_TF', ['ttbar', 'ttbar_lep', 'wjets', 'wjet_ht'])

isolation = NtupleInfo(
    filename = user.hdfs_workspace / 'isolation_test/{year}/{workdir}/',
    trees = ["SideBand",
        # "Measurement"
             ],
    region = 'Measurement',
    branches = [
        lambda vg : vg.mergeParticles("Muon", "FakeMuon", "TightMuon"),
        # lambda vg : vg.mergeParticles("TightLepton", "TightMuon", "TightElectron"),
        lambda vg : vg.mergeParticles("AllLepton", "FakeMuon", "TightMuon", "FakeElectron", "TightElectron"),
        # lambda vg : vg.mergeParticles("FakeLepton", "FakeMuon", "FakeElectron"),
        lambda vg : vg.mergeParticles("Electron", "FakeElectron", "TightElectron"),
    ]

)

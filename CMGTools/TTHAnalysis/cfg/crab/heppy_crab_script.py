#!/usr/bin/env python
import os
import PhysicsTools.HeppyCore.framework.config as cfg
#cfg.Analyzer.nosubdir=True

import ROOT
from DataFormats.FWLite import *
import sys
import re
#import PSet

ROOT.gSystem.Load("libCMGToolsTTHAnalysis")
ROOT.gSystem.Load("libFWCoreFWLite.so")
ROOT.gSystem.Load("libDataFormatsFWLite.so")
ROOT.gSystem.Load("libPhysicsToolsHeppy")
ROOT.gSystem.Load("libCMGToolsRootTools")
ROOT.AutoLibraryLoader.enable()

dataset = ""
total = 0  # total number of jobs for given dataset, not used at the moment
nevents = None # this means run all events
nprint  = 0 # quiet printout, change if you want to print the first nprint events

# arguments of scriptExe
print "ARGV:",sys.argv
JobNumber=sys.argv[1] # 1st crab argument is jobID
job = int(JobNumber)
# if one wants to include more options to be passed to the crab scriptExe add a corresponding argument below
# crab only allows arguments of the type 'arg=value'
for arg in sys.argv[2:]:
    if arg.split("=")[0] == "dataset":  # this argument is strictly necessary
        dataset = arg.split("=")[1]
    elif arg.split("=")[0] == "total":
        total = int(arg.split("=")[1])
    elif arg.split("=")[0] == "nevents":
        nevents = int(arg.split("=")[1])
        print "selected to run over", nevents, "events"

print "dataset:", dataset
print "job", job , " out of", total

# fetch config file
import imp
handle = open("heppy_config.py", 'r')
cfo = imp.load_source("heppy_config", "heppy_config.py", handle)
config = cfo.config
handle.close()

# pick right component from dataset and file from jobID
selectedComponents = []
for comp in config.components:
    if comp.name == dataset:
        comp.files = comp.files[job-1: job] # first job number is 1
        comp.name = comp.name+"_Chunk"+str(job)
        selectedComponents.append(comp)

# check selectedComponents
if len(selectedComponents) == 0:
    print "No selected components found!!"
    print "   - dataset:", dataset
    print "   - components:", config.components
if len(selectedComponents)>1:
    print "More than one selected component:"
    cfg.printComps(selectedComponents)
else:
    print "Selected component:"
    print selectedComponents[0]
    print "files: ", selectedComponents[0].files

# set component to run
config.components = selectedComponents

# run!!!
from PhysicsTools.HeppyCore.framework.looper import Looper
looper = Looper( 'Output', config, nPrint = nprint, nEvents = nevents)
looper.loop()
looper.write()

#os.system("ls -lR") # for debugging

# assign the right name
os.rename("Output/mt2.root", "mt2.root")

# print in crab log file the content of the job log files, so one can see it from 'crab getlog'
print "-"*25
print "printing output txt files"
os.system('for i in Output/*.txt; do echo $i; cat $i; echo "---------"; done')

# pack job log files to be sent to output site
os.system("tar czf output.log.tgz Output/")
#os.system("mkdir log")
#os.rename("output.log.tgz log/output.log.tgz")


import ROOT
f=ROOT.TFile.Open('mt2.root')
entries=f.Get('tree').GetEntries()
f.Close()

print entries, "events processed"
print "job succesful"

# genstudies-eft

Clone repository:
```sh
git clone --recurse-submodules https://github.com/fstaeg/genstudies-eft.git
```

Setup (at the start of each new session):
```sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/bin/thisroot.sh
```

Install python packages:
```sh
pip install pyhepmc
pip install fastjet
```

## Generating events

Event samples with SMEFT weights included are generated using the `EFT2Obs` tool. Detailed instructions are in [docs/EventGeneration.md](docs/EventGeneration.md) or in [EFT2Obs/README.md](https://github.com/ajgilbert/EFT2Obs/blob/master/README.md)).

## Processing samples

Read the HepMC or LHE samples and save the events in a .pkl file
```sh
python read_events.py \
 -i EFT2Obs/DYjets-SMEFTsim3/events_{1..10}.hepmc.gz \
 -o DYjets/events.pkl --parallel 10
# options
#   -i {files}: input HepMC or LHE files
#   -o {file}: output .pkl file (default: events.pkl)
#   --parallel {N}: read N files in parallel (default: 1)
```

Make histograms:
```sh
python make_histograms.py \
 -i DYjets/events.pkl -o DYjets/histograms.pkl -c config_DYjets.py
# options
#   -i {file}: input .pkl file with events
#   -o {file}: output .pkl file with histograms (default: histograms.pkl)
#   -c {script}: Analysis config with selections, variables, ... [see below] (default: config_DYjets.py)
```

An example analysis config is in [config_DYjets.py](config_DYjets.py). The config should contain:
- a list of Wilson coefficients (in same order as in the `reweight_card`)
- the event selection
- a list of variables

## Plotting

```sh
python make_plots.py \
 -i DYjets/histograms.pkl -o DYjets/plots -c config_DYjets.py
# options
#   -i {file}: input .pkl file with histograms (default: histograms.pkl)
#   -o {directory}: output directory for plots (default: plots)
#   -c {script}: Analysis config (default: config_DYjets.py)
```

## Fitting

We use [Combine](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/) to do the Asimov fits and derive expected limits on the Wilson coefficients. Instructions on how to install Combine are in [docs/InstallCombine.md](docs/InstallCombine.md), and the physics model in [EFTModel.py](EFTModel.py).

Create the Combine datacard and ROOT histograms:
```sh
python make_cards.py \
 -i DYjets/histograms.pkl -o DYjets/datacard.txt --observable mll
# options
#   -i {file}: input .pkl file with histograms (default: histograms.pkl)
#   -o {file}: output datacard and histograms for Combine (default: datacard.txt)
#   --observable {obs}: observable (default: mll)
```

Make the Combine workspace:
```sh
text2workspace.py DYjets/datacard.txt -o DYjets/workspace.root \
 -P HiggsAnalysis.CombinedLimit.EFTModel:eftModel \
 --PO poi=clj1:clj3:ceu:ced:cje:clu:cld
# ignore quadratic terms ~c^2/Lambda^4: --PO linear
```

Fit, e.g.:
```sh
cd DYjets
mkdir scans

combine workspace.root -M MultiDimFit -t -1 \
 -n .clj1 -P clj1 --algo grid --setParameterRanges clj1=-0.4,0.4

plot1DScan.py higgsCombine.clj1.MultiDimFit.mH120.root \
 --POI clj1 -o scans/clj1 --main-label 'Expected'
```


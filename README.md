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

Event samples with SMEFT weights included are generated using the `EFT2Obs` tool. Detailed instructions are in [EventGeneration.md](EventGeneration.md) or in the EFT2Obs [README](EFT2Obs/README.md).

1) Install EFT2Obs
```sh
# LCG environment
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/bin/thisroot.sh

cd EFT2Obs
source env.sh

# Installing MG5_aMC@NLO, Pythia8, and the SMEFTsim3 model
./scripts/setup_mg5.sh
./scripts/setup_model_SMEFTsim3.sh
```

2) Generate events using the cards in `eft2obs_cards/DYjets-SMEFTsim3`:
```sh
cp -r eft2obs_cards/DYjets-SMEFTsim3 EFT2Obs/cards/
cd EFT2Obs
source env.sh

./scripts/setup_process.sh DYjets-SMEFTsim3
./scripts/make_gridpack.sh DYjets-SMEFTsim3

python scripts/launch_jobs.py --gridpack gridpack_DYjets-SMEFTsim3.tar.gz \
 -j 10 -e 10000 -s 1 --job-mode interactive --parallel 10 \
 --to-step shower --save-hepmc DYjets-SMEFTsim3 
# stop at LHE level: --to-step lhe --save-lhe DYjets-SMEFTsim3
```

## Processing samples

1) Read the HepMC or LHE samples and save the events in a .pkl file
```sh
python read_events.py \
 -i EFT2Obs/DYjets-SMEFTsim3/events_{1..10}.hepmc.gz \
 -o DYjets/events.pkl --parallel 10
# options
#   -i {files}: input HepMC or LHE files
#   -o {file}: output .pkl file (default: events.pkl)
#   --parallel {N}: read N files in parallel (default: 1)
```

2) Make histograms:
```sh
python make_histograms.py \
 -i DYjets/events.pkl -o DYjets/histograms.pkl -c config_DYjets.py
# options
#   -i {file}: input .pkl file with events
#   -o {file}: output .pkl file with histograms (default: histograms.pkl)
#   -c {script}: Analysis config with selections, variables, ... [see below] (default: config_DYjets.py)
```

An example analysis config is in [config_DYjets.py](config_DYjets.py). The config should contain:
- a list of Wilson coefficients (in same order as in the `reweight_card`), e.g.:
```python
wilson_coefficients = ['clj1', 'clj3', 'ceu', 'ced', 'cje', 'clu', 'cld']
```
- the event selection, e.g.:
```python
def selection(events):
  events['Muon'] = events.Muon[events.Muon.pt > 15]
  events = events[ak.num(events.Muon) >= 2]
  events = events[events.Muon[:,0].pt > 29]
  return events
```
- a list of variables, e.g.:
```python
variables = {
  'mll': {
    'function': lambda events: (events.Muon[:, 0] + events.Muon[:, 1]).mass,
    'axis': hist.axis.Variable([40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,120,
      130,140,150,175,200,225,250,300]),
    'label': '$m_{\\ell\\ell}$',
    'unit': 'GeV',
    'xlog': True
  },
  # etc
}
```

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

We use Combine to do the Asimov fits and derive expected limits on the Wilson coefficients. 

1) Clone Combine repository and symlink the physics model [EFTModel.py](EFTModel.py) into the `HiggsAnalysis/CombinedLimit/python` directory
```sh
git -c advice.detachedHead=false clone --depth 1 --branch v10.5.1 \
 https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git \
 HiggsAnalysis/CombinedLimit

# symlink the physics model into the python directory
cd HiggsAnalysis/CombinedLimit/python
ln -s path/to/genstudies-eft/EFTModel.py ./
cd ..
```

2) Install Combine
```sh
# LCG environment (at the start of each new session)
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/bin/thisroot.sh

# compile
mkdir build
cd build
cmake ..
cmake --build . -j8
cd ..

# append environment variables (at the start of each new session)
export PATH=$PWD/build/bin:$PATH
export LD_LIBRARY_PATH=$PWD/build/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$PWD/build/python:$PYTHONPATH

cd ../..
```

3) Create the Combine datacard and ROOT histograms:
```sh
python make_cards.py \
 -i DYjets/histograms.pkl -o DYjets/datacard.txt --observable mll
# options
#   -i {file}: input .pkl file with histograms (default: histograms.pkl)
#   -o {file}: output datacard and histograms for Combine (default: datacard.txt)
#   --observable {obs}: observable (default: mll)
```

4) Make Combine workspace:
```sh
text2workspace.py DYjets/datacard.txt -o DYjets/workspace.root \
 -P HiggsAnalysis.CombinedLimit.EFTModel:eftModel \
 --PO poi=clj1:clj3:ceu:ced:cje:clu:cld
# ignore quadratic terms ~c^2/Lambda^4: --PO linear
```

5) Fit, e.g.:
```sh
cd DYjets
mkdir scans

combine workspace.root -M MultiDimFit -t -1 \
 -n .clj1 -P clj1 --algo grid --setParameterRanges clj1=-0.4,0.4

plot1DScan.py higgsCombine.clj1.MultiDimFit.mH120.root \
 --POI clj1 -o scans/clj1 --main-label 'Expected'
```


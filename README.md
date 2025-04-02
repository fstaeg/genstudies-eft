# dy-eft-study

Clone repository:
```sh
git clone https://github.com/fstaeg/dy-eft-study.git
```

Setup:
```sh
. /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
```

Create ROOT tree from the LHE files:
```sh
python lhe_to_tree.py -i DY_SM
# options
# -i {directory}: directory of input LHE files and for output ROOT file
# -o {file.root}: name of the output ROOT file (default: events.root)
# -n {N}: only read the first N input files. Useful to save time when testing code (default: all of them)
```

Make plots:
```sh
python make_plots.py -i DY_SM/events.root -o plots
```


### Generate events

To generate the samples with SMEFT weights included, we use the `EFT2Obs` framework.

Installation:
```sh
. /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh # ignore warnings

git clone https://github.com/ajgilbert/EFT2Obs.git
cd EFT2Obs
source env.sh # should be sourced at the start of each new session

./scripts/setup_mg5.sh
./scripts/setup_rivet.sh
./scripts/setup_rivet_plugins.sh

./scripts/setup_model_SMEFTsim3.sh
```


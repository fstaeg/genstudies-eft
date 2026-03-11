To generate the samples with SMEFT weights included, we use the `EFT2Obs` tool, which is included in this repository as a submodule. The cards for DY production are in `eft2obs_cards/DYjets-SMEFTsim3`.

## Installing EFT2Obs

```sh
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
# doesn't work, use CMSSW_14_1_0_pre4

cd EFT2Obs
git checkout master
git pull
source env.sh # should be sourced at the start of each new session

# Installing MG5_aMC@NLO and Pythia8
./scripts/setup_mg5.sh

# Installing the SMEFTsim3 model
./scripts/setup_model_SMEFTsim3.sh
```

### Setting up the event generation

1) First we create a subdirectory `cards/DYjets-SMEFTsim3` with a file `proc_card.dat`:
```
import model SMEFTsim_topU3l_MwScheme_UFO-massless

# Definitions
define ell+ = e+ mu+
define ell- = e- mu-

generate p p > ell+ ell- NP<=1 @0
add process p p > ell+ ell- j NP<=1 @1

output DYjets-SMEFTsim3 -nojpeg
```

2) Initialise the process in MadGraph:
```sh
./scripts/setup_process.sh DYjets-SMEFTsim3
```
- this creates a process directory `EFT2Obs/MG5_aMC-v2_9_16/DYjets-SMEFTsim3`
- take a look at the Feynman diagrams in `EFT2Obs/MG5_aMC-v2_9_16/DYjets-SMEFTsim3/SubProcesses/*/matrix*.ps`

3) The last step created two new cards in `EFT2Obs/cards/DYjets-SMEFTsim3`: `pythia8_card.dat` and `run_card.dat`:
- We make three changes to `run_card.dat`:
```txt
10.0 = xqcut
False = use_syst
none = systematics_program
```
- In `pythia8_card.dat`, we turn off multi-parton interactions to speed things up:
```txt
partonlevel:mpi = off
```

4) Next we create a configuration file that specifies the SMEFT operators we want to study. It is generated with:
```sh
python scripts/make_config.py -p DYjets-SMEFTsim3 \
 -o cards/DYjets-SMEFTsim3/config.json --pars SMEFT:108,109,113,115,117,119,121 \
 --def-val 1.0 --def-sm 0.0 --def-gen 0.0
```
- 108,...,121 are the IDs of the seven operators we are interested in: `clj1, clj3, ceu, ced, cje, clu, cld`

5) Next we use the `config.json` to create two additional cards, `param_card.dat` and `reweight_card.dat`:
```sh
python scripts/make_param_card.py -p DYjets-SMEFTsim3 \
 -c cards/DYjets-SMEFTsim3/config.json -o cards/DYjets-SMEFTsim3/param_card.dat

python scripts/make_reweight_card.py cards/DYjets-SMEFTsim3/config.json \
 cards/DYjets-SMEFTsim3/reweight_card.dat
```

### Generating events

1) Now that all the cards are prepared, we can produce a gridpack:
```sh
./scripts/make_gridpack.sh DYjets-SMEFTsim3
```

2) From the gridpack, we can now generate events:
```sh
python scripts/launch_jobs.py --gridpack gridpack_DYjets-SMEFTsim3.tar.gz \
 -j 10 -e 10000 -s 1 --job-mode interactive --parallel 10 \
 --to-step shower --save-hepmc DYjets-SMEFTsim3
# or: --to-step lhe --save-lhe DYjets-SMEFTsim3
```
- this will generate a total of 100k events split in 10 jobs that run in parallel
- in the last line, we set the option to stop after the showering and creating the HepMC files (by default it would run a Rivet routine). Alternatively, we can stop at the LHE level (using the options `--to-step lhe --save-lhe DYjets-SMEFTsim3`)

3) We are done. The generated HepMC (LHE) files are saved in `DYjets-SMEFTsim3/events_{N}.hepmc.gz` (`events_{N}.lhe.gz`).
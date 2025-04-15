# genstudies-eft

Clone repository:
```sh
git clone --recurse-submodules https://github.com/fstaeg/genstudies-eft.git
```

Setup (should be sourced at the start of each new session):
```sh
. /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
```

## Workflow

To generate the samples with SMEFT weights included, we use the `EFT2Obs` tool, which we include in this repository as a submodule.

### Installing EFT2Obs

```sh
. /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh

cd EFT2Obs
source env.sh # should be sourced at the start of each new session

# Installing MG5_aMC@NLO and Pythia8
./scripts/setup_mg5.sh

# Installing Rivet (Can be skipped. We do not need Rivet at the moment)
# ./scripts/setup_rivet.sh
# ./scripts/setup_rivet_plugins.sh

# Installing the SMEFTsim model
./scripts/setup_model_SMEFTsim3.sh
```

### Setting up the event generation

1) First we create a subdirectory `cards/dy-SMEFTsim3` with a file `proc_card.dat`:
```
import model SMEFTsim_topU3l_MwScheme_UFO-massless

# Definitions
define ell+ = e+ mu+
define ell- = e- mu-

generate p p > ell+ ell- NP<=1 @0

output dy-SMEFTsim3 -nojpeg
```

- first we import the SMEFTsim3 model
- then we generate pp $\rightarrow$ $\ell^{+} \ell^{-}$ events with up to one new physics vertices inserted (`NP<=1`)
- the directory specified in the last line has to match the name of the subdirectory in `cards` (`dy-SEMFTsim3`)

2) Initialise the process in MadGraph:
```sh
./scripts/setup_process.sh dy-SMEFTsim3
```

- this creates a process directory `MG5_aMC-v2_9_16/dy-SMEFTsim3`
- take a look at the Feynman diagrams in `MG5_aMC-v2_9_16/dy-SMEFTsim3/SubProcesses/P0_qq_ll/matrix1.ps` and `...matrix2.ps`

3) The last step created two new cards in `cards/dy-SMEFTsim3`: `pythia8_card.dat` (we are not using Pythia for now, so this can be left as it is) and `run_card.dat`. We make two changes to `run_card.dat`:
```txt
False = use_syst
none = systematics_program
```

- in `run_card.dat` we can also apply generator level cuts. Later we will probably have to generate events in several bins of mll, to improve the statistics of our samples at high invariant mass. For this we can use the parameters `mmll` and `mmllmax`.

4) Next we create a configuration file that specifies the SMEFT operators we want to study. It is generated with:
```sh
python scripts/make_config.py -p dy-SMEFTsim3 -o cards/dy-SMEFTsim3/config.json \
 --pars SMEFT:108,109,113,115,117,119,121 --def-val 1.0 --def-sm 0.0 --def-gen 0.0
```

- 108,...,121 are the IDs of the seven operators we are interested in: `clj1, clj3, ceu, ced, cje, clu, cld`

5) Next we use the `config.json` to create two additional cards, `param_card.dat` and `reweight_card.dat`:
```sh
python scripts/make_param_card.py -p dy-SMEFTsim3 \
 -c cards/dy-SMEFTsim3/config.json -o cards/dy-SMEFTsim3/param_card.dat

python scripts/make_reweight_card.py cards/dy-SMEFTsim3/config.json \
 cards/dy-SMEFTsim3/reweight_card.dat
```

### Generating events

1) Now that all the cards are prepared, we can produce a gridpack:
```sh
./scripts/make_gridpack.sh dy-SMEFTsim3
```

2) From the gridpack, we can now generate events:
```sh
python scripts/launch_jobs.py --gridpack gridpack_dy-SMEFTsim3.tar.gz \
 -j 10 -e 10000 -s 1 --job-mode interactive --parallel 10 \
 --to-step lhe --save-lhe dy-SMEFTsim3
```

- this will generate a total of 100k events split in 10 jobs that run in parallel
- in the last line, we set the option to stop after generating the LHE files. By default it would run the showering with Pythia8 and run a Rivet routine (for now we do not want that)

3) We are done. The generated LHE files are saved in `dy-SMEFTsim3/events_{N}.lhe.gz`. Move them to the `genstudies-eft` directory:
```sh
cp -r dy-SMEFTsim3 ..
cd ..
```

### Processing the samples

1) Create a ROOT tree from the LHE files:
```sh
python lhe_to_tree.py -d dy-SMEFTsim3
# options
# -d {dirname}: directory of input LHE files and for output ROOT file
# -f {filename.root}: name of the output ROOT file (default: events.root)
# -n {N}: only read the first N input files. Useful to save time when testing code (default: all of them)
```

2) Make plots:
```sh
python make_plots.py -i dy-SMEFTsim3/events.root -o plots
```

# dy-eft-study

Clone repository:
```sh
git clone git@github.com:fstaeg/dy-eft-study.git
```

Setup:
```sh
# on linux.physik.uzh.ch
cd /app/cern/root_v6.22.08
source bin/thisroot.sh
cd -
```

Create ROOT tree from the LHE files:
```sh
python scripts/lhe_to_tree.py -i DY_sm
```

Look at contents of the ROOT file using TBrowser (have to use `ssh -Y user@linux.physik.uzh.ch` for this to work):
```sh
root -l DY_sm/events.root
```

```cpp
new TBrowser()
```
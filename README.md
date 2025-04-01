# dy-eft-study

Clone repository:
```sh
git clone https://github.com/dy-eft-study.git
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
python scripts/lhe_to_tree.py -i DY_SM
```

Look at contents of the ROOT file using TBrowser (have to use `ssh -Y user@linux.physik.uzh.ch` for this to work):
```sh
root -l DY_SM/events.root
```

```cpp
new TBrowser()
```
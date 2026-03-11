To run the fits and derive expected limits on the Wilson coefficients, we use [Combine](https://cms-analysis.github.io/HiggsAnalysis-CombinedLimit/latest/). The physics model [EFTModel.py](EFTModel.py) has to be symlinked into the `HiggsAnalysis/CombinedLimit/python` directory before compiling.

Clone Combine repository and symlink the physics model [EFTModel.py](EFTModel.py) into the `HiggsAnalysis/CombinedLimit/python` directory:
```sh
git -c advice.detachedHead=false clone --depth 1 --branch v10.5.1 \
 https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git \
 HiggsAnalysis/CombinedLimit

# symlink the physics model into the python directory
cd HiggsAnalysis/CombinedLimit/python
ln -s path/to/genstudies-eft/EFTModel.py ./
cd ..
```

Install Combine:
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
```

At the start of each new session you have to do:
```sh
cd HiggsAnalysis/CombinedLimit
export PATH=$PWD/build/bin:$PATH
export LD_LIBRARY_PATH=$PWD/build/lib:$LD_LIBRARY_PATH
export PYTHONPATH=$PWD/build/python:$PYTHONPATH
cd ../..
```

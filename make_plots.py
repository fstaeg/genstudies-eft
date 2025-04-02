import ROOT
import os
import hist
import mplhep as hep
import numpy as np
from matplotlib import pyplot as plt
from argparse import ArgumentParser

style = hep.style.CMS
style['font.size'] = 18
plt.style.use(style)

parser = ArgumentParser()
parser.add_argument('-i', '--input', default=None, help='path to ROOT file')
parser.add_argument('-o', '--output', default='plots', help='output directory')
args = parser.parse_args()

# define variables and binning
variables = {
    'mll': {
        'function': lambda tree: tree.mll,
        'axis': hist.axis.Regular(50, 50, 300)
    },
    'ptl': {
        'function': lambda tree: tree.Lepton_pt,
        'axis': hist.axis.Regular(60, 0, 150)
    },
    'detall': {
        'function': lambda tree: abs(tree.Lepton_eta[0]-tree.Lepton_eta[1]),
        'axis': hist.axis.Regular(50, 0, 5)
    }
}

# create histograms
histos = {}
for k,v in variables.items():
    histos[k] = hist.Hist(v['axis'], storage=hist.storage.Weight())

# loop through the ROOT tree and fill the histograms
infile = ROOT.TFile(args.input, 'READ')
tree = infile.Get('events')

for i in range(tree.GetEntries()):
    tree.GetEntry(i)
    for k,v in variables.items():
        histos[k].fill(v['function'](tree), weight=tree.EventWeight)

# plotting
if not os.path.isdir(args.output):
    os.makedirs(args.output)

for k,v in histos.items():
    fig,ax = plt.subplots(dpi=300)
    hep.cms.label('Private Work', data=True, ax=ax, rlabel='')
    ax.set_yscale('log')
    ax.set_ylabel('Events')
    ax.set_xlabel(k)
    ax.set_xlim(v.axes[0].edges[0], v.axes[0].edges[-1])

    ax.stairs(
        v.values(), 
        v.axes[0].edges, 
        label=f"DY SM [{int(round(np.sum(v.values()), 0))}]", 
        color='cornflowerblue',
        edgecolor='black',
        fill=True,
        linewidth=1.0,
    )
    
    ax.legend(loc="upper right", fontsize=12)
    fig.savefig(f"{args.output}/{k}.png", bbox_inches="tight")



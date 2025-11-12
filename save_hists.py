import ROOT
import hist
import numpy as np

def hist_to_th1d(h, name):
    edges = h.axes[0].edges
    values = h.values()
    errors = h.variances()**0.5

    res = ROOT.TH1D(name, name, len(edges)-1, edges)
    for i in range(len(values)):
        res.SetBinContent(i+1, values[i])
        res.SetBinError(i+1, errors[i])

    return res

# create hist.Hist and fill with random values
histo = hist.Hist(hist.axis.Regular(25, 50, 300), storage=hist.storage.Weight())
data = np.random.normal(150, 50, 1000)
histo.fill(data)

# open ROOT file
tfile = ROOT.TFile('histogram.root', 'RECREATE')

# convert hist.Hist to ROOT.TH1D and save to ROOT file 
thisto = hist_to_th1d(histo, 'histo_name')
thisto.Write()

# close ROOT file
tfile.Close()
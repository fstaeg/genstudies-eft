import numpy as np
import hist
import ROOT

# load analysis config
def get_analysis_config(config='config.py'):
    exec(
        f'import {config.replace(".py","").replace("/",".")} as analysis_cfg', 
        globals(), globals()
    )
    
    analysis_config = analysis_cfg.__dict__
    if not 'luminosity' in analysis_config: analysis_config['luminosity'] = 1.
    if not 'wilson_coefficients' in analysis_config: analysis_config['wilson_coefficients'] = ['c1']
    if not 'selection' in analysis_config: analysis_config['selection'] = lambda x: x
    if not 'variables' in analysis_config: analysis_config['variables'] = {}
    
    return analysis_config

# convert hist.Hist to ROOT.TH1D
def hist_to_th1d(h, name):
    edges = h.axes[0].edges
    values = h.values()
    errors = h.variances()**0.5

    res = ROOT.TH1D(name, name, len(edges)-1, edges)
    for i in range(len(values)):
        res.SetBinContent(i+1, values[i])
        res.SetBinError(i+1, errors[i])

    return res

# normalize histogram
def renorm_histo(h, lumi):
    return h.copy() * lumi * 1e3 # pb -> fb

# weight transformation like in EFT2Obs/setup/WeightCorrector.h
def transform_weights_lhe(weights_in):
    n_weights = len(weights_in)-1
    n_wc = int((-3 + np.sqrt(9 + 8 * (n_weights-1))) / 2)
    weights_out = [0 for i in range(n_weights)]
    weights_out[0] = weights_in[1]

    for i_wc in range(n_wc):
        s0 = weights_in[1]
        s1 = weights_in[2*i_wc+2]-s0
        s2 = weights_in[2*i_wc+3]-s0
        Ai = 4*s1-s2
        Bii = s2-Ai
        weights_out[2*i_wc+1] = Ai
        weights_out[2*i_wc+2] = Bii

    offset, i_cross = 2*n_wc+1, 0
    for i_wc in range(n_wc):
        for j_wc in range(i_wc+1, n_wc):
            s0 = weights_in[1]
            s1 = weights_in[offset+i_cross+1]-s0
            Ai = weights_out[2*i_wc+1]
            Bii = weights_out[2*i_wc+2]
            Aj = weights_out[2*j_wc+1]
            Bjj = weights_out[2*j_wc+2]
            Bij = s1 - Ai - Bii - Aj - Bjj
            weights_out[offset+i_cross] = Bij
            i_cross += 1

    return weights_out

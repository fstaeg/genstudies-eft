import os
import cloudpickle
import numpy as np
import awkward as ak
import vector; vector.register_awkward()
import hist
from argparse import ArgumentParser
from framework import get_analysis_config, renorm_histo


if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', help='path to input .pkl file with events')
    parser.add_argument('-o', '--output', default='histograms.pkl', help='path to output .pkl file with histograms')
    parser.add_argument('-c', '--config', default='config_DYjets.py', help='path to config file')
    args = parser.parse_args()

    # load analysis config
    config = get_analysis_config(args.config)
    luminosity = config['luminosity']
    wilson_coefficients = config['wilson_coefficients']
    selection = config['selection']
    variables = config['variables']

    # load events
    with open(args.input, 'rb') as file:
        events = cloudpickle.loads(file.read())

    # apply event selection
    events = config['selection'](events)

    # make histograms
    histos = { k: {} for k in variables }

    for k,var in variables.items():
        
        # SM histograms
        histos[k]['sm'] = hist.Hist(var['axis'], storage=hist.storage.Weight())
        histos[k]['sm'].fill(var['function'](events), weight=events.weight[:, 0])
        histos[k]['sm'] = renorm_histo(histos[k]['sm'], luminosity)

        # EFT histograms
        for i,wc in enumerate(wilson_coefficients):
            histos[k][f'{wc}_lin'] = hist.Hist(var['axis'], storage=hist.storage.Weight())
            histos[k][f'{wc}_lin'].fill(var['function'](events), weight=events.weight[:, 2*i+1])
            histos[k][f'{wc}_lin'] = renorm(histos[k][f'{wc}_lin'], luminosity)
            
            histos[k][f'{wc}_quad'] = hist.Hist(var['axis'], storage=hist.storage.Weight())
            histos[k][f'{wc}_quad'].fill(var['function'](events), weight=events.weight[:, 2*i+2])
            histos[k][f'{wc}_quad'] = renorm(histos[k][f'{wc}_quad'], luminosity)

    # save histograms
    outdir = os.path.split(args.output)[0]
    if not os.path.isdir(outdir): 
        os.makedirs(outdir)

    with open(args.output, 'wb') as file:
        file.write(cloudpickle.dumps(histos))


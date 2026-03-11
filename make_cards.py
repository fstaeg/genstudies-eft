import os
import cloudpickle
import ROOT
import hist
import numpy as np
from argparse import ArgumentParser
from framework import hist_to_th1d


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', default='histograms.pkl', help='path to input .pkl file with histograms')
    parser.add_argument('-o', '--output', default='datacard.txt', help='path to output Combine datacard and shapes')
    parser.add_argument('--observable', default='mll', help='name of observable')
    args = parser.parse_args()

    # load histograms
    with open(args.input, 'rb') as file:
        histos = cloudpickle.loads(file.read())
    histos = { k:v for k,v in histos[args.observable].items() }

    # prepare output directory
    outdir, outfile = os.path.split(args.output)
    outfile = outfile.replace('.root','').replace('.txt','')
    if not os.path.isdir(outdir): 
        os.makedirs(outdir)

    # prepare datacard
    nproc = len(histos)
    padding = max([len(str(np.sum(histos[h].values()))) for h in histos])+2

    datacard = []
    datacard.append(f'imax    1 number of bins')
    datacard.append(f'jmax    {nproc-1} number of processes minus 1')
    datacard.append(f'kmax    * number of nuisance parameters')
    datacard.append('--------------------------------------------------------------------------------')
    datacard.append(f'shapes * * {outfile}.root $PROCESS $PROCESS_$SYSTEMATIC')
    datacard.append('--------------------------------------------------------------------------------')
    datacard.append('bin          signal_region')
    datacard.append(f'observation  {np.sum(histos["sm"].values())}')
    datacard.append('--------------------------------------------------------------------------------')
    datacard.append(f'bin          ')
    datacard.append(f'process      ')
    datacard.append(f'process      ')
    datacard.append(f'rate         ')
    datacard.append('--------------------------------------------------------------------------------')
    datacard.append(f'lumi    lnN  ')
    for i,h in enumerate(histos):
        datacard[-6] += 'signal_region'.ljust(padding)
        datacard[-5] += h.ljust(padding)
        datacard[-4] += str(1-i).ljust(padding)
        datacard[-3] += str(np.sum(histos[h].values())).ljust(padding)
        datacard[-1] += str(1.01).ljust(padding)

    # save datacard
    with open(f'{outdir}/{outfile}.txt', 'w') as f:
        for line in datacard:
            f.write(line)
            f.write('\n')


    # save histograms in ROOT file
    tfile = ROOT.TFile(f'{outdir}/{outfile}.root', 'RECREATE')
    
    h_data = hist_to_th1d(histos['sm'], 'data_obs')
    h_data.Write()
    
    for k,h in histos.items(): 
        h = hist_to_th1d(h, k)
        h.Write()
    
    tfile.Close()


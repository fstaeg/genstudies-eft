import os
import cloudpickle
import numpy as np
import awkward as ak
import vector; vector.register_awkward()
import hist
from argparse import ArgumentParser
from matplotlib import pyplot as plt
import mplhep as hep
from framework import get_analysis_config


if __name__ == '__main__':
    
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', default='histograms.pkl', help='path to input .pkl file with histograms')
    parser.add_argument('-o', '--output', default='plots', help='path to output directory for plots')
    parser.add_argument('-c', '--config', default='config_DYjets.py', help='path to config file')
    args = parser.parse_args()

    # load analysis config
    config = get_analysis_config(args.config)
    luminosity = config['luminosity']
    wilson_coefficients = config['wilson_coefficients']
    variables = config['variables']

    # set style
    style = hep.style.CMS
    style['font.size'] = 18
    plt.style.use(style)

    # load histograms
    with open(args.input, 'rb') as file:
        histos = cloudpickle.loads(file.read())

    # prepare output directory
    if not os.path.isdir(args.output):
        os.makedirs(args.output)

    # make plots
    for k,var in variables.items():
        widths = histos[k]['sm'].axes[0].widths
        edges = histos[k]['sm'].axes[0].edges

        # set labels and axis ranges
        unit = var.get('unit')
        xlog = var.get('xlog', False)
        var_label = var.get('label', k)
        
        xlabel = f'{var_label} ({unit})' if unit is not None else var_label
        
        if luminosity == 1.:
            ylabel = f'$d\\sigma$ / d{var_label} (fb / {unit if unit is not None else "bin"})'
            rlabel = ''
        else:
            ylabel = f'Events / {unit if unit is not None else "bin"}'
            rlabel = f'{round(luminosity, 2)} $fb^{{-1}}$'

        xmin = edges[1]/2 if xlog and edges[0]<=0 else edges[0]
        xmax = edges[-1]

        ymin = np.min([v for v in (histos[k]['sm'].values()/widths) if v>0]) / 5.
        ymax = np.max(histos[k]['sm'].values()/widths) * 20.
        
        # loop over Wilson coefficients
        for wc in wilson_coefficients:
            h_sm = histos[k]['sm'].values()
            h_lin = histos[k][f'{wc}_lin'].values()
            h_quad = histos[k][f'{wc}_quad'].values()

            fig,ax = plt.subplots(2, 1, sharex=True, gridspec_kw={'height_ratios': [3,1]}, dpi=300)
            fig.tight_layout(pad=-0.5)
            hep.cms.label('Private Work', data=True, ax=ax[0], rlabel=rlabel)
            
            # upper panel: histograms
            ax[0].set_ylabel(ylabel)
            ax[0].set_xlim(xmin, xmax)
            ax[0].set_ylim(ymin, ymax)
            ax[0].set_yscale('log')
            if xlog: ax[0].set_xscale('log')

            ax[0].stairs(
                h_sm/widths, 
                edges, 
                label=f'SM [{int(round(np.sum(h_sm), 0))}]', 
                color='cornflowerblue',
                edgecolor='royalblue',
                fill=True,
                linewidth=2.0,
            )

            ax[0].stairs(
                (h_sm+h_lin)/widths, 
                edges, 
                label=f'{wc}=1.0 (linear) [{int(round(np.sum(h_lin), 0))}]', 
                color='palevioletred',
                fill=False,
                linewidth=2.0,
                linestyle='dashed',
            )

            ax[0].stairs(
                (h_sm+h_lin+h_quad)/widths, 
                edges, 
                label=f'{wc}=1.0 (linear+quadratic) [{int(round(np.sum(h_lin+h_quad), 0))}]', 
                color='darkmagenta',
                fill=False,
                linewidth=2.0,
                linestyle='dotted',
            )
            
            ax[0].legend(loc='upper center', fontsize=15, ncols=3)

            # lower panel: ratio
            denominator = np.where(h_sm>0., h_sm, 1e-6) # we can not divide by 0
            
            rmin = np.min([v for v in (h_sm+h_lin)/denominator if v>0])
            rmax = max(np.max((h_sm+h_lin)/denominator), np.max((h_sm+h_lin+h_quad)/denominator))
            dmax = 1.1*max(1-rmin, rmax-1)
            
            ax[1].set_xlabel(xlabel)
            ax[1].set_ylabel('BSM / SM')
            ax[1].set_ylim(max(1-dmax, 0.), 1+dmax)

            ax[1].plot(
                edges, 
                np.ones_like(edges), 
                color='royalblue', 
            )
            
            ax[1].stairs(
                (h_sm+h_lin)/denominator, 
                edges, 
                edgecolor='palevioletred',
                fill=False,
                linewidth=2.0,
                linestyle='dashed',
            )

            ax[1].stairs(
                (h_sm+h_lin+h_quad)/denominator, 
                edges, 
                edgecolor='darkmagenta',
                fill=False,
                linewidth=2.0,
                linestyle='dotted',
            )
            
            # save plot
            print(f'saving {args.output}/{k}_{wc}.pdf')
            fig.savefig(f'{args.output}/{k}_{wc}.pdf', bbox_inches='tight')
            plt.close()


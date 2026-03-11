import os
import sys
import cloudpickle
import pyhepmc
import fastjet
import numpy as np
import awkward as ak
import vector; vector.register_awkward()
import cppyy; cppyy.include('EFT2Obs/LHEF.h')
from argparse import ArgumentParser
from multiprocessing import Pool
from framework import transform_weights_lhe

# read LHE file using EFT2Obs/LHEF.h
def read_lhe(lhe_file):

    os.system('gunzip %s' % lhe_file)
    lhe_file = lhe_file.replace('.gz','')
    
    events_builder = { k: ak.ArrayBuilder() for k in ['weight','Muon','Jet'] }

    # loop over events
    reader = cppyy.gbl.LHEF.Reader(lhe_file)
    while reader.readEvent():

        if reader.hepeup.isGroup: subevents = reader.hepeup.subevents
        else: subevents = [reader.hepeup]

        for event in subevents:

            for key in events_builder.keys():
                events_builder[key].begin_list()
            
            # event weights
            weights = [ weight.first for weight in reader.hepeup.weights ]
            weights = transform_weights_lhe(weights)
            for weight in weights:
               events_builder['weight'].real(weight)

            # loop over particles
            for j in range(event.NUP):  
                
                # ISTUP = 1: final state
                if event.ISTUP[j] != 1:
                    continue

                px,py,pz,e = event.PUP[j]
                pt = np.sqrt(np.square(px)+np.square(py))

                # Muons (IDUP = pdgID)
                if abs(event.IDUP[j]) == 13: 
                    events_builder['Muon'].begin_record('Momentum4D')
                    events_builder['Muon'].field('pdgId').real(event.IDUP[j])
                    events_builder['Muon'].field('px').real(px)
                    events_builder['Muon'].field('py').real(py)
                    events_builder['Muon'].field('pz').real(pz)
                    events_builder['Muon'].field('e').real(e)
                    events_builder['Muon'].field('pt').real(pt)
                    events_builder['Muon'].end_record()

                # Quarks and Gluons
                elif abs(event.IDUP[j]) in [1,2,3,4,5,21]: 
                    events_builder['Jet'].begin_record('Momentum4D')
                    events_builder['Jet'].field('px').real(px)
                    events_builder['Jet'].field('py').real(py)
                    events_builder['Jet'].field('pz').real(pz)
                    events_builder['Jet'].field('e').real(e)
                    events_builder['Jet'].field('pt').real(pt)
                    events_builder['Jet'].end_record()

            for key in events_builder.keys():
                events_builder[key].end_list()

    os.system('gzip %s' % lhe_file)
    print(f'Read file {lhe_file}')

    events = ak.Array({ k: v.snapshot() for k,v in events_builder.items() })
    return events


# read HepMC file using pyhepmc
def read_hepmc(hepmc_file):
    
    os.system('gunzip %s' % hepmc_file) # decompress the file
    hepmc_file = hepmc_file.replace('.gz','')

    events_builder = { k: ak.ArrayBuilder() for k in ['weight','Muon','Jet'] }

    # loop over events
    with pyhepmc.open(hepmc_file) as f:
        for event in f:
            
            for key in events_builder.keys():
               events_builder[key].begin_list()

            # event weights
            weights = [ weight for k,weight in zip(event.weight_names, event.weights) if k.startswith('rw') ]
            for weight in weights:
               events_builder['weight'].real(weight)
            
            pseudojets = list()

            # loop over particles
            for particle in event.particles:
                
                # status = 1: final state
                if particle.status != 1:
                    continue
                
                momentum = particle.momentum
                
                # Muons
                if abs(particle.pid) == 13:
                    events_builder['Muon'].begin_record('Momentum4D')
                    events_builder['Muon'].field('pdgId').integer(particle.pid)
                    events_builder['Muon'].field('px').real(momentum.px)
                    events_builder['Muon'].field('py').real(momentum.py)
                    events_builder['Muon'].field('pz').real(momentum.pz)
                    events_builder['Muon'].field('e').real(momentum.e)
                    events_builder['Muon'].field('pt').real(momentum.pt())
                    events_builder['Muon'].end_record()

                # Collect particles for jet clustering
                pseudojet = fastjet.PseudoJet(
                    momentum.px, momentum.py, momentum.pz, momentum.e
                )
                pseudojets.append(pseudojet)

            # Jet clustering
            jet_definition = fastjet.JetDefinition(fastjet.antikt_algorithm, 0.4)
            cluster = fastjet.ClusterSequence(pseudojets, jet_definition)
            jets = cluster.inclusive_jets(ptmin=10.)
            
            # Jets
            for jet in jets:
                events_builder['Jet'].begin_record('Momentum4D')
                events_builder['Jet'].field('px').real(jet.px())
                events_builder['Jet'].field('py').real(jet.py())
                events_builder['Jet'].field('pz').real(jet.pz())
                events_builder['Jet'].field('e').real(jet.e())
                events_builder['Jet'].field('pt').real(jet.pt())
                events_builder['Jet'].end_record()

            for key in events_builder.keys():
                events_builder[key].end_list()

    os.system('gzip %s' % hepmc_file)
    print(f'Read file {hepmc_file}')

    events = ak.Array({ k: v.snapshot() for k,v in events_builder.items() })
    return events


if __name__ == '__main__':

    parser = ArgumentParser()
    parser.add_argument('-i', '--input', nargs='+', default=[], help='path to input LHE or HepMC files')
    parser.add_argument('-o', '--output', default='events.pkl', help='path to output .pkl file')
    parser.add_argument('--parallel', type=int, default=1, help='number of files to read in parallel')
    args = parser.parse_args()

    if args.input[0].replace('.gz','').endswith('.lhe'):
        print('Reading LHE files')
        events = ak.concatenate(Pool(args.parallel).map(read_lhe, args.input))
        
        # normalize weights so xs = sum(weights) ### LHE: weight = xs
        events['weight'] = events['weight'] / len(events)
    
    elif args.input[0].replace('.gz','').endswith('.hepmc'):
        print('Reading HepMC files')
        events = ak.concatenate(Pool(args.parallel).map(read_hepmc, args.input))

        # normalize weights so xs = sum(weights) ### HepMC: weight = xs/nevents(file)
        events['weight'] = events['weight'] / len(args.input)

    # sort leptons and jets by pt
    lepton_sort = ak.argsort(events[('Muon', 'pt')], ascending=False, axis=1)
    jet_sort = ak.argsort(events[('Jet', 'pt')], ascending=False, axis=1)
    events['Muon'] = events.Muon[lepton_sort]
    events['Jet'] = events.Jet[jet_sort]

    # save events
    outdir = os.path.split(args.output)[0]
    if not os.path.isdir(outdir): 
        os.makedirs(outdir)

    with open(args.output, 'wb') as file:
        file.write(cloudpickle.dumps(events))


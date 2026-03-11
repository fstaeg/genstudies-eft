import hist
import numpy as np
import awkward as ak

luminosity = 138.0 # Run 2

wilson_coefficients = ['clj1', 'clj3', 'ceu', 'ced', 'cje', 'clu', 'cld']

# define selection
def selection(events):
    events['Muon'] = events.Muon[events.Muon.pt > 15]
    events = events[ak.num(events.Muon) >= 2]
    events = events[events.Muon[:,0].pt > 29]
    return events

def cos_theta_star(l1, l2):
    get_sign = lambda nr: nr/abs(nr)
    return 2*get_sign((l1+l2).pz)/(l1+l2).mass * get_sign(l1.pdgId)*(l2.pz*l1.energy-l1.pz*l2.energy)/np.sqrt(((l1+l2).mass)**2+((l1+l2).pt)**2)

# define variables 
variables = {
    'mll': {
        'function': lambda events: (events.Muon[:, 0] + events.Muon[:, 1]).mass,
        'axis': hist.axis.Variable([40,45,50,55,60,65,70,75,80,85,90,95,100,105,110,120,
            130,140,150,175,200,225,250,300]),
        'label': '$m_{\\ell\\ell}$',
        'unit': 'GeV',
        'xlog': True
    },
    'yll': {
        'function': lambda events: abs((events.Muon[:, 0] + events.Muon[:, 1]).rapidity),
        'axis': hist.axis.Regular(25, 0, 5),
        'label': '$|y_{\\ell\\ell}|$',
    },
    "costhetastar": {
        'function': lambda events: cos_theta_star(events.Muon[:, 0], events.Muon[:, 1]),
        'axis': hist.axis.Regular(50, -1, 1),
        'label': '$cos\\,\\theta^{\\ast}$',
    },
}




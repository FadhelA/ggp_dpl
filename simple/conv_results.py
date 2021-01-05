# This script allows converting the pickled data to a format that do not need
# the particles library, as it seems that it is not handled on some devices

import sys
sys.path.append('../')

import numpy as np
import argparse
import os
import pickle
from scipy.stats.mstats import mquantiles

from gamma_iid_incr import GammaIIDIncr
from gbfry_iid_incr import GBFRYIIDIncr
from nig_iid import NIGIID
from ns_iid_incr import NSIIDIncr
from ghyperbolic_iid import GHDIIDIncr
from student_iid import StudentIIDIncr
from vgamma3_iid import VGamma3IID
from vgamma4_iid import VGamma4IID

from utils import logit

parser = argparse.ArgumentParser()
parser.add_argument('--filename', type=str, default=None)
parser.add_argument('--model', type=str, default='gbfry')
parser.add_argument('--run_names', type=str, nargs='+', default=['chain1', 'chain2', 'chain3'])
parser.add_argument('--save_name')

args = parser.parse_args()

if args.model == 'gamma':
    ssm_cls = GammaIIDIncr
elif args.model == 'gbfry':
    ssm_cls = GBFRYIIDIncr
elif args.model == 'ns':
    ssm_cls = NSIIDIncr
elif args.model == 'vgamma3':
    ssm_cls = VGamma3IID
elif args.model == 'vgamma4':
    ssm_cls = VGamma4IID
elif args.model == 'nig':
    ssm_cls = NIGIID
elif args.model == 'student':
    ssm_cls = StudentIIDIncr
elif args.model == 'ghd':
    ssm_cls = GHDIIDIncr
else:
    raise NotImplementedError
prior = ssm_cls.get_prior()

if args.filename is None:
    raise ValueError('You must specify data')
else:
    data = os.path.splitext(os.path.basename(args.filename))[0]

save_dir = os.path.join('results', args.model, data)
prefix = '{}_{}'.format(data, args.model)

fig_dir = os.path.join('plots', data, args.model)
if not os.path.isdir(fig_dir):
    os.makedirs(fig_dir)

keys = prior.laws.keys()
chains = []

for run_name in args.run_names:
    with open(os.path.join(save_dir, run_name, 'chain.pkl'), 'rb') as f:
        chains.append(pickle.load(f))

gathered = {}
for key in keys:
    params = r"${}$".format(ssm_cls.params_latex[key])
    gathered[params] = []
    c_id = 1
    for chain in chains:
        val = ssm_cls.params_transform[key](chain.theta[key])
        gathered[params].append(np.array(val))
        c_id += 1

if not os.path.isdir(os.path.join(save_dir, args.save_name)):
        os.makedirs(os.path.join(save_dir, args.save_name))

with open(os.path.join(save_dir, args.save_name, "params.pkl"), 'wb') as handle:
    pickle.dump(gathered, handle, protocol=pickle.HIGHEST_PROTOCOL)




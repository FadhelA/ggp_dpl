import sys
sys.path.append('../')

import numpy as np
import numpy.random as npr
import particles.distributions as dists

from gbfry import GGPsumrnd
from utils import logit, sigmoid
from iid_incr import IIDIncr

class GammaSumDist(dists.ProbDist):
    def __init__(self, eta, sigma, c=1.0):
        self.eta = eta
        self.sigma = sigma
        self.c = c

    def rvs(self, size=1):
        return GGPsumrnd(self.eta, self.sigma, self.c, size)

class GammaIIDIncr(IIDIncr):

    params_name = {
            'log_eta':'eta',
            'log_c':'c',
            'logit_sigma':'sigma'}

    params_latex = {
            'log_eta':'\eta',
            'log_c':'c',
            'logit_sigma':'\sigma'}

    params_transform = {
            'log_eta':np.exp,
            'log_c':np.exp,
            'logit_sigma':sigmoid}

    def __init__(self,
                mu=0.,
                beta=0.,
                log_eta=np.log(0.1),
                logit_sigma=logit(0.2),
                log_c = np.log(1.),
                volumes=1.):
        super(GammaIIDIncr, self).__init__(mu=mu, beta=beta)
        self.log_eta = log_eta
        self.logit_sigma = logit_sigma
        self.log_c = log_c
        self.volumes = volumes

    def get_volume(self, t):
        if np.size(self.volumes) == 1 or np.size(self.volumes) <= t:
            return np.mean(self.volumes)
        else:
            return self.volumes[t]

    def PX0(self):
        vol = self.get_volume(0)
        eta = np.exp(self.log_eta)*vol
        sigma = sigmoid(self.logit_sigma)
        c = np.exp(self.log_c)
        return GammaSumDist(eta, sigma, c)

    def PX(self, t, xp):
        vol = self.get_volume(t)
        eta = np.exp(self.log_eta)*vol
        sigma = sigmoid(self.logit_sigma)
        c = np.exp(self.log_c)
        return GammaSumDist(eta, sigma, c)

    @staticmethod
    def get_prior():
        prior_dict = {'log_eta':dists.LogD(dists.Gamma(a=.1, b=.1)),
                'logit_sigma':dists.LogitD(dists.Beta(a=1., b=1.)),
                'log_c':dists.LogD(dists.Gamma(a=.1, b=.1))}
        return dists.StructDist(prior_dict)

    @staticmethod
    def get_theta0(y):
        prior = GammaIIDIncr.get_prior()
        theta0 = prior.rvs()
        theta0['log_c'] = np.log(1.0) + 0.1*npr.randn()
        theta0['log_eta'] = np.log(1.0) + 0.1*npr.randn()
        theta0['logit_sigma'] = sigmoid(logit(0.5) + 0.1*npr.randn())
        return theta0

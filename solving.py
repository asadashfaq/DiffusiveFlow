from __future__ import division
import sys
from time import time
import numpy as np
from multiprocessing import Pool
from diffusive import diffusiveIterator
from random import sample

"""
Different ways of calling the diffusive iterator to solve the power flows and
colormixes for different time steps and fractional constraints on the sinks.
"""

"""
Initialisation
"""
if len(sys.argv) < 2:
    raise Exception('Not enough inputs!')
else:
    task = str(sys.argv[:])

cores = 4
A = np.loadtxt('./settings/Europeadmat.txt')
K = np.load('data/K.npy')
phi = np.load('./data/phi.npy')


def solver(startPoint):
    """
    Solve a range of time steps for a fixed fraction
    """
    for t in range(int(startPoint), int(startPoint + interval)):
        i, pf, ip, lf, pn = diffusiveIterator(A, K, phi, t, frac=1, direction='export', limit=600, objective=.1)
        lf = np.sum(lf, 0)
        np.savez(savePath + str(t) + '_o_' + str(.1) + '.npz', i=i, initPower=ip, powerFrac=pf, linkFlow=lf, powerMix=pn, limit=600, objective=.1)


def fractionSolver(timeStep, fractions=None):
    """
    Solve a single time step for a range of fractions
    """
    if not fractions: fractions = np.linspace(.1, 1, 10)
    for fraction in fractions:
        i, pf, ip, lf, pn = diffusiveIterator(A, K, phi, timeStep, frac=fraction, direction='export', limit=5000, objective=.1)
        lf = np.sum(lf, 0)
        np.savez(savePath + 't_' + str(timeStep) + '_f_' + str(fraction) + '_o_' + str(.1) + '.npz', i=i, initPower=ip, powerFrac=pf, linkFlow=lf, powerMix=pn, limit=5000, objective=.1)

if 'fraction' in task:
    """
    Run the diffusive iterator on a single time step for different values of
    the fractional constraint on the sinks
    """
    print "Solving fractional sinks"
    savePath = './results/fraction/'
    usedTimes = np.load('./results/fraction/timeSteps.npy')
    timeSteps = sample(range(70128), 5)
    for i, j in enumerate(timeSteps):
        if j in usedTimes: timeSteps.pop(i)
    p = Pool(cores)
    p.map(fractionSolver, timeSteps)
    usedTimes = np.append(usedTimes, timeSteps)
    np.save('./results/fraction/timeSteps.npy', usedTimes)

if 'timeseries' in task:
    """
    Run the diffusive iterator in the entire time series. This is meant to be
    run on 4 cores
    """
    print "Solving entire time series"
    start = time()
    savePath = './results/timeseries/'
    interval = 70128 / cores
    print "Populating " + str(cores) + " workers"
    startPoints = np.linspace(0, 3, 4) * interval
    p = Pool(cores)
    p.map(solver, startPoints)
    end = time()
    print "Done"
    print "It took " + str(int(round(end - start))) + " seconds"

if 'test' in task:
    """
    A test case that was originally done by hand to check the implementation.
    """
    A = np.array([[0, 1, 0, 1, 1], [1, 0, 1, 1, 0], [0, 1, 0, 1, 0], [1, 1, 1, 0, 1], [1, 0, 0, 1, 0]])
    K = np.array([[1, 0, 0, 0, -1, 0, 1], [-1, 1, 0, 1, 0, 0, 0], [0, -1, -1, 0, 0, 0, 0], [0, 0, 1, -1, 1, 1, 0], [0, 0, 0, 0, 0, -1, -1]])
    phi = np.reshape(np.array([6, -2, 3, 2, -9]), (5, 1))
    t = 0
    i, pf, ip, lf, pn = diffusiveIterator(A, K, phi, t, frac=1, direction='export', limit=2, objective=False)

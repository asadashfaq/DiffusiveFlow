from __future__ import division
import sys
from time import time
import numpy as np
from multiprocessing import Pool
from diffusive import diffusiveIterator

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

def solver(startPoint):
    """
    Solve a range of time steps for a fixed fraction
    """
    for t in range(int(startPoint), int(startPoint+interval)):
        i, pf, ip, lf, pn = diffusiveIterator(A, K, phi, t, frac=1, direction='export', limit=500, objective=.1)
        lf = np.sum(lf, 0)
        np.savez(savePath+str(t)+'_o_'+str(.1)+'.npz', i=i, initPower=ip, powerFrac=pf, linkFlow=lf, powerMix=pn)

def fractionSolver(timeStep, fractions):
    """
    Solve a single time step for a range of fractions
    """
    for fraction in fractions:
        i, pf, ip, lf, pn = diffusiveIterator(A, K, phi, timeStep, frac=fraction, direction='export', limit=5000, objective=.1)
        lf = np.sum(lf, 0)
        np.savez(savePath+'t_'+str(t)+'_f_'+str(fraction)+'_o_'+str(.1)+'.npz', i=i, initPower=ip, powerFrac=pf, linkFlow=lf, powerMix=pn)

if 'fraction' in task:
    """
    Run the diffusive iterator on a single time step for different values of
    the fractional constraint on the sinks
    """
    print "Solving fractional sinks"
    A = np.loadtxt('./settings/Europeadmat.txt')
    K = np.load('data/K.npy')
    phi = np.load('./data/phi.npy')
    savePath = './results/fraction/'
    fractions = np.linspace(.1,1,10)
    timeSteps = [0, 100, 1000, 5000, 20000]
    for t in timeSteps:
        fractionSolver(t, fractions)

if 'timeseries' in task:
    """
    Run the diffusive iterator in the entire time series. This is meant to be
    run on 4 cores
    """
    print "Solving entire time series"
    start = time()
    A = np.loadtxt('./settings/Europeadmat.txt')
    K = np.load('data/K.npy')
    phi = np.load('./data/phi.npy')
    cores = 4
    savePath = './results/timeseries/'
    interval = 70128/cores
    print "Populating "+str(cores)+" workers"
    p = Pool(cores)
    startPoints = np.linspace(0,3,4)*interval
    p.map(solver, startPoints)
    end = time()
    print "Done"
    print "It took "+str(int(round(end-start)))+" seconds"

if 'test' in task:
    """
    A test case that was originally done by hand to check the implementation.
    """
    A = np.array([[0,1,0,1,1],[1,0,1,1,0],[0,1,0,1,0],[1,1,1,0,1],[1,0,0,1,0]])
    K = np.array([[1,0,0,0,-1,0,1],[-1,1,0,1,0,0,0],[0,-1,-1,0,0,0,0],[0,0,1,-1,1,1,0],[0,0,0,0,0,-1,-1]])
    phi = np.reshape(np.array([6,-2,3,2,-9]),(5,1))
    t = 0
    i, pf, ip, lf, pn = diffusiveIterator(A, K, phi, t, frac=1, direction='export', limit=2, objective=False)

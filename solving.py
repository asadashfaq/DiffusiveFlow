from __future__ import division
import sys
from time import time
import numpy as np
from multiprocessing import Pool
from diffusive import diffusiveIterator

"""
DOCSTRING
"""

"""
Initialisation
"""
#if len(sys.argv) < 2:
#    raise Exception('Not enough inputs!')
#else:
task = str(sys.argv[:])

def solver(startPoint):
    """
    """
    for t in range(int(startPoint), int(startPoint+interval)):
        i, pf, ip, lf, pn = diffusiveIterator(A, K, phi, t, frac=1, direction='export', objective=.1)
        np.savez(savePath+str(t)+'_o_'+str(.1)+'.npz', i=i, powerFrac=pf, linkFlow=lf, powerMix=pn)

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

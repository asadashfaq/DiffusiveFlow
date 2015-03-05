from __future__ import division
import numpy as np

"""
A collection of commonly used functions.
"""


def nodeDegree(A, n):
    """
    Calculate node degree(s) from adjacency matrix. Input can be a single index
    or a list of indices.
    """
    if not (type(n) == int or type(n) == list):
        raise Exception('input type should be _int_ or _list_')
    if type(n) == int:
        return int(sum(A[n]))
    if type(n) == list:
        return np.array([nodeDegree(A, i) for i in n])


def norm(v):
    """
    Normalise input vector.
    """
    if sum(v) != 0:
        return v / sum(v)
    else:
        print('Sum of vector equals zero. Returning un-normalised vector')
        return v


def iterationStats(timeSteps, limit=None, fraction=False, save=False):
    """
    Calculate stats for selected time steps
    timeSteps:  input integer or list
    limit:      the limit of iterations in the solver
    save:       True saves results to file. False prints results in terminal
    """
    if fraction:
        loadPath = './results/fraction/'
        if not Limit: limit = 5000
    else:
        loadPath = './results/timeseries/'
        if not limit: limit = 500
    if not (type(timeSteps) == int or type(timeSteps) == list):
        raise Exception('input type should be _int_ or _list_')

    if type(timeSteps) == int:
        d = np.load(loadPath + str(timeSteps) + '_o_' + str(.1) + '.npz')
        iteration = d['i']
        initPower = d['initPower']
        powerFrac = d['powerFrac']
        print 'Time step: ', timeSteps
        print 'Iterations: ', iteration
        print 'Initial power [W]: ', int(round(initPower))
        print 'Remaining power: ', '%.3f' % powerFrac + '%'

    if type(timeSteps) == list:
        iteration = np.zeros(len(timeSteps))
        initPower = np.zeros(len(timeSteps))
        powerFrac = np.zeros(len(timeSteps))
        for i, t in enumerate(timeSteps):
            d = np.load(loadPath + str(t) + '_o_' + str(.1) + '.npz')
            iteration[i] = d['i']
            initPower[i] = d['initPower']
            powerFrac[i] = d['powerFrac']
        if save:
            np.savez('./results/stats_' + str(int(len(timeSteps))) + '.npz', iteration=iteration, initPower=initPower, powerFrac=powerFrac)
        if len(timeSteps) > 1:
            print 'Time step: ', str(timeSteps[0]) + ':' + str(timeSteps[-1])
        else:
            print 'Time step: ', timeSteps
        print 'Iterations [min, max, mean]: ', int(min(iteration)), int(max(iteration)), int(round(np.mean(iteration)))
        print 'Fraction of maxed iterations: ', len(np.where(iteration == limit)[0]), '/', len(timeSteps)
        print 'Initial power [W] [min, max, mean]: ', int(min(initPower)), int(max(initPower)), int(np.mean(initPower))
        print 'Remaining power [min, max, mean]: ', '%.3f' % min(powerFrac) + '%', '%.3f' % max(powerFrac) + '%', '%.3f' % np.mean(powerFrac) + '%'

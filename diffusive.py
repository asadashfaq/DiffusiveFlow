from __future__ import division
import numpy as np

"""
Diffusive iterator to solve and trace power flow

To do:
- split injection pattern in P+ and P-
- scale adjacency matrix with node degree
- iterator
    - multiply modified adjacency matrix with positive part of injection: R
    - compare R with P-
    - update P-
    - update P+
    - check convergence (how much power is still flowing?)

"""

def nodeDegree(A, n):
    """
    Calculalte node degree from adjacency matrix
    """
    if type(n) == int:
        return int(sum(A[n]))
    if type(n) == list:
        return np.array([nodeDegree(A,i) for i in n])

def diffusiveIterator(A, phi, timeStep, limit=False, objective=False):
    """
    A:          adjacency matrix
    phi:        injection pattern
    timeStep:   what hour of the time series to solve
    limit:      maximum number of iterations
    objective:  convergence limit
    """

    nodes = A.shape[0]
    degrees = nodeDegree(A, range(nodes))

    posIndex = np.where(phi[timeStep] > 0)
    negIndex = np.where(phi[timeStep] < 0)

    # pp: positive part of injection
    # pn: negative part of injection
    pp, pn = np.zeros(nodes), np.zeros(nodes)

    for i, p in enumerate(phi[:, timeStep]):
        if p > 0: pp[i] = p
        if p < 0: pn[i] = p
    initPower = sum(pp)
    print 'initPower: ',initPower
    # Adjacency matrix scaled with node degrees. Column i is divided by the
    # degree of node i.
    Amod = np.array([A[i] / degrees[i] for i in range(nodes)]).transpose()


    # ITERATE
    iterate = True
    iteration = 0
    while(iterate):
        iteration += 1
        # multiply Amod with P+
        R = np.dot(Amod, pp)
        pp = np.zeros(nodes)

        # compare R with P-
        # update P-, P+
        for i, p in enumerate(R):
            if p == 0:
                continue
            elif p <= abs(pn[i]):
                pn[i] += p
            elif p > abs(pn[i]):
                pp[i] = p + pn[i]
                pn[i] = 0

        # check convergence
        powerFrac = sum(pp)/initPower*100
        print iteration,' powerFrac: ',powerFrac
        if limit:
            if iteration == limit: iterate = False
        if objective:
            if powerFrac <= objective: iterate = False

    return iteration, powerFrac

# Test function
A = np.loadtxt('./settings/Europeadmat.txt')
phi = np.load('./data/phi.npy')
t = 10

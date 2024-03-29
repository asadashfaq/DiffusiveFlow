from __future__ import division
import numpy as np
from functions import nodeDegree, norm

"""
Diffusive iterator to solve and trace power flow
"""


def diffusiveIterator(A, K, phi, timeStep, frac=1, direction='export', limit=False, objective=False):
    """
    A:          adjacency matrix
    K:          incidence matrix
    phi:        injection pattern
    timeStep:   what hour of the time series to solve
    frac:       the fraction of available power that sinks are allowed to get
    direction:  'export' or 'import'. What flows we are looking for
    limit:      maximum number of iterations
    objective:  convergence objective - percentage of total initial injection

    It is possible to give the iterator both a limit and an objective. In such
    a case the iterator stops when it reaches the objective or the limit. In
    case none of them is set the iterator runs for 100 iterations and returns.
    """

    if not (limit or objective): limit = 100

    if direction == 'import':
        phi = -phi
        K = -K

    nodes = A.shape[0]
    degrees = nodeDegree(A, range(nodes))
    links = len(np.where(A)[0]) / 2

    # pp: positive part of injection pattern
    # pn: negative part of injection pattern
    pp, pn = np.zeros((nodes, nodes)), np.zeros((nodes, nodes))

    for i, p in enumerate(phi[:, timeStep]):
        if p > 0: pp[i, i] = p
        if p < 0: pn[i, i] = p
    initPower = sum(sum(pp))

    # Adjacency matrix scaled with node degrees. Column i is divided by the
    # degree of node i.
    Amod = np.array([A[i] / degrees[i] for i in range(nodes)]).transpose()

    # Prepare vectors for saving flow
    linkFlow = np.zeros((nodes, links, nodes))

    # Iterate if more than 1W is injected in total
    iteration = 0
    if initPower < 1:
        iterate = False
        powerFrac = 0
    else:
        iterate = True

    while(iterate):
        iteration += 1
        R = np.zeros((nodes, nodes))
        for i in range(nodes):
            R += np.array(np.dot(np.reshape(Amod[:, i], (nodes, 1)), np.reshape(pp[i], (1, nodes))))

        # update colors and link flows
        for n in range(nodes):
            linkFlow[n, :, :] += np.outer(K[n], pp[n] / degrees[n])

        # compare R with P-, update P-, P+
        pp = np.zeros((nodes, nodes))
        for i, p in enumerate(R):
            if np.round(sum(pn[i]), 3) == 0:
                pp[i] = p
            if np.round(sum(pn[i]), 3) < 0:
                pn[i] += frac * p
                pp[i] += (1 - frac) * p
            if np.round(sum(pn[i]), 3) > 0:
                sinkStrength = pn[i, i]
                sourceStrength = sum(pn[i])
                pn[i, i] = 0
                pn[i] = norm(pn[i]) * abs(sinkStrength)
                pn[i, i] = sinkStrength
                pp[i] += norm(p) * sourceStrength

        # check convergence
        powerFrac = sum(sum(pp)) / initPower * 100
        if limit:
            if iteration == limit: iterate = False
        if objective:
            if powerFrac <= objective: iterate = False

    return iteration, powerFrac, initPower, linkFlow, pn

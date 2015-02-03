from __future__ import division
import numpy as np

"""
Diffusive iterator to solve and trace power flow
"""

def nodeDegree(A, n):
    """
    Calculalte node degree from adjacency matrix
    """
    if type(n) == int:
        return int(sum(A[n]))
    if type(n) == list:
        return np.array([nodeDegree(A,i) for i in n])

def normalise(v):
    if sum(v) != 0:
        return v/sum(v)
    else: return v

def diffusiveIterator(A, K, phi, timeStep, limit=False, objective=False):
    """
    A:          adjacency matrix
    K:          incidence matrix
    phi:        injection pattern
    timeStep:   what hour of the time series to solve
    limit:      maximum number of iterations
    objective:  convergence objective - percentage of total initial injection

    It is possible to give the iterator both a limit and an objective. In such
    a case the iterator stops when it reaches the objective or the limit. In
    case none of them is set the iterator runs for 100 iterations and returns.
    """

    if not (limit or objective): limit = 100

    nodes = A.shape[0]
    degrees = nodeDegree(A, range(nodes))
    links = len(np.where(A)[0])/2

    # pp: positive part of injection
    # pn: negative part of injection
    pp, pn = np.zeros(nodes), np.zeros(nodes)

    for i, p in enumerate(phi[:, timeStep]):
        if p > 0: pp[i] = p
        if p < 0: pn[i] = p
    initPower = sum(pp)

    # Adjacency matrix scaled with node degrees. Column i is divided by the
    # degree of node i.
    Amod = np.array([A[i] / degrees[i] for i in range(nodes)]).transpose()

    # Prepare vectors for saving flow and power mixes
    linkFlow = np.zeros((nodes, links))
    nodeColor = np.zeros((nodes, nodes))

    # ITERATE
    iterate = True
    iteration = 0
    while(iterate):
        iteration += 1
        R = np.dot(Amod, pp)

        # update colors and link flows
        nodeColor += np.multiply(Amod, pp)
        linkFlow += np.array([K[i]*pp[i]/degrees[i] for i in range(nodes)])

        # compare R with P-, update P-, P+
        pp = np.zeros(nodes)
        for i, p in enumerate(R):
            if p == 0: continue
            elif p <= abs(pn[i]):
                pn[i] += p
            elif p > abs(pn[i]):
                pp[i] = p + pn[i]
                pn[i] = 0

        # check convergence
        powerFrac = sum(pp)/initPower*100
        if limit:
            if iteration == limit: iterate = False
        if objective:
            if powerFrac <= objective: iterate = False

    # normalise colors and sum link flows before returning
    nodeColor = np.array([normalise(nodeColor) for i in range(nodes)])
    linkFlow = np.sum(linkFlow, axis=0)

    return iteration, powerFrac, nodeColor, linkFlow, initPower

# Test function
A = np.loadtxt('./settings/Europeadmat.txt')
K = np.load('data/K.npy')
phi = np.load('./data/phi.npy')
t = 10

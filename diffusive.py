from __future__ import division
import numpy as np

"""
Diffusive iterator to solve and trace power flow
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
        return np.array([nodeDegree(A,i) for i in n])

def norm(v):
    """
    Normalise input vector.
    """
    if sum(v) != 0:
        return v/sum(v)
    else:
        print('Sum of vector equals zero. Returning un-normalised vector')
        return v

def diffusiveIterator(A, phi, timeStep, limit=False, objective=False):
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

    # pp: positive part of injection pattern
    # pn: negative part of injection pattern
    pp, pn = np.zeros((nodes, nodes)), np.zeros((nodes, nodes))

    for i, p in enumerate(phi):
        if p > 0: pp[i,i] = p
        if p < 0: pn[i,i] = p
    initPower = sum(sum(pp))

    # Adjacency matrix scaled with node degrees. Column i is divided by the
    # degree of node i.
    Amod = np.array([A[i] / degrees[i] for i in range(nodes)]).transpose()

    # Prepare vectors for saving flow
    linkFlow = np.zeros((nodes, links))

    # ITERATE
    iterate = True
    iteration = 0
    while(iterate):
        iteration += 1
        R = np.zeros((nodes, nodes))
        for i in range(nodes):
            R += np.array(np.dot(np.reshape(Amod[:,i], (nodes,1)), np.reshape(pp[i], (1, nodes))))

        # update colors and link flows
        # linkFlow += np.array([K[i]*np.sum(pp, axis=1)[i]/degrees[i] for i in range(nodes)])

        # compare R with P-, update P-, P+
        pp = np.zeros((nodes, nodes))
        for i, p in enumerate(R):
            if sum(pn[i]) == 0:
                pp[i] = p
            if sum(pn[i]) < 0:
                pn[i] += p
            if sum(pn[i]) > 0:
                sink = pn[i,i]
                pn[i] /= np.abs(sink)
                pn[i,i] = sink
                pp[i] = norm(p)*sum(pn[i])

        # check convergence
        powerFrac = sum(sum(pp))/initPower*100
        if limit:
            if iteration == limit: iterate = False
        if objective:
            if powerFrac <= objective: iterate = False

    # sum link flows before returning
    linkFlow = np.sum(linkFlow, axis=0)

    return iteration, powerFrac, linkFlow, initPower, Amod, R, pp, pn

# Test function
# A = np.loadtxt('./settings/Europeadmat.txt')
# K = np.load('data/K.npy')
# phi = np.load('./data/phi.npy')
A = np.array([[0,1,0,1,1],[1,0,1,1,0],[0,1,0,1,0],[1,1,1,0,1],[1,0,0,1,0]])
phi = np.array([6,-2,3,2,-9])
t = 0

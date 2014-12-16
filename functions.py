# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 20:38:34 2014

@author: Bo Tranberg

A collection of functions used for the diffusive approach to flow tracing.

"""
import time
import numpy as np

"""
    Phi = np.load('./data/phi.npy')
    K = np.load('./data/K.npy')
    F = np.load('./data/F.npy')
"""

def convergenceCheck(F, LinkValuePos, LinkValueNeg):
    """
    Check convergence of diffusive flow to solver flow.
    """
    LinkValue = LinkValuePos + LinkValueNeg
    LinkDist = sum(LinkValue, axis=2)
    FlowCheck= sum(LinkDist[:, :], axis=0) - F
    return np.mean(np.abs(FlowCheck))

def diffusiveIterator(Phi, K, F, objective, fraction=1, direction='export', verbose=False):
    start = time.time()
    NodeIte = 2000 # maximum number of iterations
    Nodes, Links = K.shape
    RoundSumPhi = round(sum(Phi), 2)
    if verbose: print 'Sum of initial node Values: ' + str("%.5f" % RoundSumPhi)

    if direction == 'import':
        Phi = -Phi
        K = -K

    NodeValue = np.zeros((Nodes, Nodes, NodeIte))  # work horse
    NodeValueSave = np.zeros((Nodes, Nodes, NodeIte))  # for the archives
    NodeValueSave2 = np.zeros((Nodes, Nodes, NodeIte))  # overflow values

    # Puts the injection pattern on the diagonal of the NodeValue matrix    
    np.fill_diagonal(NodeValue[:, :, 0], Phi)
    np.fill_diagonal(NodeValueSave[:, :, 0], Phi)

    # store link values in positive direction
    LinkValuePos = np.zeros((Nodes, Links, NodeIte))
    # store link values in negative direction
    LinkValueNeg = np.zeros((Nodes, Links, NodeIte))

    # array of row numbers with starting negative injection pattern
    PhiNeg = [i for i, j in enumerate(Phi) if j < 0]

    iteration = 0
    PosNegLinkRun = 0
    noderun = 0
    linkrun = 0
    d = 0
    e = 0
    
    meanFlow = objective + 1
    meanFlow2 = None
    
    while meanFlow > objective:

        for noderun in range(0, Nodes):  # run through all node
            # node is sink and ejects all
            if sum(NodeValue[:, noderun, iteration]) <= 0:
                NodeValue[noderun, noderun, iteration + 1] += np.sum(NodeValue[:, noderun, iteration]) * fraction
                NodeValueSave[noderun, noderun, iteration + 1] += np.sum(NodeValue[:, noderun, iteration]) * fraction

            else:  # if the sum of a node is positive:
                if np.min(NodeValue[noderun, noderun, iteration]) < 0:
                    # if the average is larger than zero but it contains a negativ number
                    # - node is a sink, but there is going to be overflow
                    givefraction = np.abs(NodeValue[noderun, noderun, iteration]) / np.sum(NodeValue[:, noderun, iteration].clip(0)) * fraction
                    # how much of each node that is ejected
                    injectfraction = 1 - givefraction
                    # how much of each node that is injected again.

                    NodeValueSave2[:, noderun, iteration] = NodeValueSave[:, noderun, iteration] * givefraction
                    # to have the value of ejected
                    NodeValueSave[:, noderun, iteration] = NodeValueSave[:, noderun, iteration] * injectfraction
                    # to save the value of injected

                    NodeValue[:, noderun, iteration] = NodeValue[:, noderun, iteration] * injectfraction
                    # node values after ejection
                    NodeValueSave2[noderun, noderun, iteration] = 0
                    # sink is full
                    NodeValue[noderun, noderun, iteration] = 0
                    NodeValueSave[noderun, noderun, iteration] = 0

                    NOL = abs(K[noderun, :]).sum() * 1.  # Number of links
                    # devide node value with number of links
                    NewValue = NodeValue[:, noderun, iteration] / NOL
                    for PosNegLinkRun in range(0, Links):
                        if K[noderun, PosNegLinkRun] > 0:
                            LinkValuePos[:, PosNegLinkRun, iteration] = LinkValuePos[:, PosNegLinkRun, iteration] + NewValue
                        if K[noderun, PosNegLinkRun] < 0:
                            LinkValueNeg[:, PosNegLinkRun, iteration] = LinkValueNeg[:, PosNegLinkRun, iteration] - NewValue

                    NodeValue[:, noderun, iteration] = 0

                else:
                    NOL = abs(K[noderun, :]).sum() * 1.  # Number of links
                    # devide node value with number of links
                    NewValue = NodeValue[:, noderun, iteration] / NOL
                    for PosNegLinkRun in range(0, Links):
                        if K[noderun, PosNegLinkRun] == 1:
                            LinkValuePos[:, PosNegLinkRun, iteration] = LinkValuePos[:, PosNegLinkRun, iteration] + NewValue
                        if K[noderun, PosNegLinkRun] == -1:
                            LinkValueNeg[:, PosNegLinkRun, iteration] = LinkValueNeg[:, PosNegLinkRun, iteration] - NewValue

                    NodeValueSave[:, noderun, iteration] = NodeValue[:, noderun, iteration]
                    NodeValue[:, noderun, iteration] = 0.
                    # node values saved and removed

        # Inject what is on the links to the right node.
        for linkrun in range(0, Links):
            for d in range(0, Nodes):
                if K[d, linkrun] == -1:
                    NodeValue[:, d, iteration + 1] += LinkValuePos[:, linkrun, iteration]
                    NodeValueSave[:, d, iteration + 1] += LinkValuePos[:, linkrun, iteration]
            for e in range(0, Nodes):
                if K[e, linkrun] == 1:
                    NodeValue[:, e, iteration + 1] += abs(LinkValueNeg[:, linkrun, iteration])
                    NodeValueSave[:, e, iteration + 1] += abs(LinkValueNeg[:, linkrun, iteration])

        meanFlow = convergenceCheck(F, LinkValuePos, LinkValueNeg)

        iteration += 1

        if iteration == NodeIte-1:
            meanFlow2 = meanFlow
            meanFlow = objective-1

    if verbose:
        print 'Iterations: ',iteration
        if meanFlow2:
            print 'Final calculated flow minus given flow: ' + str("%.5f" % meanFlow2)
        else:
            print 'Final calculated flow minus given flow: ' + str("%.5f" % meanFlow)

    NodeDist = sum(NodeValue, axis=2) + sum(NodeValueSave2, axis=2)
    LinkValue = LinkValuePos + LinkValueNeg
    LinkDist = sum(LinkValue, axis=2)

    a = 0
    for a in PhiNeg:
        NodeDist[a, a] = - np.max(NodeValueSave[a, a, :])

    takentime = np.round((time.time() - start) / iteration * 1000, 2)
    if verbose: print 'It took', takentime, 'milliseconds per iteration.'
    if verbose: print 'It took', np.round(time.time() - start, 2), 'seconds in total.'
    return  NodeDist, LinkDist, iteration
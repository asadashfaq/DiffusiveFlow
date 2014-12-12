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


def diffusiveIterator(timeStep, injectionPattern, K, F, nIterations,
                      direction='export'):
    start = time.time()
    NodeIte = nIterations
    Phi = injectionPattern[:, timeStep]
    Nodes, Links = K.shape
    RoundSumPhi = round(sum(Phi), 2)
    print 'Sum of initial node Values: ' + str("%.5f" % RoundSumPhi)

    if direction == 'import':
        Phi = -Phi

    NodeValue = np.zeros((Nodes, Nodes, NodeIte))  # work horse
    NodeValueSave = np.zeros((Nodes, Nodes, NodeIte))  # for the archives
    NodeValueSave2 = np.zeros((Nodes, Nodes, NodeIte))  # overflow values

    NodeInitial = 0
    # Puts the injection pattern on the diagonal of the NodeValue matrix
    for NodeInitial in range(0, Nodes):
        NodeValue[NodeInitial, NodeInitial, 0] = Phi[NodeInitial]
        NodeValueSave[NodeInitial, NodeInitial, 0] = Phi[NodeInitial]

    # store link values in positive direction
    LinkValuePos = np.zeros((Nodes, Links, NodeIte))
    # store link values in negative direction
    LinkValueNeg = np.zeros((Nodes, Links, NodeIte))

    # array of row numbers with starting negative injection pattern
    PhiNeg = [i for i, j in enumerate(Phi) if j < 0]

    # to display node number and start injection pattern
    Lande = np.zeros((Nodes, 2))
    Lande[:, 0] = range(0, Nodes)
    Lande[:, 1] = Phi

    iteration = 0
    PosNegLinkRun = 0
    noderun = 0
    linkrun = 0
    d = 0
    e = 0
    for iteration in range(0, NodeIte - 1):  # run for iterations
        for noderun in range(0, Nodes):  # run through all node

            # node is sink and ejects all
            if sum(NodeValue[:, noderun, iteration]) <= 0:
                NodeValue[noderun, noderun, iteration +
                          1] += np.sum(NodeValue[:, noderun, iteration])
                NodeValueSave[noderun, noderun, iteration + 1] += np.sum(NodeValue[:, noderun, iteration])

            else:  # if the sum of a node is positive:
                if np.min(NodeValue[noderun, noderun, iteration]) < 0:
                    # if the average is larger than zero but it contains a negativ number
                    # - node is a sink, but there is going to be overflow
                    givefraction = np.abs(NodeValue[noderun, noderun, iteration]) / np.sum(NodeValue[:, noderun, iteration].clip(0))
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

    NodeValue2D = np.zeros((Nodes, NodeIte))
    LinkValue = np.zeros((Nodes, Links, NodeIte))

    LinkValue[:, :, :] = LinkValuePos[:, :, :] + LinkValueNeg[:, :, :]

    # NodeValueSave2 for overflow
    NodeDist = sum(NodeValue, axis=2) + sum(NodeValueSave2, axis=2)
    LinkDist = sum(LinkValue, axis=2)

    NodeValue2D = np.sum(NodeValueSave, axis=0)

    LinkValue2D = np.sum(LinkValue, axis=0)
    AcumSumLink = np.cumsum(LinkValue2D, axis=1)

    takentime = np.round((time.time() - start) / NodeIte * 1000, 2)

    a = 0
    for a in PhiNeg:
        NodeDist[a, a] = - np.max(NodeValueSave[a, a, :])
    Phitjek1 = sum(NodeDist, axis=1) - Phi.T.clip(0)
    Phitjek2 = sum(NodeDist, axis=0) - np.abs(Phi.T.clip(-100000000000000, 0))
    Flowtjek = sum(LinkDist[:, :], axis=0) - F[:, timeStep]
    print 'Final Injection pattern max value: ' + str("%.5f" % np.max(np.abs(Phitjek1)))
    print 'Final calculated flow minus given flow: ' + str("%.5f" % np.max(np.abs(Flowtjek)))
    print 'It took', takentime, 'milliseconds per iteration.'
    return  NodeDist, LinkDist, Lande

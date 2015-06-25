from __future__ import division
import sys
import math
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap
from figutils import *

"""
Investigating correlation of power mixes between diffusive flow and up/down
stream approach for different fraction constraints on the sinks.

Ways of calling:
plot:   plot color mesh of correlation of power mixes for different fractions
avg:    same as above but averaged over a specified number of hours. Include
        number of hours as second command line argument. See examples below.
link:   same as 'plot' but for links

example:
python fractionCorrelation.py plot
python fractionCorrelation.py avg 100

'plot' can be called with an integer as an optional argument, so it only plots
figures for that particular time step. Example:
python fractionCorrelation.py plot 10
"""

"""
Initialisation
"""
if len(sys.argv) < 2:
    raise Exception('Not enough inputs!')
else:
    task = str(sys.argv[:])
nodes = 30
fractions = np.linspace(.1, 1, 10)
timeSteps = np.load('./results/fraction/timeSteps.npy')
rr = 3  # rounding of power mixes, number of decimal places
Blues_cmap = LinearSegmentedColormap('blue', Blues_data, 1000)

if 'plot' in task:
    if len(sys.argv) > 2:
        try:
            timeSteps = [int(sys.argv[2])]
        except ValueError:
            timeSteps = timeSteps
    phi = np.load('./data/phi.npy')
    # Load power mixes from up/down stream approach
    upDownPowerMix = np.load('./input/linear_pm.npz', mmap_mode='r')
    # settings for figures
    titles = ['', '-load', '-degree']
    orders = [range(30), loadOrder, degreeOrder]
    nameList = [names, loadNames, degreeNames]
    norm = mpl.colors.Normalize(vmin=0, vmax=1)

    for t in timeSteps:
        t = int(t)
        pmex = upDownPowerMix['power_mix_ex'][:, :, t]
        pmim = upDownPowerMix['power_mix'][:, :, t]

        # Remove self import/export from up/down stream approach
        for n in range(nodes):
            if round(phi[n, t], rr) > 0:
                pmim[n, n] = 0
            if round(phi[n, t], rr) < 0:
                pmex[n, n] = 0

        # Load power mixes from diffusive iterator
        iteration = np.zeros(len(fractions))
        initPower = np.zeros(len(fractions))
        powerFrac = np.zeros(len(fractions))
        linkFlow = np.zeros((len(fractions), 50, 30))
        powerMix = np.zeros((len(fractions), 30, 30))

        for i, f in enumerate(fractions):
            d = np.load('./results/fraction/t_' + str(t) + '_f_' + str(f) + '_o_0.1.npz')
            iteration[i] = d['i']
            initPower[i] = d['initPower']
            powerFrac[i] = d['powerFrac']
            linkFlow[i] = d['linkFlow']
            pm = d['powerMix']
            np.fill_diagonal(pm, 0)
            powerMix[i] = pm

        # compare power mixes from the two approaches
        # if node is a sink compare imports, if node is a source compare exports
        corr = np.zeros((nodes, len(fractions)))
        newNames = np.copy(names)
        for n in range(nodes):
            if round(phi[n, t], rr) == 0:
                newNames[n] = names[n]
                for i in range(len(fractions)):
                    corr[n, i] = 0
            if round(phi[n, t], rr) > 0:
                newNames[n] = '+ ' + names[n]
                for i in range(len(fractions)):
                    tempCorr = pearsonr(pmex[n], powerMix[i, :, n])[0]
                    if math.isnan(tempCorr):
                        corr[n, i] = 0
                    else:
                        corr[n, i] = tempCorr
            if round(phi[n, t], rr) < 0:
                newNames[n] = '- ' + names[n]
                for i in range(len(fractions)):
                    tempCorr = pearsonr(pmim[n], powerMix[i, n, :])[0]
                    if math.isnan(tempCorr):
                        corr[n, i] = 0
                    else:
                        corr[n, i] = tempCorr

        for m in range(3):
            title = titles[m]
            order = orders[m]
            names = nameList[m]

            plt.figure()
            ax = plt.subplot()
            plt.pcolormesh(corr[order], norm=norm, cmap=Blues_cmap)
            cbl = plt.colorbar()
            cbl.set_label(label='pearson correlation', size=11)
            cbl.solids.set_edgecolor('face')
            ax.set_xticks(np.linspace(.5, 9.5, 10))
            ax.set_xticklabels(np.linspace(.1, 1, 10))
            ax.set_yticks(np.linspace(.5, 29.5, 30))
            ax.set_yticklabels(newNames[order], ha="right", va="center", fontsize=8)
            plt.xlabel(r'$\eta$')
            plt.savefig('./figures/fraction correlation/fc_t_' + str(t) + title + '.pdf', bbox_inches='tight')
            plt.close()

if 'avg' in task:
    if len(sys.argv) > 2:
        try:
            hours = int(sys.argv[2])
        except ValueError:
            raise ValueError('Input number of hours to include as second command line argument')
    else:
        raise ValueError('Input number of hours to include as second command line argument')
    importCorr = np.zeros((nodes, len(fractions)))
    exportCorr = np.zeros((nodes, len(fractions)))
    phi = np.load('./data/phi.npy')
    upDownPowerMix = np.load('./input/linear_pm.npz', mmap_mode='r')
    timeSteps = range(hours)
    corrTimesIm = np.zeros((nodes, len(fractions)))
    corrTimesEx = np.zeros((nodes, len(fractions)))
    for t in timeSteps:
        t = int(t)
        pmex = upDownPowerMix['power_mix_ex'][:, :, t]
        pmim = upDownPowerMix['power_mix'][:, :, t]

        # Remove self import/export from up/down stream approach
        for n in range(nodes):
            if round(phi[n, t], rr) > 0:
                pmim[n, n] = 0
            if round(phi[n, t], rr) < 0:
                pmex[n, n] = 0

        # Load power mixes from diffusive iterator
        powerMix = np.zeros((len(fractions), 30, 30))
        for i, f in enumerate(fractions):
            d = np.load('./results/fraction/t_' + str(t) + '_f_' + str(f) + '_o_0.1.npz')
            pm = d['powerMix']
            np.fill_diagonal(pm, 0)
            powerMix[i] = pm

        # compare power mixes from the two approaches
        # if node is a sink compare imports, if node is a source compare exports
        corr = np.zeros((nodes, len(fractions)))
        for n in range(nodes):
            if round(phi[n, t], rr) == 0: continue
            if round(phi[n, t], rr) > 0:
                for i in range(len(fractions)):
                    tempCorr = pearsonr(pmex[n], powerMix[i, :, n])[0]
                    if not math.isnan(tempCorr):
                        exportCorr[n, i] += tempCorr
                        corrTimesEx[n, i] += 1
            if round(phi[n, t], rr) < 0:
                for i in range(len(fractions)):
                    tempCorr = pearsonr(pmim[n], powerMix[i, n, :])[0]
                    if not math.isnan(tempCorr):
                        importCorr[n, i] += tempCorr
                        corrTimesIm[n, i] += 1

    # average correlations for each fraction over all time steps
    corrTimesIm[np.where(corrTimesIm == 0)] = 1
    corrTimesEx[np.where(corrTimesEx == 0)] = 1
    exportCorr = exportCorr / corrTimesEx
    importCorr = importCorr / corrTimesIm

    # plot import and export side by side and sort in 3 different ways
    titles = ['', '-load', '-degree']
    orders = [range(30), loadOrder, degreeOrder]
    nameList = [names, loadNames, degreeNames]
    norm = mpl.colors.Normalize(vmin=0, vmax=1)
    for m in range(3):
        title = titles[m]
        order = orders[m]
        names = nameList[m]

        plt.figure(figsize=(11, 5))
        ax = plt.subplot(121)
        plt.pcolormesh(exportCorr[order], norm=norm, cmap=Blues_cmap)
        cbl = plt.colorbar()
        cbl.set_label(label='pearson correlation', size=11)
        cbl.solids.set_edgecolor('face')
        ax.set_xticks(np.linspace(.5, 9.5, 10))
        ax.set_xticklabels(np.linspace(.1, 1, 10))
        ax.set_yticks(np.linspace(.5, 29.5, 30))
        ax.set_yticklabels(names, ha="right", va="center", fontsize=8)
        plt.xlabel(r'$\eta$')

        ax = plt.subplot(122)
        plt.pcolormesh(importCorr[order], norm=norm, cmap=Blues_cmap)
        cbl = plt.colorbar()
        cbl.set_label(label='pearson correlation', size=11)
        cbl.solids.set_edgecolor('face')
        ax.set_xticks(np.linspace(.5, 9.5, 10))
        ax.set_xticklabels(np.linspace(.1, 1, 10))
        ax.set_yticks(np.linspace(.5, 29.5, 30))
        ax.set_yticklabels(names, ha="right", va="center", fontsize=8)
        plt.xlabel(r'$\eta$')
        plt.savefig('./figures/avg/power_mix_correlation-' + str(len(timeSteps)) + title + '.pdf', bbox_inches='tight')

from __future__ import division
import sys
import numpy as np
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import matplotlib as mpl

"""
Investigating correlation of power mixes between diffusive flow and up/down
stream approach for different fraction constraints on the sinks.

Ways of calling:
plot:   plot color mesh of correlation of power mixes for different fractions
avg:    same as above but averaged over a specified number of hours. Include
        number of hours as second command line argument. See examples below.
link:   same as 'plot' but for links

example:
python fractionCorrelation.py plot load
python fractionCorrelation.py avg 100 load
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

names = np.array(['AT', 'FI', 'NL', 'BA', 'FR', 'NO', 'BE', 'GB', 'PL', 'BG',
                  'GR', 'PT', 'CH', 'HR', 'RO', 'CZ', 'HU', 'RS', 'DE', 'IE',
                  'SE', 'DK', 'IT', 'SI', 'ES', 'LU', 'SK', 'EE', 'LV', 'LT'],
                 dtype='|S4')

# Node indices and names sorted after descending mean load
loadOrder = [18, 4, 7, 22, 24, 20, 8, 5, 2, 6, 1, 15, 0, 10, 14,
             9, 11, 12, 16, 21, 17, 19, 3, 26, 13, 29, 27, 23, 28, 25]

loadNames = np.array(['DE', 'FR', 'GB', 'IT', 'ES', 'SE', 'PL', 'NO', 'NL',
                      'BE', 'FI', 'CZ', 'AT', 'GR', 'RO', 'BG', 'PT', 'CH',
                      'HU', 'DK', 'RS', 'IE', 'BA', 'SK', 'HR', 'LT', 'EE',
                      'SI', 'LV', 'LU'], dtype='|S4')

# Node indices and names ordered after descending node degree
degreeOrder = [18, 0, 4, 22, 20, 17, 16, 13, 2, 8, 12, 15, 5, 7, 9,
               14, 21, 23, 26, 28, 10, 24, 6, 3, 27, 1, 19, 11, 25, 29]

degreeNames = np.array(['DE', 'AT', 'FR', 'IT', 'SE', 'RS', 'HU', 'HR', 'NL',
                        'PL', 'CH', 'CZ', 'NO', 'GB', 'BG', 'RO', 'DK', 'SI',
                        'SK', 'LV', 'GR', 'ES', 'BE', 'BA', 'EE', 'FI', 'IE',
                        'PT', 'LU', 'LT'], dtype='|S4')

if 'load' in task:
    order = loadOrder
    names = loadNames
    title = '-load'
elif 'degree' in task:
    order = degreeOrder
    names = degreeNames
    title = '-degree'
else:
    order = range(30)
    names = names
    title = ''

if 'plot' in task:
    phi = np.load('./data/phi.npy')
    # Load power mixes from up/down stream approach
    upDownPowerMix = np.load('./input/linear_pm.npz', mmap_mode='r')
    for t in timeSteps:
        t = int(t)
        pmex = upDownPowerMix['power_mix_ex'][:, :, t]
        pmim = upDownPowerMix['power_mix'][:, :, t]

        # Remove self import/export from up/down stream approach
        for n in range(nodes):
            if phi[n, t] > 0:
                pmim[n, n] = 0
            if phi[n, t] < 0:
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
            if round(phi[order[n], t], 4) == 0:
                newNames[n] = names[n]
                for i in range(len(fractions)):
                    corr[n, i] = 0
            if round(phi[order[n], t], 4) > 0:
                newNames[n] = '+ ' + names[n]
                for i in range(len(fractions)):
                    corr[n, i] = pearsonr(pmex[order[n]], powerMix[i, :, order[n]])[0]
            if round(phi[order[n], t], 4) < 0:
                newNames[n] = '- ' + names[n]
                for i in range(len(fractions)):
                    corr[n, i] = pearsonr(pmim[order[n]], powerMix[i, order[n], :])[0]
        plt.figure()
        ax = plt.subplot()
        plt.pcolormesh(corr)
        plt.colorbar()
        ax.set_xticks(np.linspace(.5, 9.5, 10))
        ax.set_xticklabels(np.linspace(.1, 1, 10))
        ax.set_yticks(np.linspace(.5, 29.5, 30))
        ax.set_yticklabels(newNames, ha="right", va="center", fontsize=8)
        plt.xlabel('fraction')
        plt.savefig('./figures/fraction correlation/t_' + str(t) + title + '.png', bbox_inches='tight')
        plt.close()

if 'avg' in task:
    try:
        hours = int(sys.argv[2])
    except ValueError:
        raise ValueError('Input number of hours to include as second command line argument')
    importCorr = np.zeros((nodes, len(fractions)))
    exportCorr = np.zeros((nodes, len(fractions)))
    phi = np.load('./data/phi.npy')
    upDownPowerMix = np.load('./input/linear_pm.npz', mmap_mode='r')
    timeSteps = range(hours)
    for t in timeSteps:
        t = int(t)
        pmex = upDownPowerMix['power_mix_ex'][:, :, t]
        pmim = upDownPowerMix['power_mix'][:, :, t]

        # Remove self import/export from up/down stream approach
        for n in range(nodes):
            if phi[n, t] > 0:
                pmim[n, n] = 0
            if phi[n, t] < 0:
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
            if round(phi[order[n], t], 4) == 0: continue
            if round(phi[order[n], t], 4) > 0:
                for i in range(len(fractions)):
                    exportCorr[n, i] += pearsonr(pmex[order[n]], powerMix[i, :, order[n]])[0]
            if round(phi[order[n], t], 4) < 0:
                for i in range(len(fractions)):
                    importCorr[n, i] += pearsonr(pmim[order[n]], powerMix[i, order[n], :])[0]

    # average correlations for each fraction over all time steps
    exportCorr = exportCorr / len(timeSteps)
    importCorr = importCorr / len(timeSteps)

    # plot import and export side by side and sort in 3 different ways
    titles = ['', '-load', '-degree']
    orders = [range(30), loadOrder, degreeOrder]
    nameList = [names, loadNames, degreeNames]
    norm = mpl.colors.Normalize(vmin=0, vmax=1)
    for m in range(3):
        title = titles[m]
        order = orders[m]
        names = nameList[m]

        plt.figure(figsize=(12, 6))
        ax = plt.subplot(121)
        plt.pcolormesh(exportCorr[order], norm=norm)
        plt.colorbar()
        ax.set_xticks(np.linspace(.5, 9.5, 10))
        ax.set_xticklabels(np.linspace(.1, 1, 10))
        ax.set_yticks(np.linspace(.5, 29.5, 30))
        ax.set_yticklabels(names, ha="right", va="center", fontsize=8)
        plt.xlabel('fraction')
        plt.title('Export color mix')

        ax = plt.subplot(122)
        plt.pcolormesh(importCorr[order], norm=norm)
        plt.colorbar()
        ax.set_xticks(np.linspace(.5, 9.5, 10))
        ax.set_xticklabels(np.linspace(.1, 1, 10))
        ax.set_yticks(np.linspace(.5, 29.5, 30))
        ax.set_yticklabels(names, ha="right", va="center", fontsize=8)
        plt.xlabel('fraction')
        plt.title('Import color mix')
        plt.savefig('./figures/avg/power_mix_correlation-' + str(len(timeSteps)) + title + '.png', bbox_inches='tight')

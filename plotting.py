from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
from functions import norm

"""
Plotting comparison of diffusive flow and up/down stream approach
"""

names = ['AT', 'FI', 'NL', 'BA', 'FR', 'NO', 'BE', 'GB', 'PL', 'BG', 'GR',
         'PT', 'CH', 'HR', 'RO', 'CZ', 'HU', 'RS', 'DE', 'IE', 'SE', 'DK',
         'IT', 'SI', 'ES', 'LU', 'SK', 'EE', 'LV', 'LT']

linkNames = ['AT-CH', 'AT-CZ', 'AT-HU', 'AT-DE', 'AT-IT', 'AT-SI', 'FI-SE',
             'FI-EE', 'NL-NO', 'NL-BE', 'NL-GB', 'NL-DE', 'BA-HR', 'BA-RS',
             'FR-BE', 'FR-GB', 'FR-CH', 'FR-DE', 'FR-IT', 'FR-ES', 'NO-SE',
             'NO-DK', 'GB-IE', 'PL-CZ', 'PL-DE', 'PL-SE', 'PL-SK', 'BG-GR',
             'BG-RO', 'BG-RS', 'GR-IT', 'PT-ES', 'CH-DE', 'CH-IT', 'HR-HU',
             'HR-RS', 'HR-SI', 'RO-HU', 'RO-RS', 'CZ-DE', 'CZ-SK', 'HU-RS',
             'HU-SK', 'DE-SE', 'DE-DK', 'DE-LU', 'SE-DK', 'IT-SI', 'EE-LV',
             'LV-LT']

shift = .3
width = .5


def plotNodes(t=100, consistency=False):
    """
    Function that plots nodes' power mixes to compare diffusive flow to up/down
    stream approach.
    """
    phi = np.load('./data/phi.npy')
    pmim = np.load('./results/power_mix_node_import_100.npy')
    pmex = np.load('./results/power_mix_node_export_100.npy')
    dpm = np.load('./results/dpm_export.npy')
    np.fill_diagonal(dpm, 0)
    nodes = pmim.shape[0]

    for n in range(nodes):
        if phi[n, t] > 0:
            pmim[n, n] = 0
            if consistency: print ' +  , ', sum(dpm[:, n]) - phi[n, t]
        if phi[n, t] < 0:
            pmex[n, n] = 0
            if consistency: print '- , ', sum(dpm[n, :]) + phi[n, t]

        plt.figure(figsize=(13, 6))
        plt.subplot(1, 2, 1)
        plt.bar(range(nodes), dpm[n, :], width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(shift, nodes + shift, 1), pmim[n, :], width, edgecolor='none', color='LightSteelBlue')
        plt.xticks(np.arange((width + shift) * .5, nodes + (width + shift) * .5, 1), names, rotation=75, fontsize=10)
        plt.legend(('Diffusive flow', 'Up/down stream'), loc='best')
        plt.title('Import', fontsize=12)
        plt.ylabel('MW')
        plt.ylim(ymin=0)

        plt.subplot(1, 2, 2)
        plt.bar(range(nodes), dpm[:, n], width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(shift, nodes + shift, 1), pmex[n, :], width, edgecolor='none', color='LightSteelBlue')
        plt.xticks(np.arange((width + shift) * .5, nodes + (width + shift) * .5, 1), names, rotation=75, fontsize=10)
        plt.legend(('Diffusive flow', 'Up/down stream'), loc='best')
        plt.title('Export', fontsize=12)
        plt.ylabel('MW')
        plt.ylim(ymin=0)

        plt.suptitle(names[n] + " (" + str(int(round(phi[n, t]))) + "), t = " + str(t), fontsize=14)
        plt.savefig('./figures/nodes/' + str(n) + '.png', bbox_inches='tight')


def plotLinks():
    LinkExport = np.load('./input/link_export_100_linear.npy')
    LinkImport = np.load('./input/link_import_100_linear.npy')
    linkFlowEx = np.load('./results/linkFlow_export.npy')
    linkFlowIm = np.load('./results/linkFlow_import.npy')
    linkFlowEx = np.sum(linkFlowEx, 0)
    linkFlowIm = np.sum(linkFlowIm, 0)
    nodes = linkFlowEx.shape[1]
    for l in range(len(LinkExport)):
        plt.figure(figsize=(13, 6))
        plt.subplot(1, 2, 1)
        b = plt.bar(np.arange(0, nodes), linkFlowEx[l, :], width, edgecolor='none', color='SteelBlue')
        c = plt.bar(np.arange(shift, nodes + shift, 1), LinkExport[l, :], width, edgecolor='none', color='LightSteelBlue')
        plt.title(linkNames[l] + ' export flow')
        plt.ylabel('MW')
        plt.grid(True)
        plt.xticks(np.arange((width + shift) * .5, nodes + (width + shift) * .5, 1), names, rotation=75, fontsize=10)
        plt.legend((b, c), ('Diffusive flow', 'Up/down stream'), loc='best')

        plt.subplot(1, 2, 2)
        b = plt.bar(np.arange(0, nodes), linkFlowIm[l, :], width, edgecolor='none', color='SteelBlue')
        c = plt.bar(np.arange(shift, nodes + shift, 1), LinkImport[l, :], width, edgecolor='none', color='LightSteelBlue')
        plt.title(linkNames[l] + ' import flow')
        plt.ylabel('MW')
        plt.grid(True)
        plt.xticks(np.arange((width + shift) * .5, nodes + (width + shift) * .5, 1), names, rotation=75, fontsize=10)
        plt.legend((b, c), ('Diffusive flow', 'Up/down stream'), loc='best')

        plt.savefig('./figures/links/' + str(l) + '.png', bbox_inches='tight')


def plotUsage(t=100, consistency=False):
    phi = np.load('./data/phi.npy')
    LinkExport = np.load('./input/link_export_100_linear.npy')
    LinkImport = np.load('./input/link_import_100_linear.npy')
    linkFlowEx = np.load('./results/linkFlow_export.npy')
    linkFlowIm = np.load('./results/linkFlow_import.npy')
    linkFlowEx = np.sum(linkFlowEx, 0)
    linkFlowIm = np.sum(linkFlowIm, 0)
    nodes = linkFlowEx.shape[1]

    for n in range(nodes):
        if consistency:
            if phi[n, t] < 0:
                print '- , ', sum(np.abs(linkFlowIm[:, n])) / sum(LinkImport[:, n])
            if phi[n, t] > 0:
                print ' +  , ', sum(np.abs(linkFlowEx[:, n])) / sum(LinkExport[:, n])

        plt.figure(figsize=(11, 8))
        plt.subplot(2, 1, 1)
        plt.bar(range(0, 50), np.abs(linkFlowIm[:, n]), width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(shift, 50 + shift, 1), LinkImport[:, n], width, edgecolor='none', color='LightSteelBlue')
        plt.ylabel('import [MW]')
        plt.grid(True)
        plt.xticks(np.arange((width + shift) * .5, 50 + (width + shift) * .5, 1), linkNames, rotation=90, fontsize=10)
        plt.xlim(xmin=0, xmax=50)
        plt.ylim(ymin=0)
        plt.legend(('Diffusive flow', 'Up- down stream'), loc='best')

        plt.subplot(2, 1, 2)
        plt.bar(range(0, 50), np.abs(linkFlowEx[:, n]), width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(shift, 50 + shift, 1), LinkExport[:, n], width, edgecolor='none', color='LightSteelBlue')
        plt.ylabel('export [MW]')
        plt.grid(True)
        plt.ylim(ymin=0)
        plt.xticks(np.arange((width + shift) * .5, 50 + (width + shift) * .5, 1), linkNames, rotation=90, fontsize=10)

        plt.suptitle(names[n] + " (" + str(int(round(phi[n, t]))) + "), t = " + str(t), fontsize=14)
        plt.savefig('./figures/usage/' + str(n) + '.png', bbox_inches='tight')

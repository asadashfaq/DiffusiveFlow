from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

"""
Plotting comparison of diffusive flow and up/down stream approach
"""

names = ['AT', 'FI', 'NL', 'BA', 'FR', 'NO', 'BE', 'GB', 'PL', 'BG', 'GR',\
         'PT', 'CH', 'HR', 'RO', 'CZ', 'HU', 'RS', 'DE', 'IE', 'SE', 'DK',\
         'IT', 'SI', 'ES', 'LU', 'SK', 'EE', 'LV', 'LT']

phi = np.load('./data/phi.npy')
pm = np.load('./results/power_mix_node_import_100.npy')
dpm = np.load('./results/dpm.npy')
np.fill_diagonal(dpm,0)

nodes = pm.shape[0]
shift = .3
width = .5

def plotNodes(t=100):
    """
    Function that plots nodes' power mixes to compare diffusive flow to up/down
    stream approach.
    """
    for n in range(nodes):
        plt.figure(figsize=(14,7))
        plt.subplot(1,2,1)
        plt.bar(range(nodes), dpm[n,:], width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(shift,nodes+shift,1), pm[n,:], width, edgecolor='none', color='LightSteelBlue')
        plt.xticks(np.arange((width+shift)*.5,nodes+(width+shift)*.5,1), names, rotation=75, fontsize=10)
        plt.legend(('Diffusive flow','Up- down stream'), loc='best')
        plt.title('Import', fontsize=12)
        plt.ylabel('MW')
        plt.ylim(ymin=0)

        plt.subplot(1,2,2)
        plt.bar(range(nodes), dpm[:,n], width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(shift,nodes+shift,1), pm[:,n], width, edgecolor='none', color='LightSteelBlue')
        plt.xticks(np.arange((width+shift)*.5,nodes+(width+shift)*.5,1), names, rotation=75, fontsize=10)
        plt.legend(('Diffusive flow','Up- down stream'), loc='best')
        plt.title('Export', fontsize=12)
        plt.ylabel('MW')
        plt.ylim(ymin=0)

        plt.suptitle(names[n] + " (" + str(int(round(phi[n,t]))) + "), t = "+str(t), fontsize=14)

        plt.savefig('./figures/nodes/'+str(n)+'.png', bbox_inches='tight')

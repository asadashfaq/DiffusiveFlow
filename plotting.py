from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

"""
Plotting comparison of diffusive flow and up/down stream approach
"""

pm = np.load('./results/power_mix_node_import_100.npy')
dpm = np.load('./results/dpm.npy')

nodes = pm.shape[0]
shift = .3
width = .5

plt.figure()
plt.subplot(1,2,1)
plt.bar(range(nodes), dpm[0,:], width, edgecolor='none', color='SteelBlue')
plt.bar(np.arange(shift,nodes+shift,1), pm[0,:], width, edgecolor='none', color='LightSteelBlue')
plt.xticks(np.arange((width+shift)*.5,nodes+(width+shift)*.5,1), ('0AT', '1FI', '2NL', '3BA', '4FR', '5NO','6BE', '7GB', '8PL', '9BG', '10GR','11PT', '12CH', '13HR', '14RO', '15CZ','16HU', '17RS', '18DE', '19IE', '20SE','21DK', '22IT', '23SI', '24ES', '25LU','26SK', '27EE', '28LV', '29LT'),rotation=75 )

plt.subplot(1,2,2)
plt.bar(range(nodes), dpm[:,0], width, edgecolor='none', color='SteelBlue')
plt.bar(np.arange(shift,nodes+shift,1), pm[:,0], width, edgecolor='none', color='LightSteelBlue')
plt.xticks(np.arange((width+shift)*.5,nodes+(width+shift)*.5,1), ('0AT', '1FI', '2NL', '3BA', '4FR', '5NO','6BE', '7GB', '8PL', '9BG', '10GR','11PT', '12CH', '13HR', '14RO', '15CZ','16HU', '17RS', '18DE', '19IE', '20SE','21DK', '22IT', '23SI', '24ES', '25LU','26SK', '27EE', '28LV', '29LT'),rotation=75 )

plt.show()

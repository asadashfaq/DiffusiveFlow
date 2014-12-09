# -*- coding: utf-8 -*-
"""
Created on Thu Nov 20 12:37:30 2014

@author: Jacob Bjerre
"""
import numpy as np
import matplotlib.pyplot as plt

plt.close("all")
plt.ioff()

PlotNodeImportExport = False
PLotLinkImportExport = False
PlotTotalLinkUsage   = False
PlotEachLinkTraffic  = True


NodeDist          = np.load('NodeDist.npy')
NodeDistImport    = np.load('NodeDistimport.npy')
LinkDist          = np.load('LinkDist.npy')
LinkDistImport    = np.load('LinkDistimport.npy')

LinkDistImport100 = np.load('link_import_100.npy')
LinkDistExport100 = np.load('link_export_100.npy')
NodeDistExport100 = np.load('power_mix_node_export_100.npy')
NodeDistImport100 = np.load('power_mix_node_import_100.npy')
F                 = np.load('F.npy')

Phiload           = np.load('phi.npy')
LoadSerie=100
Phi = np.round(Phiload[:,LoadSerie],2)
Nodes=30
Links=50
ind = np.arange(Nodes)
indlinks = np.arange(Links)
width = 0.4
displace=0.3
lande=('Austria', 'Finland', 'Netherland', 'Bosnia and Herzegovina', 'France', 'Norway','Belgium', 'Great Britain', 'Poland', 'Bulgaria', 'Greece','Portugal', 'Swiss', 'Croatia', 'Romania', 'Czech','Hungary', 'Serbia', 'Germany', 'Ireland', 'Sweden','Denmark', 'Italy', 'Slovenia', 'Spain', 'Luxembourg','Slovakia', 'Estonia', 'Latvia', 'Lithuania')
Linkname=('0 AT-CH','1 AT-CZ','2 AT-HU','3 AT-DE','4 AT-IT','5 AT-SI','6 FI-SE','7 FI-EE','8 NL-NO','9 NL-BE','10 NL-GB','11 NL-DE','12 BA-HR','13 BA-RS','14 FR-BE',' 15 FR-GB',' 16 FR-CH',' 17 FR-DE',' 18 FR-IT','19 FR-ES',' 20 NO-SE',' 21 NO-DK',' 22 GB-IE',' 23 PL-CZ',' 24 PL-DE',' 25 PL-SE',' 26 PL-SK',' 27 BG-GR',' 28 BG-RO',' 29 BG-RS',' 30 GR-IT',' 31 PT-ES',' 32 CH-DE',' 33 CH-IT',' 34 HR-HU',' 35 HR-RS',' 36 HR-SI',' 37 RO-HU','38 RO-RS',' 39 CZ-DE','40 CZ-SK',' 41 HU-RS',' 42 HU-SK',' 43 DE-SE',' 44 DE-DK',' 45 DE-LU',' 46 SE-DK',' 47 IT-SI',' 48 EE-LV',' 49 LV-LT')

if PlotNodeImportExport:
    for i in range(0,Nodes):
        if Phi[i] > 0:
            NodeDistExport100[i,:]=NodeDistExport100[i,:]*(1-(sum(NodeDistImport100[i,:])-NodeDistImport100[i,i])/sum(NodeDistImport100[i,:]))
            LinkDistExport100[:,i]=LinkDistExport100[:,i]*(1-(sum(NodeDistImport100[i,:])-NodeDistImport100[i,i])/sum(NodeDistImport100[i,:]))
            NodeDistImport100[i,:]=0
        if Phi[i] < 0:
            NodeDistImport100[i,:]=NodeDistImport100[i,:]*(1-(sum(NodeDistExport100[i,:])-NodeDistExport100[i,i])/sum(NodeDistExport100[i,:]))
            LinkDistImport100[:,i]=LinkDistImport100[:,i]*(1-(sum(NodeDistExport100[i,:])-NodeDistExport100[i,i])/sum(NodeDistExport100[i,:]))
            NodeDistExport100[i,:]=0        

    for a in range(0,Nodes):
        plt.figure(figsize=(19,8))
        plt.subplot(1,2,1)
        plt.bar(range(0,Nodes),NodeDist[:,a],width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(displace,Nodes+displace,1),NodeDistImport100[a,:],width, edgecolor='none', color='LightSteelBlue')    
        plt.title(lande[a]+' import. (IP='+str(Phi[a])+')')
        plt.ylabel('MW')
        plt.xticks(ind+width/2., ('0AT', '1FI', '2NL', '3BA', '4FR', '5NO','6BE', '7GB', '8PL', '9BG', '10GR','11PT', '12CH', '13HR', '14RO', '15CZ','16HU', '17RS', '18DE', '19IE', '20SE','21DK', '22IT', '23SI', '24ES', '25LU','26SK', '27EE', '28LV', '29LT'),rotation=75 )
        plt.grid(True)
        plt.ylim(ymin=1)  

        plt.subplot(1,2,2)
        plt.bar(range(0,Nodes),NodeDist[a,:],width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(displace,Nodes+displace,1),NodeDistExport100[a,:],width, edgecolor='none', color='LightSteelBlue')    
        plt.title(lande[a]+' export. (IP='+str(Phi[a])+')')
        plt.ylabel('MW')
        plt.xticks(ind+width/2., ('0AT', '1FI', '2NL', '3BA', '4FR', '5NO','6BE', '7GB', '8PL', '9BG', '10GR','11PT', '12CH', '13HR', '14RO', '15CZ','16HU', '17RS', '18DE', '19IE', '20SE','21DK', '22IT', '23SI', '24ES', '25LU','26SK', '27EE', '28LV', '29LT'),rotation=75 )
        plt.grid(True)
        plt.legend(('Diffusive flow','Up- down stream'), loc='best')
        plt.ylim(ymin=1)
    
        plt.savefig('./figures/nodes/'+lande[a]+'.png')
    
#------LINKS PLOTTING --------------------------------------------------------
if PLotLinkImportExport:
    a=0     
    for a in range(0,Nodes):
        plt.figure(figsize=(19,10))
        plt.subplot(2,1,1)
        plt.bar(range(0,Links),np.abs(LinkDistImport[a,:]),width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(displace,Links+displace,1),LinkDistImport100[:,a],width, edgecolor='none', color='LightSteelBlue')    
        plt.title(lande[a]+' import from links.')
        plt.ylabel('MW')
        plt.grid(True)
        #plt.ylim(ymin=1)  
        plt.xlim(xmin=0, xmax=50)    
        plt.legend(('Diffusive flow','Up- down stream'), loc='best')
        
        plt.subplot(2,1,2)
        plt.bar(range(0,Links),np.abs(LinkDist[a,:]),width, edgecolor='none', color='SteelBlue')
        plt.bar(np.arange(displace,Links+displace,1),LinkDistExport100[:,a],width, edgecolor='none', color='LightSteelBlue')    
        plt.title(lande[a]+' export to links.') 
        plt.ylabel('MW')
        plt.xticks(indlinks+width/2.,('0 AT-CH','1 AT-CZ','2 AT-HU','3 AT-DE','4 AT-IT','5 AT-SI','6 FI-SE','7 FI-EE','8 NL-NO','9 NL-BE','10 NL-GB','11 NL-DE','12 BA-HR','13 BA-RS','14 FR-BE',' 15 FR-GB',' 16 FR-CH',' 17 FR-DE',' 18 FR-IT','19 FR-ES',' 20 NO-SE',' 21 NO-DK',' 22 GB-IE',' 23 PL-CZ',' 24 PL-DE',' 25 PL-SE',' 26 PL-SK',' 27 BG-GR',' 28 BG-RO',' 29 BG-RS',' 30 GR-IT',' 31 PT-ES',' 32 CH-DE',' 33 CH-IT',' 34 HR-HU',' 35 HR-RS',' 36 HR-SI',' 37 RO-HU','38 RO-RS',' 39 CZ-DE','40 CZ-SK',' 41 HU-RS',' 42 HU-SK',' 43 DE-SE',' 44 DE-DK',' 45 DE-LU',' 46 SE-DK',' 47 IT-SI',' 48 EE-LV',' 49 LV-LT'),rotation=90, fontsize=10 )
        plt.grid(True)
        #plt.ylim(ymin=1) 
    
        plt.savefig('./figures/links/'+lande[a]+'.png')
    
#---- Total Link Usage ------------
if PlotTotalLinkUsage:
    plt.figure()
    plt.bar(np.arange(0,Links),F[:,LoadSerie],width, edgecolor='none', color='LightSteelBlue')
    plt.bar(np.arange(displace,Links+displace,1),sum(LinkDist[:,:],axis=0),width, edgecolor='none', color='SteelBlue')
    plt.title('Total link Usage')
    plt.ylabel('MW')
    plt.xticks(indlinks+width/2.,('0 AT-CH','1 AT-CZ','2 AT-HU','3 AT-DE','4 AT-IT','5 AT-SI','6 FI-SE','7 FI-EE','8 NL-NO','9 NL-BE','10 NL-GB','11 NL-DE','12 BA-HR','13 BA-RS','14 FR-BE',' 15 FR-GB',' 16 FR-CH',' 17 FR-DE',' 18 FR-IT','19 FR-ES',' 20 NO-SE',' 21 NO-DK',' 22 GB-IE',' 23 PL-CZ',' 24 PL-DE',' 25 PL-SE',' 26 PL-SK',' 27 BG-GR',' 28 BG-RO',' 29 BG-RS',' 30 GR-IT',' 31 PT-ES',' 32 CH-DE',' 33 CH-IT',' 34 HR-HU',' 35 HR-RS',' 36 HR-SI',' 37 RO-HU','38 RO-RS',' 39 CZ-DE','40 CZ-SK',' 41 HU-RS',' 42 HU-SK',' 43 DE-SE',' 44 DE-DK',' 45 DE-LU',' 46 SE-DK',' 47 IT-SI',' 48 EE-LV',' 49 LV-LT'),rotation=75 , fontsize=10  )
    plt.grid(True)
    plt.legend(('Diffusive flow','Up- down stream'), loc='best')
    plt.savefig('./figures/Total_Link_usage.png')
#----------------------------------

if PlotEachLinkTraffic:
    a=0     
    for a in range(0,Links):
        plt.figure()
        b=plt.bar(np.arange(0,Nodes),np.abs(LinkDist[:,a]),width, edgecolor='none', color='SteelBlue')
        c=plt.bar(np.arange(displace,Nodes+displace,1),LinkDistExport100[a,:],width, edgecolor='none', color='LightSteelBlue')
        #b=plt.bar(np.arange(0,Nodes),np.abs(LinkDistImport[:,a]),width, edgecolor='none', color='SteelBlue')
        #c=plt.bar(np.arange(displace,Nodes+displace,1),LinkDistImport100[a,:],width, edgecolor='none', color='LightSteelBlue')        
        plt.title(Linkname[a]+' link tranport')
        plt.ylabel('MW')
        plt.xticks(ind+width/2., ('0AT', '1FI', '2NL', '3BA', '4FR', '5NO','6BE', '7GB', '8PL', '9BG', '10GR','11PT', '12CH', '13HR', '14RO', '15CZ','16HU', '17RS', '18DE', '19IE', '20SE','21DK', '22IT', '23SI', '24ES', '25LU','26SK', '27EE', '28LV', '29LT'),rotation=75 )
        plt.legend((b,c),('Diffusive flow', 'Up- down stream'), loc='best')        
        plt.grid(True)
    
        plt.savefig('./figures/each_link/'+str(a)+'.png')

plt.close("all")

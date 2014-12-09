# -*- coding: utf-8 -*-
"""
Created on Sun Nov 09 16:07:01 2014

@author: Jacob Bjerre
"""
import time
import numpy as np
import matplotlib.pyplot as plt
import os
clear = lambda: os.system('cls')
clear()

plt.close("all")
start = time.time()
#Phi = np.matrix('-20.;-10.;10.;20.')
#K= np.matrix([[ 1, 0,  1, 0, 1],
 #             [-1, 1,  0, 0, 0],
 #             [ 0, 0, -1, 1, 0],
 #             [ 0,-1,  0,-1,-1],])
 
Phiload = np.load('./data/phi.npy')
K = np.load('./data/K.npy')
F = np.load('./data/F.npy')

LoadSerie=100   # Load serie (calculations done on 100)
NodeIm   =18    # Plotted Node Number for import 
NodeEx   =18    # Plotted Node Number for export
LinkUsage=18    # 
NodeIte  =1000  # Number of iterations.

Phi = Phiload[:,LoadSerie]
Links=len(K.T)
Nodes =len(K)
RoundSumPhi = round(sum(Phi),2)
print 'Sum of initial node Values: %d' %RoundSumPhi

NodeValue=np.zeros((Nodes,Nodes,NodeIte))       #work horse
NodeValueSave=np.zeros((Nodes,Nodes,NodeIte))   #for the archives
NodeValueSave2=np.zeros((Nodes,Nodes,NodeIte))  #overflow values

NodeInitial=0
for NodeInitial in range(0,Nodes): #Puts the injection pattern on the diagonal of the NodeValue matrix
    NodeValue[NodeInitial,NodeInitial,0]=Phi[NodeInitial]
    NodeValueSave[NodeInitial,NodeInitial,0]=Phi[NodeInitial]

LinkValuePos=np.zeros((Nodes,Links,NodeIte)) #store link values in positive direction 
LinkValueNeg=np.zeros((Nodes,Links,NodeIte)) #store link values in negative direction                       


PhiNeg=[i for i, j in enumerate(Phi) if j < 0] #array of row numbers with starting negative injection pattern

Lande=np.zeros((Nodes,2)) #to display node number and start injection pattern
Lande[:,0]=range(0,Nodes)
Lande[:,1]=Phi

iteration=0; PosNegLinkRun=0; noderun=0; linkrun=0; d=0; e=0
for iteration in range(0,NodeIte-1): #run for iterations
    for noderun in range(0,Nodes):  #run through all node
    
        if sum(NodeValue[:,noderun,iteration]) <= 0: #node is sink and ejects all        
            NodeValue[noderun,noderun,iteration+1] += np.sum(NodeValue[:,noderun,iteration])
            NodeValueSave[noderun,noderun,iteration+1] += np.sum(NodeValue[:,noderun,iteration])
            
        else:  #if the sum of a node is positive:
            if np.min(NodeValue[noderun,noderun,iteration]) < 0: 
            # if the average is larger than zero but it contains a negativ number 
            # - node is a sink, but there is going to be overflow           
                givefraction=   np.abs(NodeValue[noderun,noderun,iteration])/np.sum(NodeValue[:,noderun,iteration].clip(0))
                    #how much of each node that is ejected                
                injectfraction= 1-givefraction
                    #how much of each node that is injected again.
                
                NodeValueSave2[:,noderun,iteration]= NodeValueSave[:,noderun,iteration]*givefraction                
                    #to have the value of ejected
                NodeValueSave[:,noderun,iteration]= NodeValueSave[:,noderun,iteration]*injectfraction
                    #to save the value of injected
                
                NodeValue[:,noderun,iteration]=NodeValue[:,noderun,iteration]*injectfraction
                    #node values after ejection                
                NodeValueSave2[noderun,noderun,iteration]=0
                    #sink is full                  
                NodeValue[noderun,noderun,iteration]=     0                
                NodeValueSave[noderun,noderun,iteration]= 0
                
                NOL = abs(K[noderun,:]).sum()*1.                 #Number of links
                NewValue  = NodeValue[:,noderun,iteration]/NOL   #devide node value with number of links
                for PosNegLinkRun in range(0,Links):            
                    if K[noderun,PosNegLinkRun] > 0:
                        LinkValuePos[:,PosNegLinkRun,iteration]= LinkValuePos[:,PosNegLinkRun,iteration]+NewValue
                    if K[noderun,PosNegLinkRun] < 0:
                        LinkValueNeg[:,PosNegLinkRun,iteration]= LinkValueNeg[:,PosNegLinkRun,iteration]-NewValue
                              
                NodeValue[:,noderun,iteration]= 0
 
            else:
                NOL = abs(K[noderun,:]).sum()*1.                 #Number of links
                NewValue  = NodeValue[:,noderun,iteration]/NOL   #devide node value with number of links
                for PosNegLinkRun in range(0,Links):            
                    if K[noderun,PosNegLinkRun] == 1:
                        LinkValuePos[:,PosNegLinkRun,iteration]= LinkValuePos[:,PosNegLinkRun,iteration]+NewValue
                    if K[noderun,PosNegLinkRun] == -1:
                        LinkValueNeg[:,PosNegLinkRun,iteration]= LinkValueNeg[:,PosNegLinkRun,iteration]-NewValue
            
                NodeValueSave[:,noderun,iteration]= NodeValue[:,noderun,iteration]            
                NodeValue[:,noderun,iteration] = 0.
                    #node values saved and removed                      
                    
    for linkrun in range(0,Links): #Inject what is on the links to the right node.
        for d in range(0,Nodes):
            if K[d,linkrun] == -1:
                NodeValue[:,d,iteration+1] += LinkValuePos[:,linkrun,iteration]
                NodeValueSave[:,d,iteration+1] += LinkValuePos[:,linkrun,iteration]
        for e in range(0,Nodes):
            if K[e,linkrun] == 1: 
                NodeValue[:,e,iteration+1] += abs(LinkValueNeg[:,linkrun,iteration])
                NodeValueSave[:,e,iteration+1] += abs(LinkValueNeg[:,linkrun,iteration])
   


NodeValue2D=np.zeros((Nodes,NodeIte))
LinkValue=np.zeros((Nodes,Links,NodeIte))


LinkValue[:,:,:] =LinkValuePos[:,:,:]+LinkValueNeg[:,:,:]

NodeDist=sum(NodeValue,axis=2)+sum(NodeValueSave2,axis=2) #NodeValueSave2 for overflow
LinkDist=sum(LinkValue,axis=2)

NodeValue2D=np.sum(NodeValueSave, axis=0)

LinkValue2D=np.sum(LinkValue, axis=0)
AcumSumLink= np.cumsum(LinkValue2D, axis=1)

takentime= np.round((time.time()-start)/NodeIte*1000,2)

a=0
for a in PhiNeg:
    NodeDist[a,a]= - np.max(NodeValueSave[a,a,:])
#print np.round(NodeDist,2)                 
Phitjek1=sum(NodeDist,axis=1)-Phi.T.clip(0)
Phitjek2=sum(NodeDist,axis=0)-np.abs(Phi.T.clip(-100000000000000,0))
Flowtjek= sum(LinkDist[:,:],axis=0) - F[:,LoadSerie]
print 'Final Injection pattern max value: %d' %np.max(np.abs(Phitjek1))
print 'Final calculated flow minus given flow: %d' %np.max(np.abs(Flowtjek))


#--------------- Saving matrices----------------------------------------------
np.save('./results/NodeDist', NodeDist)
np.save('./results/LinkDist', LinkDist)
np.save('./results/lande', Lande)

print 'It took', takentime, 'milliseconds per iteration.'


#---------------Plotting iterations-------------------------------------------

plt.figure()
m=0
plt.subplot(2,2,1)
for m in range(0,Links):
    plt.plot(range(0,NodeIte),AcumSumLink[m,:])
plt.ylabel('Link usage value')     
plt.grid(True)
plt.title('Accumulated link usage values')

plt.subplot(2, 2, 2)
for n in range(0,Nodes):
    plt.plot(range(0,NodeIte),NodeValue2D[n,:])
plt.ylabel('Node value') 
plt.grid(True)
plt.title('Node values as a function of iterations')        

m=0
plt.subplot(2,2,3)
for m in range(0,Links):
    plt.plot(range(0,NodeIte),LinkValue2D[m,:])
plt.xlabel('#iterations')
plt.ylabel('Link values')     
plt.grid(True)
plt.title('Link values')

m=0
plt.subplot(2,2,4)
for m in range(0,Nodes):
    plt.plot(range(0,NodeIte),np.sum(NodeValue2D, axis=0))
plt.xlabel('#iterations')
plt.ylabel('Sum of node Values')
plt.grid(True) 
plt.title('Sum of node values in each iteration')          

plt.subplots_adjust(wspace=.5,hspace=.3,top=.8,bottom=0)
plt.savefig('iteration_results.png',bbox_inches='tight')
#plt.show()
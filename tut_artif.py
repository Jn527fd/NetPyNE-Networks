"""
tut_artif.py 
Tutorial on artificial cells (no sections)
"""
from netpyne import specs, sim
from netpyne.specs import Dict
netParams = specs.NetParams()  # object of class NetParams to store the network parameters
simConfig = specs.SimConfig()  # dictionary to store sets of simulation configurations
simConfig.hParams['celsius'] = 37

###############################################################################
# NETWORK PARAMETERS
###############################################################################
# Population parameters
numCells = 1
connList = [[i,i] for i in range(numCells)]

#netParams.popParams['artif0'] = {'cellModel' : 'NetStim', 'numCells' : 1, 'rate' : 2000, 'noise' : 10} 

netParams.popParams['artif0'] = {'cellModel' : 'NetStim', 'numCells' : numCells, 'rate' : 'variable', 'noise' : 0} #, 'start' : 0, 'seed' : 2}

netParams.popParams['artif1'] = {'cellModel': 'INTF7', 'numCells': numCells} #'start': 0, 'seed': 2}  # pop of NetStims

useArtif = True # False

netParams.synMechParams['AMPA'] = {'mod': 'Exp2Syn', 'tau1': 0.05, 'tau2': 5.3, 'e': 0}  # excitatory synaptic mechanism

if useArtif:
  netParams.popParams['artif3'] = {'cellModel': 'INTF7', 'numCells': numCells} #, 'taue': 5.0, 'taui1':10,'taui2':20,'taum':50}  # pop of IntFire4
  simConfig.recordTraces = {'V_soma':{'var':'Vm'}}  # Dict with traces to record  
else:
  netParams.popParams['artif3'] = {'numCells': numCells, 'cellModel': 'Mainen'}
  #netParams.importCellParams(label='PYR_Mainen_rule', conds={'cellType': ['artif3']}, fileName='cells/mainen.py', cellName='PYR2')
  netParams.importCellParams(label='PYR_Mainen_rule', conds={'cellType': ['artif3']}, fileName='cells/mainen.py', cellName='PYR2')
  netParams.cellParams['PYR_Mainen_rule']['secs']['soma']['threshold'] = 0.0
  simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record

# Connections

netParams.connParams['artif0->artif1'] = {
    'preConds': {'pop': 'artif0'}, 'postConds': {'pop': 'artif1'},
    #'connList': connList,
    'weight': 20,
    'synMech': 'AMPA',                
    'delay': 'uniform(1,5)'}



k = 'artif1->artif3'
netParams.connParams[k] = {
    'preConds': {'pop': 'artif1'}, 'postConds': {'pop': 'artif3'},
    #'probability': 0.2,
    'connList': connList,
    'weight': 17,
    'synMech': 'AMPA',                
    'delay': 'uniform(1,5)',
    'weightIndex': 0}

netParams.connParams[k]['plast'] = {'mech': 'STDP', 'params': {'RLon':1,'RLlenhebb':200,'RLhebbwt':0.001,'RLwindhebb':50,'wbase':0,'wmax':20}}

J = 'artif3->artif1'
netParams.connParams[J] = {
    'preConds': {'pop': 'artif3'}, 'postConds': {'pop': 'artif1'},
    #'probability': 0.2,
    'connList': connList,
    'weight': 18,
    'synMech': 'AMPA',                
    'delay': 'uniform(1,5)',
    'weightIndex': 0}

netParams.connParams[J]['plast'] = {'mech': 'STDP', 'params': {'RLon':1,'RLlenhebb':200,'RLhebbwt':0.001,'RLwindhebb':50,'wbase':0,'wmax':20}}

lsynweights = []
artif3_artif1weights = []
artif1_artif3weights = []
#timearr = []


def recordAdjustableWeights (sim, t):
  # record the plastic weights for specified popname
  #lcell = [c for c in sim.net.cells if c.gid in sim.net.pops[popname].cellGids] # this is the set of MR cells
  for cell in sim.net.cells:
    for conn in cell.conns:
      if 'hSTDP' in conn: 
      	lsynweights.append([t,conn.label,float(conn['hObj'].weight[0])])
      	if conn.label == 'artif3->artif1':
      		artif3_artif1weights.append([t,float(conn['hObj'].weight[0])])
      	if conn.label == 'artif1->artif3': 
      		artif1_artif3weights.append([t,float(conn['hObj'].weight[0])])
      	 
       

###############################################################################
# SIMULATION PARAMETER
###############################################################################
# Simulation parameters
simConfig.duration = 2.8*1e3 # Duration of the simulation, in ms
simConfig.dt = 0.1 # Internal integration timestep to use
simConfig.createNEURONObj = 1  # create HOC objects when instantiating network
simConfig.createPyStruct = 1  # create Python structure (simulator-independent) when instantiating network
simConfig.verbose = 1 #False  # show detailed messages 
# Recording 
# # Analysis and plotting 
simConfig.recordCells = ['all']
simConfig.filename = 'tut_output'
simConfig.analysis['plotRaster'] = {'saveFig' : True}
simConfig.analysis['plotTraces'] = {'saveFig': True}
simConfig.analysis['plot2Dnet'] = {'saveFig' : True}

sim.create(netParams, simConfig)

lcell = [c for c in sim.net.cells if c.gid in sim.net.pops['artif0'].cellGids]
for cell in lcell: cell.hPointp.interval = 5


#lSTDPmech = []
#for cell in sim.net.cells:
  #for conn in cell.conns:
    #STDPmech = conn.get('hSTDP')  # check if the connection has a NEURON STDP mechanism object
    #if STDPmech: lSTDPmech.append(STDPmech)


###############################################################################
# RUN SIM
###############################################################################

def mycallback (t):
  print('mycallback',t)
  #for stdpmech in lSTDPmech: stdpmech.reward_punish(0.0)
  recordAdjustableWeights(sim,t)

def insertSpikes (sim, spkht=50):
    sampr = 1e3 / simConfig.dt
    import pandas as pd
    import numpy as np
    spkt, spkid = sim.simData['spkt'], sim.simData['spkid']
    spk = pd.DataFrame(np.array([spkid, spkt]).T,columns=['spkid','spkt'])
    for kvolt in sim.simData['V_soma'].keys():
        cellID = int(kvolt.split('_')[1])
        spkts = spk[spk.spkid == cellID]
        if len(spkts):
            for idx in spkts.index:
                tdx = int(spk.at[idx, 'spkt'] * sampr / 1e3)
                sim.simData['V_soma'][kvolt][tdx] = spkht

#lcell3 = [c for c in sim.net.cells if c.gid in sim.net.pops['artif3'].cellGids]
#c = lcell3[0]
  
#sim.run.runSim()
sim.runSimWithIntervalFunc(1,mycallback)
for cell in sim.net.cells:
  for conn in cell.conns:
   STDPmech = conn.get('hSTDP')
   print(STDPmech)
   print(conn)

insertSpikes(sim)

sim.gatherData()

sim.analysis.plotData()
print(sim.simData)
print(len(artif3_artif1weights))
print(len(artif1_artif3weights))
t1, artif3_artif1 = map(list, zip(*artif3_artif1weights))

t2, artif1_artif3 = map(list, zip(*artif1_artif3weights))
 
print(len(t1))
print(len(t2))



#print(len(artif3_artif1))

#print(lsynweights)

#print(t1)

import matplotlib.pyplot as plt 
fig, axes = plt.subplots(3,figsize = (40,20))
axes[0].plot(sim.simData['t'],sim.simData['V_soma']['cell_1'], label = "artif1")
axes[0].plot(sim.simData['t'],sim.simData['V_soma']['cell_2'], label = "artif3")
axes[0].legend()
axes[0].set_title('V_soma vs time')
axes[0].set_xlabel('Times(ms)')	
axes[0].set_ylabel('V_soma')
axes[1].plot(sim.simData['spkt'],sim.simData['spkid'])
axes[1].set_title('spkid vs time')
axes[1].set_xlabel('Times(ms)')	
axes[1].set_ylabel('spkid')
axes[2].plot(t1, artif3_artif1, label = 'artif3->artif1')
axes[2].plot(t2, artif1_artif3, label = 'artif1->aritf3')
axes[2].legend()
axes[2].set_title('weights vs time')
axes[2].set_ylabel('weight')
axes[2].set_xlabel('Times(ms)')	
plt.savefig('tut_artif.png', transparent = False )



"""
#sim.createSimulateAnalyze()
sim.create(netParams, simConfig) 
sim.gatherData() # gather data from different nodes
sim.analysis.plotData()    

"""


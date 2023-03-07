from netpyne import specs, sim
netParams = specs.NetParams()
simConfig = specs.SimConfig()
simConfig.hParams['celsius'] = 37

###############################################################################
# NETWORK PARAMETERS
###############################################################################

numCells = 1
connList = [[i,i] for i in range(numCells)]

#netParams.importCellParams(label = '')

netParams.popParams['A'] = {'cellModel': 'INTF7', 'numCells' : numCells}

netParams.popParams['B'] = {'cellModel' : 'INTF7', 'numCells' : numCells}

#netParams.popParams['background'] = {'cellmodel' : 'NetStim', 'numCells': numCells, 'rate' : #5, 'noise': 0.5}

netParams.popParams['stim'] = {'cellModel' : 'NetStim', 'numCells' : numCells, 'rate' : 'variable', 'noise' : 200}

netParams.synMechParams['AMPA'] = {'mod' : 'Exp2Syn', 'tau1' : 0.05, 'tau2' : 5.3, 'e' : 2}
netParams.synMechParams['NMDA'] = {'mod' : 'Exp2Syn', 'tau1' : 0.15, 'tau2' : 1.50, 'e' : 0}

#netParams.stimSourceParams['NetStim'] = {
	#'type' : 'NetStim',
	#'rate'  : 50,
	#'noise'  : 10	
#}

#netParams.connParams['background->A,B'] = {
#	'preConds' : {'pop' : 'background'},
#	'postConds' : {'pop' : ['A','B']},
#	'weight'    : 0.05,
#	'delay'     : 'uniform(1,5)',
#	'synMech'   : 'NMDA'
#}

netParams.connParams['stim->A'] = {
	'preConds'   : {'pop' : 'stim'},
	'postConds'  : {'pop' : 'A'},
	#'connList'  : connList, 
	'weight'     : 20,
	'delay'      : 'uniform(1,5)',
	'synMech'    : 'NMDA',
	'weightIndex': 0}



netParams.connParams['A->B'] = {
	'preConds'   : {'pop' : 'A'},
	'postConds'  : {'pop' : 'B'},
	'probability': 1, 
	#'connList'  : connList, 
	'weight'     : 	20.72,
	#'probability': .2125,
	'delay'      : 5,
	'synMech'    : 'AMPA'}

netParams.connParams['A->B']['plast'] = {'mech' : 'STDP', 'params' : {'RLon' : 1, 'RLlenhebb' : 200, 'Rlhebbwt':0.001, 'Rlwindhebb' : 50, 'wbase': 0, 'wmax': 2}}

netParams.connParams['B->A'] = { 
	'preConds'   : {'pop' : 'B'},
	'postConds'  : {'pop' : 'A'},
	#'connList'  : connList, 
	'weight'     : 1.640,
	#'probability': 1.33750,
	'delay'      : 5,
	'synMech'    : 'AMPA'}
	
netParams.connParams['B->A']['plast'] = {'mech' : 'STDP', 'params' : {'RLon' : 1, 'RLlenhebb' : 20, 'Rlhebbwt':0.01, 'Rlwindhebb' : 50, 'wbase': 0, 'wmax': 2}}



lsynweights = []
INTF7cells = []

def recordAdjustableWeights (sim, t):
  for cell in sim.net.cells:
    print(cell)
    for conn in cell.conns:
       print(conn)
       if conn.label == "A->B" or conn.label == "B->A":
       	lsynweights.append([t,conn.preGid,float(conn['hObj'].weight[0])])

				
###############################################################################
# SIMULATION PARAMETERS
###############################################################################

simConfig.duration = 1*1e3
simConfig.dt = 0.1
simConfig.createNEURONObj = 1
simConfig.createPyStruct = 1
simConfig.verbose = False
simConfig.recordCells = ['all']

#simConfig.recordTraces['soma_voltage'] = {'V_soma' : {"sec": "soma", "loc": 0.5, "var": "V_soma"}}
simConfig.recordTraces = {'V_soma':{'var':'Vm'}}
	
#simConfig.recordStep = 1
#simConfig.filename = 'model_output'
#simConfig.savePickle = False
simConfig.analysis['plotRaster'] = True
simConfig.analysis['plotTraces'] = {'saveFig': True}
simConfig.analysis['plot2Dnet'] = {'saveFig' : True}

#sim.initialize(
#	simConfig = simConfig,
#	netParams = netParams
#)


sim.create(netParams, simConfig)


#lcell = [c for c in sim.net.cells if c.gid in sim.net.pops['A'].cellGids]
lcell = [c for c in sim.net.cells if c.gid in sim.net.pops['stim'].cellGids]

for cell in lcell: 
	cell.hPointp.interval = 5

lSTDPmech = []
for cell in sim.net.cells:
  for conn in cell.conns:
    STDPmech = conn.get('hSTDP')  # check if the connection has a NEURON STDP mechanism object
    if STDPmech: lSTDPmech.append(STDPmech)
###############################################################################
# RUN SIM
###############################################################################

def mycallback (t):
    print('mycallback', t)
    #for stdpmech in lSTDPmech: stdpmech.reward_punish(1.0)
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
                
#lcell3 = [c for c in sim.net.cells if c.gid in sim.net.pops['A'].cellGids]
#c = lcell3[0]
  
#sim.run.runSim()
sim.runSimWithIntervalFunc(50,mycallback)

insertSpikes(sim)

sim.gatherData()

sim.analysis.plotData()

#print(sim.simData['t'])
print(sim.simData)
print(lsynweights)
print(lSTDPmech)

import matplotlib.pyplot as plt 
fig, axes = plt.subplots(2,figsize = (20,10))
axes[0].plot(sim.simData['t'],sim.simData['V_soma']['cell_0'], label = "cell A")
axes[0].plot(sim.simData['t'],sim.simData['V_soma']['cell_1'], label = "cell B")
axes[0].legend()
axes[0].set_title('V_soma vs time')
#axes[0].set_xlabel('Times(ms)')	
axes[0].set_ylabel('V_soma')
axes[1].plot(sim.simData['spkt'],sim.simData['spkid'])
axes[1].set_title('spkid vs time')
axes[1].set_xlabel('Times(ms)')	
axes[1].set_ylabel('spkid')
plt.savefig('spkt.png', transparent = False )

"""
#sim.createSimulateAnalyze()
sim.create(netParams, simConfig) 
sim.gatherData() # gather data from different nodes
sim.analysis.plotData()    
"""






























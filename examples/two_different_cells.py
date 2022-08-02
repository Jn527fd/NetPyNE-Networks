#import NetPyNE libary
from netpyne import specs, sim

netParams = spec.NetParams() # parameters of the network
simConfig =  specs.SimConfig() #configuration of the simulation 

# {pyr: {'secs' : {}}}
netParams.cellParams['pyr'] = {} 

# define the soma
netParams.cellParams['pyr']['secs']['soma'] = {}

# add a geometry dictionary
netParams.cellParams['pyr']['secs']['soma']['geom'] = {
    'diam': 12,
    'L'   : 12,
    'Ra'  : 100.0,
    'cm'  : 1
}

# add a mechs dictionary to define biophysical mechanics
#uses the hodgkin-Huxley model
# hh.mod
netParams.cellParams['pyr']['secs']['soma']['mechs'] = {"hh" : {
    'gnabar': 0.12,
    'gkbar' : 0.036,
    'gl'    : 0.0003,
    'el'    : -54.3
}}

# build up a dend dictionary 
# pass mechanis is a simple leakage channel and buildtin to NEURON
dend = {}

# add a geometry dictionary
dend['geom'] = {
    'diam' : 1.0,
    'L'    : 200.0,
    'Ra'   : 100.0,
    'cm'   : 1,
}

# add a mechs dictionary to define biophysical mechanics for dendrities
# pas.mod
# passive.mod
dend['mechs'] = {"pas":
    {
        'g' : 0.001,
        'e' : -70
    }
}

# connect the dendrities compartement to the soma compartment 
# you must add a topol dictionary to our dend dictionary
dend['topol'] = {
    'parentSec' : 'soma',
    'parentX'   : 1.0,
    'childX'    : 0,

}

# add the dend section dinctionsary to the pyr cell dictionary
netParams.cellParams['pyr']['secs']['dend'] = dend

# create population one that holds one neuron
netParams.popParams['E'] = {
    'cellType' : 'pyr',
    'numCells' : 1,
}

#create population two that holds one neuron
netParams.popParams['I'] = {
    'cellType' : 'pyr',
    'numCells' : 1,
}


#add a stimulation
# create an entry to the 
#stimulation source parameters dictionary(stimSourceParams)
# stimulation = IClamp1
#using the NEURON type:iClamp
netParams.stimSourceParams['IClamp1'] = {
    'type' : 'IClamp',
    'dur'  : 5,
    'del'  : 20,
    'amp'  : 0.1,
}

#add a targer for the stimulation
#will stimulate the dends
#netParams.stimTargerParams['IClamp1->cell0'] = {
    "source" : "IClamp1",
    'conds'  : {'pop': ['E']},
#   "conds"  : {"cellList" : [0]},
    'sec'    : "dend",
    'loc'    : 1.0,
}


# creating synaptic model
# add dictionary synaptic mechanism parameters ditionary
# exp2Syn.mod
netParams.synMechParams['exc'] = {
    'mod'  : 'Exp2Syn',
    'taul' : 0.1,
    'tau2' : 1.0,
    'e'    : 0
}

# call connectiviney rule E->T because it will deinge connectivity from 
# the E population to the T population
netParams.connParams['E->I'] = {
    'preConds'    : {'pop': 'E'},
    'postConds'   : {'pop': 'I'},
    'weight'      : 0.005,
#   'probability' : 0.7, # 70 percent probability of connection 
    'delay'       : 5.0,
    'synMech'     : 'exc',
    'sec'         : 'soma',
#   'sec'         :'dend'
#   "loc"         : 1.0,
}

# call connectiviney rule T->E because it will deinge connectivity from 
# the E population to the T population
netParams.connParams['I->E'] = {
    'preConds'    : {'pop': 'I'},
    'postConds'   : {'pop': ['E']},
    'weight'      : 0.005,
#   'probability' : 0.7, # 70 percent probability of connection 
    'delay'       : 5.0,
    'synMech'     : 'exc',
    'sec'         : 'soma',
#   'loc'         : 1.0,
}

#simulation options
simConfig.duration = 0.5*1e3 #duration of the simulation, in ms
simConfig.dt = 0.1   #internal integration timestep to use
simConfig.hParams['celsius'] = 34
simConfig.verbose = False #show detailed messages
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  # Dict with traces to record
simConfig.recordStep = 0.1 			# Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model_output'  # Set file output name
simConfig.savePickle = False 		# Save params, network and sim output to pickle file

simConfig.analysis['iplotRaster'] =  {'markerSize': 5, 'showFig': True}
simConfig.analysis['iplotTraces'] = {'include': [0,2], 'oneFigPer': 'trace'}

if __name__ == '__main__':
    netpyne_geppetto.netParams=netParams
    netpyne_geppetto.simConfig=simConfig

#sim.createSimulateAnalyze(netParams, simConfig)

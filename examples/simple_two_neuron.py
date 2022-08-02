#import NetPyNE libary
#does not use the files in the "cell" or "mod" folders
from netpyne import specs, sim

netParams = spec.NetParams() # parameters of the network
simConfig =  specs.SimConfig() #configuration of the simulation 

# {pyr: {'secs' : {}}}
netParams.cellParams['pyr'] = {} 

# define the soma
netParams.cellParams['pyr']['secs']['soma'] = {}

# add a geometry dictionary
netParams.cellParams['pyr']['secs']['soma']['geom'] = {
    "diam": 12,
    "L"   : 12,
    "Ra"  : 100.0,
    "cm"  : 1
}

# add a mechs dictionary to define biophysical mechanics
#uses the hodgkin-Huxley model
# hh.mod
netParams.cellParams['pyr']['secs']['soma']['mechs'] = {"hh" : {
    "gnabar": 0.12,
    "gkbar" : 0.036,
    "gl"    : 0.0003,
    "el"    : -54.3
}}

# build up a dend dictionary 
# pass mechanis is a simple leakage channel and buildtin to NEURON
dend = {}

# add a geometry dictionary
dend['geom'] = {
    "diam" : 1.0,
    "L"    : 200.0,
    "Ra"   : 100.0,
    "cm"   : 1,
}

# add a mechs dictionary to define biophysical mechanics for dendrities
# pas.mod
# passive.mod
dend['mechs'] = {"pas":
    {
        "g" : 0.001,
        "e" : -70
    }
}

# connect the dendrities compartement to the soma compartment 
# you must add a topol dictionary to our dend dictionary
dend['topol'] = {
    "parentSec" : "soma",
    "parentX"   : 1.0,
    "childx"    : 0,

}

# add the dend section dinctionsary to the pyr cell dictionary
netParams.cellParams['pyr']['secs']['dend'] = dend

# create population one that holds one neuron
netParams.popParams['E'] = {
    "cellType" : "pyr",
    "numCells" : 1,
}

#create population two that holds one neuron
netParams.popParams['T'] = {
    "cellType" : "pyr",
    "numCells" : 1,
}

# creating synaptic model
# add dictionary synaptic mechanism parameters ditionary
# exp2Syn.mod
netParams.synMechParams['exc'] = {
    "mod"  : "Exp2Syn",
    "taul" : 0.1,
    "tau2" : 1.0,
    "e"    : 0
}

# call connectiviney rule E->T because it will deinge connectivity from 
# the E population to the T population
netParams.connParams['E->T'] = {
    "preConds"    : {"pop": "E"},
    "postConds"   : {"pop": "T"},
    "weight"      : 0.005,
    "probability" : 0.7, # 70 percent probability of connection 
    "delay"       : 5.0,
    "synMech"     : "exc",
    "sec"         : "dend",
    "loc"         : 1.0,
}

# set up the simulation configuration
simConfig.filename = "simple_network"
simConfig.duration = 200.0
simConfig.dt = 0.1

# record the simulation from the first cell to the middle to the end of cell
simConfig.recordCells = [0]
simConfig.recordTraces = {
    "V_soma" : {
        "sec" : "soma",
        "loc" : 0.5,
        "var" : "v",
    },
    
    "V_dend" : {
        "sec" : "dend",
        "loc" : 1.0,
        "var" : "v",
    }
}

#set up some plots to be automatically generated
simConfig.analysis = {
    "plotTraces" : {
        "include" : [0],
        "saveFig" : True,
    },
    "plotRaster" : {
        "saveFig" : True,
    }
}

# %matplotlib inline
from matplotlib import pyplot as plt

#command to create, simulate and analyze the model
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)

#overlay the traces
fig, figData = sim.analysis.plotTraces(overlay=True)

# plot the 2D connectivity of the network
fig, figData = sim.analysis.plot2Dnet()

#plot the connectivity matrix 
fig, figData = sim.analysis.plotConn()

#plots cellular level connectivity
fig, figData = sim.analysis.plotConn(feature='weight', groupBy='cell')

#add a stimulation
# create an entry to the 
#stimulation source parameters dictionary(stimSourceParams)
# stimulation = IClamp1
#using the NEURON type:iClamp
netParams.stimSourceParams['IClamp1'] = {
    "type" : "IClamp",
    "dur"  : 5,
    "del"  : 20,
    "amp"  : 0.1,

}

#add a targer for the stimulation
#will stimulate the dends
netParams.stimTargerParams['IClamp1->cell0'] = {
    "source" : "IClamp1",
    "conds"  : {"cellList" : [0]},
    "sec"    : "dend",
    "loc"    : 1.0,
}

#create, simulate and analyze the model
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)
fig, figData = sim.analysis.plotTraces(overlay=True)
fig, figData = sim.analysis.plotRaster(marker='o', markerSize=50)

#record and plot a variety of traces
#clear the "recordTraces" dictionary
# turn off the auromatic raster plot
simConfig.recordTraces = {}
simConfig.analysis['plotRaster'] = False

#record the conductances of the somatic conductances
#grabbed variables from the hh.mod file
simConfig.recordTraces['gNA'] = {
    'sec'  : 'soma',
    'loc'  : 0.5,
    'mech' :'hh',
    'var'  :'gna'
}

simConfig.recordTraces['gK']  = {
    'sec'  : 'soma',
    'loc'  : 0.5,
    'mech' :'hh',
    'var'  :'gk'
}

simConfig.recordTraces['gL']  = {
    'sec'  : 'soma',
    'loc'  : 0.5,
    'mech' :'hh',
    'var'  :'gl'
}

#re-run the simulation
sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)

#zoom in on one sprice and overlay the traces
fig, figData = sim.analysis.plotTraces(timeRange=[90,110], overlay=True)

# look in the file(exp2syn.mod) to see that the current variable is "i"
# record that and the voltage in the dendrites
simConfig.recordTraces = {}
simConfig.recordTraces['isyn0'] = {
    'sec'     : 'dend',
    'loc'     : 1.0,
    'synMech' : 'exc',
    'var'     : 'i'
}
simConfig.recordTraces['V_dend'] = {
    'sec'     : 'dend',
    'loc'     : 1.0,
    'var'     : 'v'
}

sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)

#records all the synaptic currents entering cell 0
sim.net.allCells[0].keys()

#connections coming onto the cell are in conns 
sim.net.allCells[0]['conns']

# record all the synaptic currents and create a loop that holds their trace name
simConfig.recordTraces = {}
simConfig.recordTraces['V_soma'] ={
    'sec' : 'soma',
    'loc' : 0.5,
    'var' : 'v'
}

simConfig.recordTraces['V_dend'] ={
    'sec' : 'dend',
    'loc' : 1.0,
    'var' : 'v'
}

syn_plots = {}
for index, presyn in enumerate(sim.net.allCells[0]['conns']):
    trace_name = 'i_syn_' + str(presyn['preGid'])
    syn_plots[trace_name] = None
    simConfig.recordTraces[trace_name] = {
        'sec'     : 'dend',
        'loc'     : 1.0,
        'synMech' : 'exc',
        'var'     : 'i',
        'index'   : index
    }
    
print(simConfig.recordTraces)

sim.createSimulateAnalyze(netParams=netParams, simConfig=simConfig)

#extract the data, simulation data get stored in sim.allSimData
sim.allSimData.keys()

#spkt is an array of the times of all spikes in the network 
#spkid is an array of the universal index of the cell spiking
#t is an array of the time for traces
#each is a dictionary with its key being cell_GID
#value = being the array of the trace
sim.allSimData.V_soma.keys()

#extract the data 
time = sim.allSimData['t']
v_soma = sim.allSimData['V_coma']['cell_0']
V_dend = sim.allSimData['V_dend']['cell_0']


for syn_plot is syn_plots:
    syn_plots[syn_plot] = sim.allSimData[syn_plot]['cell_0']

#make a custom plot
import mathplotlib.pyplot as plt
fig = plt.figure()

plt.subplot(211)
plt.plot(time, v_soma, label='v_soma')
plt.plot(time, v_dend, label='v_dend')
plt.legend()
plt.xlabel('Time (ms)')
plt.ylabel('Membrane potential (mV)')

plt.subplot(212)
for syn_plot in syn_plots:
    plt.plot(time, syn_plots(syn_plot), label=syn_plot)
plt.legend()
plt.xlabel('Time (ms)')
plt.ylabel('synaptic current (nA)')

plt.savefig('syn_currents.jpg', dpi=600)

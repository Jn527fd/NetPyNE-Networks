from netpyne import specs, sim

netParams = specs.NetParams()
simConfig = specs.SimConfig()

simConfig.hParams['celsius'] = 37

#########################
# Population Parameters #
#########################
netParams.popParams['Pyramidal'] = {
    'cellType'  : 'Pyramidalcell',
    'numCells'  : 1,
    'cellModel' : 'Pyramidal_model'}

netParams.popParams['Pyramidal_two'] = {
    'cellType'  : 'Pyramidalcell_two',
    'numCells'  : 1,
    'cellModel' : 'Pyramidal_model2'}

##########################
# Import Cell Parameters #
##########################

netParams.importCellParams(
    label          = 'Pyramidalcell',
    conds          = {'cellType' : 'Pyramidalcell',
                        'cellModel' : 'Pyramidal_model'},
    fileName       = 'cells/main_cell.py',
    cellName       = 'PYR2',
    importSynMechs = False)

netParams.importCellParams(
    label          = 'Pyramidalcell_two',
    conds          = {'cellType' : 'Pyramidalcell_two',
                        'cellModel' : 'Pyramidal_model2'},
    fileName       = 'cells/main_cell.py',
    cellName       = 'PYR2',
    importSynMechs = False)

cells=['Pyramidalcell', 'Pyramidalcell_two']

for i in cells:
    for sec in netParams.cellParams[i].secs:
        netParams.cellParams[i].secs[sec].threshold = 0.0
        
#########################################
# synapse of both neurons use STDP mech #
#########################################
netParams.synMechParams['STDP'] = {
    'mod': 'STDP',
    'RLon':1,
    'RLlenhebb':200,
    'RLhebbwt':0.001,
    'RLwindhebb':50,
    'wbase':0,
    'wmax':2}

""""
netParams.synMechParams['exc'] = {
    'mod'  : 'Exp2Syn',
    'tau1' : 0.1,
    'tau2' : 1.0,
    'e'    : 0}

netParams.synMechParams['inh'] = {
    'mod'  : 'Exp2Syn',
    'tau1' : 0.1,
    'tau2' : 1.0,
    'e'    : -80}
"""

################################
# stimulate one of the neurons #
################################
"""
netParams.stimSourceParams['Input_2'] = {
    'type': 'VClamp',
    'dur': [0, 1, 1],
    'amp':[1, 1, 1],
    'gain': 1,
    'rstim': 0,
    'tau1': 1,
    'tau2': 1,
    'i': 1}


netParams.stimTargerParams['Input_2->PYR'] = {
    'source'  : 'Input_2',
    'sec'     : 'soma',
    'loc'     : 0.8,
    'conds'   : {'pop':'Pyramidalcell'},
    'weight'  : 0.1,
    'delay'   : 1,
    'synmech' : 'exc'}
"""

#################################
# connect both Neurons together #
#################################
netParams.connParams['PYR->PYR2'] = {
    'preConds'   : {'pop': 'Pyramidalcell'},
    'postConds'  : {'pop': 'Pyramidalcell_two'},
    'synMech'    : 'STDP',
    'weight'     :  0.0015,
    'delay'      :  1.0,
    'loc'        :  0.6,
    'sec'        :  'soma'}

#########################
# Simulation Parameters #
#########################
simConfig.duration = 0.5*1e3
# Duration of the simulation, in ms

simConfig.dt = 0.025
# Internal integration timestep to use

simConfig.verbose = False
# Show detailed messages

simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.99,'var':'v'}}
# Dict with traces to record

simConfig.recordStep = 1
# Step size in ms to save data (eg. V traces, LFP, etc)

simConfig.filename = 'model_output'
# Set file output name

simConfig.savePickle = False
# Save params, network and sim output to pickle file

simConfig.analysis['plotRaster'] = {'syncLines': True, 'saveFig': True}
# Plot a raster

simConfig.analysis['plotTraces'] = {'include': [1], 'saveFig': True}
# Plot recorded traces for this list of cells

simConfig.analysis['plot2Dnet'] = {'saveFig': True}
# plot 2D cell positions and connections

######################
# Run the simulation #
######################
sim.initialize(
            simConfig = simConfig,
            netParams = netParams)
# create network object and set cfg and net params
# pass simulation config and network params as arguments

sim.net.createPops()
# instantiate network populations

sim.net.createCells()
# instantiate network cells based on defined populations

sim.net.connectCells()
# create connections between cells based on params

sim.net.addStims()
# add stimulation

sim.setupRecording()
# setup variables to record for each cell (spikes, V traces, etc)

sim.runSim()
# run parallel Neuron simulation

sim.gatherData()
# gather spiking data and cell info from each node

sim.saveData()
# save params, cell info and sim output to file (pickle,mat,txt,etc)

sim.analysis.plotData()
# plot spike raster

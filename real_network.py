##########################################
# Jesus G Naranjo
# 08/02/2022
# purpose: 
# To implement a small network using the NetPyne framework composed of 
# two neurons that connect one to another. The synapse of those neurons 
# will use Spike Timing Dependent Plasticity (STDP) rule to change the 
# strength of the connection.Then we need to stimulate one neuron and 
# plot the synaptic strength as a function of time
##########################################

#######################################
# import packages and call parameters #
#######################################
from netpyne import specs, sim 
from netpyne.spec import Dict

netParams = specs.NetParams()
simConfig = specs.simConfig()
simConfig.hParams['celsius'] = 37

######################
# network parameters #
######################
numCells = 1
connList = [[i,i] for i in range(cell_num)]

####################
# creates neuron A #
####################
netParams.popParams['A'] = {
    'numCells'  : numCells,
    'cellModel' : 'Mainen1'}

netparams.importCellParams(
    label    = 'PYR2_Mainen_rule',
    conds    = {'cellType' : ['A']},
    fileName = 'cells/mainen.py',
    cellName = 'PYR2')
    
####################
# creates neuron B #
####################
netparams.popParams['B'] = {
    'numCells'  : numCells,
    'cellModel' : 'Mainen2'}

netParams.importCellParams(
    label    = 'PYR3_Main_Cell', 
    conds    = {'celltype' : ['B']},
    fileName = 'cells/mainen.py',
    cellName = 'PYR3')
    
#########################################
# synapse of both neurons use STDP mech #
#########################################
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

######################
# stimulate neuron A #
######################
netParams.stimSourceParams['Input1'] = {
    'type': 'IClamp', 
    'del' : 300, 
    'dur' : 100, 
    'amp' : 'uniform(0.4,0.5)'}


netParams.stimTargerParams['Input1->A'] = {
    'source'  : 'Input_1', 
    'sec'     : 'soma', 
    'loc'     : 0.8, 
    'conds'   : {'pop':'A'},
    'synmech' : 'exc'}

#################################
# connect both Neurons together #
#################################
netParams.connParams['A->B'] = { #  S -> M label
        'preConds'   : {'pop': 'S'},   # conditions of presyn cells
        'postConds'  : {'pop': 'M'},  # conditions of postsyn cells
        'probability': 0.5,         # probability of connection
        'weight'     : 0.01,             # synaptic weight
        'delay'      : 5,                 # transmission delay (ms)
        'synMech'    : 'inh'}           # synaptic mechanism


################################################
# plot synaptic strength as a funciton of time #
################################################

#########################
# Simulation Parameters #
#########################
simConfig.duration = 0.5*1e3       
# Duration of the simulation, in ms
 
simConfig.dt = 0.025               
# Internal integration timestep to use
 
simConfig.verbose = False          
# Show detailed messages
 
simConfig.recordTraces = {'V_soma':{'sec':'soma','loc':0.5,'var':'v'}}  
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

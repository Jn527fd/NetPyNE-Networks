from netpyne import specs

###############################################################################
# NETWORK PARAMETERS
###############################################################################

netParams = specs.NetParams()

############################
# Cell parameters imported #
############################

netParams.importCellParams(
        label    = 'PYR_Mainen_rule',
        conds    = {'cellType' : 'PYR', 'cellModel':'Mainen'},
        fileName = 'cells/main_cell.py',
        cellName = 'PYR2')


#########################
# Population parameters #
#########################
netParams.popParams['cell_one'] = {
        'cellType': 'PYR',
        'cellModel': 'Mainen',
        'numCells': 1}


netParams.popParams['cell_two'] = {
        'numCells' : 1,
        'cellModel': 'Mainen',
        'cellType': 'PYR'}

#################################
# Synaptic mechanism parameters #
#################################
netParams.synMechParams['exc'] = {
        'mod': 'Exp2Syn',
        'tau1': 0.1,
        'tau2': 1.0,
        'e': 0}


netParams.synMechParams['stdpsyn'] = {
        'mod' : 'STDP',
        'RLon' : 1,
        'RLlenhebb' : 200,
        'RLhebbwt' : 0.001,
        'RLwindhebb' : 50,
        'wbase' : 0,
        'wmax' : 2}


#netParams.synMechParams['inh'] = {'mod': 'Exp2Syn', 'tau1': 0.1, 'tau2': 1.0, 'e': -80}


##########################
# Stimulation parameters #
##########################
netParams.stimSourceParams['NetStim'] = {
        'type': 'NetStim',
        'rate': 50,
        'noise': 10}


netParams.stimTargetParams['NetStim->cell_two'] = {
        'source': 'NetStim',
        'conds': {'pop': 'cell_two'},
        'weight': 1,
        'delay': 5,
        'synMech' : 'exc' }


###########################
# Connectivity parameters #
###########################
netParams.connParams['cell_one->cell_two'] = {
        'preConds': {'pop': 'cell_one'},             # presynaptic conditions
        'postConds': {'pop': 'cell_two'},     # postsynaptic conditions
        'weight': 1.0,                          # weight of each connection
        'synMech': 'stdpsyn',                   # target STDP  synapse
        'delay': 6,                             #delay
        'sec'   : 'soma'}

###############################################################################
# SIMULATION PARAMETERS
###############################################################################
cell_population = 'cell_one'


simConfig = specs.SimConfig()  # object of class SimConfig to store simulation configuration

# Simulation options
simConfig.duration = 6*1e4        # Duration of the simulation, in ms
simConfig.dt = 0.01                # Internal integration timestep to use
simConfig.verbose = False         # Show detailed messages
simConfig.recordCells = [cell_population]
simConfig.recordTraces['soma_voltage :' + cell_population] = {'sec' : 'soma', 'loc' : 0.5, 'var' : 'v' }  # Dict with traces to record
simConfig.recordTraces['Na_conn :' + cell_population] = {'sec': 'soma', 'loc': 0.5, 'var' : 'nai' }
##simConfig.recordTraces['iK_con(cell_two)'] = {'sec' : 'dend', 'loc' : '0.5', 'var' : 'ik'}
simConfig.recordStep = 1            # Step size in ms to save data (eg. V traces, LFP, etc)
simConfig.filename = 'model_output' # Set file output name
simConfig.savePickle = False        # Save params, network and sim output to pickle file
#simConfig.analysis['plotRaster'] = {'syncLines': True, 'saveFig': True}      # Plot a raster
simConfig.analysis['plotTraces'] = {'include': [1], 'saveFig': True}     # Plot recorded traces for this list of cells
simConfig.analysis['plot2Dnet'] = {'saveFig': True}                          # plot 2D cell positions and connections

###############################################################################
# EXECUTION CODE (via netpyne)
###############################################################################
from netpyne import sim

# Create network and run simulation
sim.initialize(                     # create network object and set cfg and net params
                simConfig = simConfig,          # pass simulation config and network params as arguments
                        netParams = netParams)
sim.net.createPops()                # instantiate network populations
sim.net.createCells()               # instantiate network cells based on defined populations
sim.net.connectCells()              # create connections between cells based on params
sim.net.addStims()                  # add stimulation
sim.setupRecording()                # setup variables to record for each cell (spikes, V traces, etc)
sim.runSim()                        # run parallel Neuron simulation
sim.gatherData()                    # gather spiking data and cell info from each node
# save params, cell info and sim output to file (pickle,mat,txt,etc)
sim.analysis.plotData()             # plot spike raster






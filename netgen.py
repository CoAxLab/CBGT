import random
from subprocess import call
import pickle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def makeChannel(dim='brain', pops=[], subchannels=[]):
    return {'dim': dim,
            'subchannels': subchannels,
            'pops': pops}


def makePop(name, receptors=[], data={}, data_overrides={}):
    recept_dict = {}
    for receptor in receptors:
        r_overrides = {}
        if type(receptor) is list:
            r_overrides = {
                'MeanExtCon': receptor[1],
                'MeanExtEff': receptor[2],
                'FreqExt': receptor[3]
            }
            receptor = receptor[0]
        recept_dict[receptor['name']] = receptor['data'].copy()
        recept_dict[receptor['name']].update(r_overrides)
    data = data.copy()
    data.update(data_overrides)
    return {'name': name, 'data': data, 'receptors': recept_dict}


def makeReceptor(name, preset={}, preset_overrides={}):
    data = {'Tau': 0, 'RevPot': 0, 'FreqExt': 0,
            'FreqExtSD': 0, 'MeanExtEff': 0, 'MeanExtCon': 0}
    data.update(preset)
    data.update(preset_overrides)
    return {'name': name, 'data': data}


def makePath(src, targ, receptor, preset=['all'], connectivity=1, efficacy=1,
             STFT=0, STFP=0, STDT=0, STDP=0, name='', cmtype='con', conmatrix=[]):
    return {'src': src,
            'targ': targ,
            'name': name,
            'receptor': receptor,
            'connectivity': connectivity,
            'efficacy': efficacy,
            'STFT': STFT,
            'STFP': STFP,
            'STDT': STDT,
            'STDP': STDP,
            'preset': preset,
            'cmtype': cmtype,
            'conmatrix': conmatrix}


def camP(connections, src, targ, receptor, preset=['all'], connectivity=1,
         efficacy=1, STFT=0, STFP=0, STDT=0, STDP=0, name='', cmtype='con', conmatrix=[]):
    maxlen = 1
    if type(receptor) is list:
        maxlen = len(receptor)
    if type(connectivity) is list:
        maxlen = len(connectivity)
    if type(efficacy) is list:
        maxlen = len(efficacy)
    if type(preset[0]) is list:
        maxlen = len(preset)

    if type(receptor) is not list:
        receptor = [receptor] * maxlen
    if type(connectivity) is not list:
        connectivity = [connectivity] * maxlen
    if type(efficacy) is not list:
        efficacy = [efficacy] * maxlen
    if type(preset[0]) is not list:
        preset = [preset] * maxlen

    for rec, con, eff, pre in zip(receptor, connectivity, efficacy, preset):
        connections.append(makePath(src, targ, rec, pre,
                                    con, eff, STFT, STFP, STDT, STDP, name, cmtype, conmatrix))


def makeHandle(name, targ, path, receptor=None, con=0, eff=0, preset=['syn'], conmatrix=[]):
    return {'name': name,
            'targ': targ,
            'path': path,
            'receptor': receptor,
            'connectivity': con,
            'efficacy': eff,
            'STFT': 0,
            'STFP': 0,
            'STDT': 0,
            'STDP': 0,
            'preset': preset,
            'cmtype': 'con',
            'conmatrix': conmatrix}


def makeHandleEvent(label, time, hname, hpath, freq):
    return {'label': label,
            'time': time,
            'hname': hname,
            'hpath': hpath,
            'freq': freq}


def makeEvent(time, etype, label='', pop='', receptor='', freq=0):
    return {'time': time,
            'etype': etype,
            'label': label,
            'pop': pop,
            'receptor': receptor,
            'freq': freq}


def constructCopies(dims, path, index=0):
    if index >= len(path):
        return [[]]
    copylist = []
    dimname = path[index]
    for i in range(0, dims[dimname]):
        subcopylist = constructCopies(dims, path, index + 1)
        for copy in subcopylist:
            copy.insert(0, i)
            copylist.append(copy)
    return copylist


def constructPopPaths(channel):
    poppaths = {}
    dimname = channel['dim']
    for pop in channel['pops']:
        poppaths[pop['name']] = [dimname]
    for subchannel in channel['subchannels']:
        subpoppaths = constructPopPaths(subchannel)
        for name, path in subpoppaths.items():
            subpoppaths[name].append(dimname)
        poppaths.update(subpoppaths)
    return poppaths


def constructPopCopies(dims, channel, poppaths):
    poplist = []
    for pop in channel['pops']:
        pop['path'] = poppaths[pop['name']]
        pathvals = constructCopies(dims, pop['path'])
        for pathval in pathvals:
            popcopy = pop.copy()
            popcopy['data'] = pop['data'].copy()
            popcopy['pathvals'] = pathval
            popcopy['uniquename'] = popcopy['name']
            for val in pathval:
                popcopy['uniquename'] += '_' + str(val)
            popcopy['targets'] = []
            poplist.append(popcopy)
    for subchannel in channel['subchannels']:
        subpoplist = constructPopCopies(dims, subchannel, poppaths)
        for pop in subpoplist:
            poplist.append(pop)
    return poplist


def constructConMatrix(dims, connection, path1, path2):
    # supports 'sym' 'all' 'anti' 'randbool'
    dim1 = path1[0]
    dim2 = path2[0]
    adj = []
    preset = connection['preset']
    for dist1 in range(0, dims[dim1]):
        adjrow = []
        for dist2 in range(0, dims[dim2]):
            con = 0
            if preset[0] == 'syn':
                if dist1 == dist2:
                    con = 1
            if preset[0] == 'anti':
                if dist1 != dist2:
                    con = 1
            if preset[0] == 'all':
                con = 1
            if preset[0] == 'randbool':
                if random.uniform(0, 1) < preset[1]:
                    con = 1
            adjrow.append(con)
        adj.append(adjrow)
    connection['conmatrix'] = adj


def constructTracts(connection, source, popcopylist):
    for target in popcopylist:
        if target['name'] == connection['targ']:
            i1 = len(source['pathvals']) - 1
            i2 = len(target['pathvals']) - 1
            valid = True
            while i1 >= 0 and i2 >= 0 and (i1 > 0 or i2 > 0):
                if source['path'][i1] != target['path'][i2]:
                    break
                if source['pathvals'][i1] != target['pathvals'][i2]:
                    valid = False
                    break
                i1 -= 1
                i2 -= 1
            if valid:
                dist1 = source['pathvals'][0]
                dist2 = target['pathvals'][0]
                conmod = connection['conmatrix'][dist1][dist2]
                if conmod > 0:
                    tract = {}
                    data = {}
                    tract['target'] = target['uniquename']
                    tract['name'] = connection['name']
                    data['TargetReceptor'] = connection['receptor']
                    data['STFacilitationTau'] = connection['STFT']
                    data['STFacilitationP'] = connection['STFP']
                    data['STDepressionTau'] = connection['STDT']
                    data['STDepressionP'] = connection['STDP']
                    data['Connectivity'] = connection['connectivity']
                    if connection['cmtype'] == 'con':
                        data['Connectivity'] *= conmod
                    data['MeanEff'] = connection['efficacy']
                    if connection['cmtype'] == 'eff':
                        data['MeanEff'] *= conmod
                    tract['data'] = data
                    source['targets'].append(tract)


def constructConnections(dims, connections, poppaths, popcopylist):
    for con in connections:
        constructConMatrix(
            dims, con, poppaths[con['src']], poppaths[con['targ']])
        for source in popcopylist:
            if source['name'] == con['src']:
                constructTracts(con, source, popcopylist)


def constructHandleCopies(dims, handletypes, poppaths, popcopylist):
    handles = []
    for handle in handletypes:
        constructConMatrix(
            dims, handle, handle['path'], poppaths[handle['targ']])
        for pathval in constructCopies(dims, handle['path']):
            handlecopy = handle.copy()
            handlecopy['targets'] = []
            handlecopy['pathvals'] = pathval
            handlecopy['frequency'] = 0
            handlecopy['std_dev'] = 0
            constructTracts(handlecopy, handlecopy, popcopylist)
            for tract in handlecopy['targets']:
                for pop in popcopylist:
                    if tract['target'] == pop['uniquename'] and handlecopy['receptor'] != None:
                        pop['receptors'][handlecopy['receptor']
                                         ]['MeanExtCon'] = tract['data']['Connectivity']
                        pop['receptors'][handlecopy['receptor']
                                         ]['MeanExtEff'] = tract['data']['MeanEff']
            handles.append(handlecopy)
    return handles


def constructEvents(handleevent, handles, eventlist):
    for handle in handles:
        if handle['name'] == handleevent['hname']:
            valid = True
            for spec, val in zip(handleevent['hpath'], handle['pathvals']):
                if spec != -1 and spec != val:
                    valid = False
            if valid:
                for tract in handle['targets']:
                    event = makeEvent(handleevent['time'], 'ChangeExtFreq', handleevent['label'],
                                      tract['target'], tract['data']['TargetReceptor'], handleevent['freq'])
                    eventlist.append(event)


def printNetData(poppaths, popcopylist, handles):
    for handle in handles:
        print(" ! ", handle['name'], handle['pathvals'])
        for tract in handle['targets']:
            print("  - ", tract['target'])
    for k, x in poppaths.items():
        print(" * ", k)
        for y in popcopylist:
            if y['name'] == k:
                print("  - ", y['uniquename'])
                for targ in y['targets']:
                    print("    - ", targ['target'])


def writeCsv(popcopylist):
    f = open('net.csv', 'w')
    f.write("connection name,from node,to node\n")
    counter = 0
    for pop in popcopylist:
        for tract in pop['targets']:
            # tractname = str(counter) + '_' + tract['name'] + '_' + str(
            #     tract['data']['Connectivity']) + '_' + str(tract['data']['MeanEff'])
            tractname = str(counter) + '_' + tract['name']
            f.write(tractname + ',' +
                    pop['uniquename'] + ',' + tract['target'] + "\n")
            counter += 1
    f.flush()
    f.close()


def writeConf(popcopylist):
    f = open('network.conf', 'w')
    for pop in popcopylist:
        f.write('% ' + pop['uniquename'] + '\n')
    for pop in popcopylist:
        f.write('\n\nNeuralPopulation: ' + pop['uniquename'] + '\n')
        f.write('%-------------------------------------------------------\n\n')
        for k, v in pop['data'].items():
            f.write(k + '=' + str(v) + '\n')
        for name, data in pop['receptors'].items():
            f.write('\nReceptor: ' + name + '\n')
            for k, v in data.items():
                f.write(k + '=' + str(v) + '\n')
            f.write('EndReceptor\n')
        for tract in pop['targets']:
            f.write('\nTargetPopulation: ' + tract['target'] + '\n')
            for k, v in tract['data'].items():
                if v != 0:
                    f.write(k + '=' + str(v) + '\n')
            f.write('EndTargetPopulation\n')
        f.write('\nEndNeuralPopulation\n')
    f.flush()
    f.close()


def writePro(eventlist):
    f = open('network.pro', 'w')
    for event in eventlist:
        f.write('\nEventTime ' + str(event['time']) + '\n\n')
        f.write('Type=' + event['etype'] + '\n')
        if event['label'] != '':
            f.write('Label=' + event['label'] + '\n')
        if event['pop'] != '':
            f.write('Population: ' + event['pop'] + '\n')
        if event['receptor'] != '':
            f.write('Receptor: ' + event['receptor'] + '\n')
        if event['etype'] == 'ChangeExtFreq':
            f.write('FreqExt=' + str(event['freq']) + '\n')
        f.write('\nEndEvent\n\n')
    f.flush()
    f.close()


def writePickle(trialdata):
    f = open('network.pickle', 'wb')
    pickle.dump(trialdata, f)
    f.flush()
    f.close()


def compileAndRun(trials=1, offset=0, sweepnumber=0):
    directory = getDirectory(sweepnumber)
    call('gcc -o ' + directory +
         '/sim BG_inh_pathway_spedup.c rando2.h -lm', shell=True)
    seed = 1000
    for trial in range(0, trials):
        call('./sim -ns -n' + str(trial + offset) + ' -s' + str(seed + trial + offset),
             shell=True, cwd='autotest')


def compileAndRunSweep(trials=1, offset=0, sweepcount=1):
    for sweepnumber in range(0, sweepcount):
        directory = getDirectory(sweepnumber)
        call('gcc -o ' + directory +
             '/sim BG_inh_pathway_spedup.c rando2.h -lm', shell=True)
    seed = 1000
    for trial in range(0, trials):
        for sweepnumber in range(0, sweepcount):
            directory = getDirectory(sweepnumber)
            call('./sim -ns -n' + str(trial + offset) + ' -s' + str(seed + trial + offset),
                 shell=True, cwd=directory)


def getCellDefaults():
    return {'N': 250,
            'C': 0.5,
            'Taum': 20,
            'RestPot': -70,
            'ResetPot': -55,
            'Threshold': -50,

            'RestPot_ca': -85,
            'Alpha_ca': 0.5,
            'Tau_ca': 80,
            'Eff_ca': 0.0,

            'tauhm': 20,
            'tauhp': 100,
            'V_h': -60,
            'V_T': 120,
            'g_T': 0}


def describeBG(**kwargs):
    ThExtEff = 2
    if 'ThExtEff' in kwargs:
        ThExtEff = kwargs['ThExtEff']
    SNrExtEff = 6
    if 'SNrExtEff' in kwargs:
        SNrExtEff = kwargs['SNrExtEff']

    c = []
    h = []

    cd_pre = getCellDefaults()

    GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})

    SNr = makePop("SNr", [GABA, [AMPA, 800, SNrExtEff, 0.8], NMDA], cd_pre)
    camP(c, 'SNr', 'Th', 'GABA', ['syn'], 1, 0.09)
    STNE = makePop("STNE", [GABA, [AMPA, 800, 1.6, 4], NMDA], cd_pre,
                   {'N': 2500, 'g_T': 0.06})
    camP(c, 'STNE', 'GPe', ['AMPA', 'NMDA'], ['syn'], 0.05, [0.05, 2])
    camP(c, 'STNE', 'SNr', 'NMDA', ['syn'], 1, 0.06)
    GPe = makePop("GPe", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 4], NMDA], cd_pre,
                  {'N': 2500, 'tauhm': 10, 'g_T': 0.01})
    camP(c, 'GPe', 'GPe', 'GABA', ['syn'], 0.05, 1.5)
    camP(c, 'GPe', 'STNE', 'GABA', ['syn'], 0.02, 0.8)
    camP(c, 'GPe', 'SNr', 'GABA', ['syn'], 1, 0.04)
    camP(c, 'GPe', 'STR', 'GABA', ['syn'], 1, 0.03, name='arkipallidal')
    STR = makePop("STR", [GABA, [AMPA, 800, 4, 1.6], NMDA], cd_pre)
    camP(c, 'STR', 'STR', 'GABA', ['syn'], 1, 1)
    camP(c, 'STR', 'SNr', 'GABA', ['syn'], 1, 2.4, name='direct')
    camP(c, 'STR', 'GPe', 'GABA', ['syn'], 1, 3)
    LIP = makePop("LIP", [GABA, [AMPA, 800, 2.0, 3],
                          NMDA], cd_pre, {'N': 240})
    camP(c, 'LIP', 'Th', 'AMPA', ['syn'], 1, 0)
    camP(c, 'LIP', 'STR', 'AMPA', ['syn'], 1, 1.0)
    camP(c, 'LIP', 'LIPb', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['syn'], 1, [0.085, 0.2805])
    camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['anti'], 1, [0.043825, 0.14462])
    camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])
    Th = makePop('Th', [GABA, [AMPA, 800, ThExtEff, 3.2], NMDA],
                 cd_pre)
    # camP(c, 'Th', 'Th', 'NMDA', ['syn'], 1, 1.5)
    # camP(c, 'Th', 'LIPI', 'NMDA', ['all'], 1, 0.32, STDP=0.45, STDT=600)
    camP(c, 'Th', 'LIP', 'NMDA', ['syn'], 1, 0.32, STDP=0.45, STDT=600)
    action_channel = makeChannel('choices', [SNr, STNE, GPe, STR, LIP, Th])
    LIPb = makePop("LIPb", [GABA, [AMPA, 800, 2.1, 3],
                            NMDA], cd_pre, {'N': 1120})
    camP(c, 'LIPb', 'LIPb', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    camP(c, 'LIPb', 'LIP', ['AMPA', 'NMDA'], ['all'], 1, [0.043825, 0.14462])
    camP(c, 'LIPb', 'LIPI', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])
    LIPI = makePop("LIPI", [GABA, [AMPA, 800, 1.62, 3], NMDA], cd_pre, {
                   'N': 400, 'C': 0.2, 'Taum': 10})
    camP(c, 'LIPI', 'LIPb', 'GABA', ['all'], 1, 1.3)
    camP(c, 'LIPI', 'LIP', 'GABA', ['all'], 1, 1.3)
    camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1)
    brain = makeChannel('brain', [LIPb, LIPI], [action_channel])

    return (brain, c, h)


def describeSubcircuit(**kwargs):
    c = []
    h = []

    cd_pre = getCellDefaults()

    GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})

    STNE = makePop('STNE', [GABA, [AMPA, 800, 1, 4], NMDA],
                   cd_pre, {'N': 2500, 'g_T': 0.06})
    camP(c, 'STNE', 'GPeI', 'AMPA', ['syn'], 0.05, 0.05)
    camP(c, 'STNE', 'GPeI', 'NMDA', ['syn'], 0.05, 10)
    GPeI = makePop('GPeI', [[GABA, 2500, 22, 1], [
                   AMPA, 800, 1.6, 5], NMDA], cd_pre, {'N': 2500, 'g_T': 0.06})
    camP(c, 'GPeI', 'GPeI', 'GABA', ['syn'], 0.05, 0.02)
    camP(c, 'GPeI', 'STNE', 'GABA', ['syn'], 0.02, 10)
    brain = makeChannel('brain', [GPeI, STNE])

    return (brain, c, h)


def mcInfo(**kwargs):
    dims = {'brain': 1, 'choices': 2}

    hts = []
    hts.append(makeHandle('sensory', 'LIP', ['choices'], 'AMPA', 800, 2.1))
    hts.append(makeHandle('cancel', 'STNE', ['choices'], 'AMPA', 800, 1.6))
    hts.append(makeHandle('out', 'Th', ['choices']))

    hes = []
    hes.append(makeHandleEvent('reset', 0, 'sensory', [], 0))
    hes.append(makeHandleEvent('wrong stimulus', 600, 'sensory', [], 3.0772))
    hes.append(makeHandleEvent('right stimulus', 600, 'sensory', [0], 3.2884))

    houts = []
    houts.append(makeHandleEvent('decision made', 600, 'out', [], 20))

    timelimit = 1300

    return (dims, hts, hes, houts, timelimit)


def modifyNetwork(popcopylist, connections, **kwargs):
    for key, value in kwargs.items():
        if key == 'popscale':
            for pop in popcopylist:
                pop['data']['N'] *= value
            for path in connections:
                # scale C and then E only if needed
                # maybe some other form of balancing is better
                path['connectivity'] /= value
                if path['connectivity'] > 1:
                    path['efficacy'] *= path['connectivity']
                    path['connectivity'] = 1
        for path in connections:
            if key == path['name']:
                path['efficacy'] *= value


def configureExperiment(**kwargs):
    # get network description
    brain, connections, handletypes = describeBG(**kwargs)

    # get description relevant to this experiment and merge
    dims, hts, handleeventlist, outputevents, timelimit = mcInfo(**kwargs)
    for ht in hts:
        handletypes.append(ht)

    # create network populations
    poppaths = constructPopPaths(brain)
    popcopylist = constructPopCopies(dims, brain, poppaths)

    # modify network
    modifyNetwork(popcopylist, connections, **kwargs)

    # create all network connections
    handles = constructHandleCopies(dims, handletypes, poppaths, popcopylist)
    constructConnections(dims, connections, poppaths, popcopylist)

    # create events from handleevents
    eventlist = []
    for he in handleeventlist:
        constructEvents(he, handles, eventlist)
    eventlist.append(makeEvent(timelimit, 'EndTrial'))

    # write files
    # printNetData(poppaths, popcopylist, handles)
    writeCsv(popcopylist)
    writeConf(popcopylist)
    writePro(eventlist)

    trialdata = {'dims': dims,
                 'poppaths': poppaths,
                 'popcopylist': popcopylist,
                 'handles': handles,
                 'eventlist': eventlist,
                 'outputevents': outputevents}
    trialdata.update(kwargs)

    writePickle(trialdata)

    return trialdata


def readTrialResult(sweepnumber, trial):
    directory = getDirectory(sweepnumber)
    f = open(directory + '/popfreqs' + str(trial) + '.dat', "r")
    columns = []
    rawdata = []
    lines = f.readlines()
    for i in range(len(lines)):
        if i == 0:
            columns = lines[i].strip().split("\t")
            for colnum in range(len(columns)):
                rawdata.append([])
        if i > 0:
            data = lines[i].strip().split("\t")
            if(float(data[0]) > 2):
                for colnum, val in zip(range(len(columns)), data):
                    rawdata[colnum].append(val)
    labeled = {}
    for colnum in range(len(columns)):
        labeled[columns[colnum]] = np.array(rawdata[colnum], dtype='float32')

    g = open(directory + '/network.pickle', 'rb')
    trialdata = pickle.load(g)

    trialdata['popfreqs'] = pd.DataFrame(labeled)

    return(trialdata)


def readAllTrialResults(trials, offset=0, sweepcount=1):
    allresults = []
    for sweepnumber in range(sweepcount):
        results = []
        for trial in range(trials):
            results.append(readTrialResult(sweepnumber, trial + offset))
        allresults.append(results)
    return allresults


def findOutputs(trialdata, df=None):
    if df is None:
        df = trialdata['popfreqs']
    outputs = {}
    for handleevent in trialdata['outputevents']:
        output = {'time': None,
                  'start': handleevent['time'],
                  'delay': None,
                  'pathvals': None,
                  'threshold': handleevent['freq']}
        outputs[handleevent['label']] = output
        for handle in trialdata['handles']:
            if handle['name'] == handleevent['hname']:
                valid = True
                for spec, val in zip(handleevent['hpath'], handle['pathvals']):
                    if spec != -1 and spec != val:
                        valid = False
                if valid:
                    for tract in handle['targets']:
                        for i in range(0, df.shape[0]):
                            curtime = df.at[i, 'Time (ms)']
                            if curtime < output['start']:
                                continue
                            if df.at[i, tract['target']] >= output['threshold']:
                                if output['time'] == None or curtime < output['time']:
                                    output['time'] = curtime
                                    output['delay'] = curtime - output['start']
                                    output['pathvals'] = handle['pathvals']
                                break
    return outputs


def getDirectory(sweepnumber=0):
    return 'autotest' + str(sweepnumber)


def configureSweep(sc=0, **kwargs):
    for key, value in kwargs.items():
        if type(value) is list:
            selected = {}
            selected.update(kwargs)
            for opt in value:
                selected[key] = opt
                sc = configureSweep(sc, **selected)
            return sc
    configureExperiment(**kwargs)
    directory = getDirectory(sc)
    call('mkdir -p ' + directory, shell=True)
    for filename in ['network.conf', 'network.pro', 'network.pickle']:
        call('mv ' + filename + ' ' + directory + '/' + filename, shell=True)
    return sc + 1

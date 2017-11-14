#!usr/bin/env python
import os, sys
import random
from subprocess import call
from subprocess import Popen
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from . import netconfig

# number of clients for multiprocess
parallel = 4
# package_dir
_package_dir = os.path.dirname(os.path.realpath(__file__))

def makeHandle(name, targ, path, receptor=None, con=0,
               eff=0, preset=['syn'], conmatrix=[]):
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


def makeHandleEvent(label, time, hname, hpath, freq, etype='ChangeExtFreq'):
    return {'label': label,
            'time': time,
            'hname': hname,
            'hpath': hpath,
            'freq': freq,
            'etype': etype}


def makeEvent(time, etype, label='', pop='', freq=0, receptor=''):
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


# def constructConnections(dims, connections, poppaths, popcopylist):
#     for con in connections:
#         constructConMatrix(
#             dims, con, poppaths[con['src']], poppaths[con['targ']])
#         for source in popcopylist:
#             if source['name'] == con['src']:
#                 constructTracts(con, source, popcopylist)


def constructConnections(dims, connections, poppaths, popcopylist, **kwargs):
    for con in connections:
        constructConMatrix(
            dims, con, poppaths[con['src']], poppaths[con['targ']])
        for key, value in kwargs.items():
            if key == con['name']:
                if isinstance(value, dict):
                    for src,dest,mult in zip(value['src'],value['dest'],value['mult']):
                        con['conmatrix'][src][dest] *= mult
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
                    if tract['target'] == pop['uniquename'] and handlecopy['receptor'] is not None:
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
                    if handleevent['etype'] == 'ChangeExtFreq':
                        event = makeEvent(handleevent['time'], 'ChangeExtFreq', handleevent['label'],
                                          tract['target'], handleevent['freq'], tract['data']['TargetReceptor'])
                    if handleevent['etype'] == 'EndTrial':
                        event = makeEvent(handleevent['time'], 'EndTrial', handleevent['label'],
                                          tract['target'], handleevent['freq'])
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
            # tract['data']['Connectivity']) + '_' +
            # str(tract['data']['MeanEff'])
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
        if event['pop'] != '':
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
    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
    elif sys.platform == "darwin":
        compiler = 'gcc-7'

    simfile = os.path.join(getDirectory(sweepnumber), 'sim')
    call('{} -o {} BG_inh_pathway_spedup.c rando2.h -lm -std=c99'.format(compiler, simfile), shell=True, cwd=_package_dir)

    seed = 1000
    for trial in range(0, trials):
        Popen('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)
    os.chdir(wkdir)



def compileAndRunSweep(trials=1, offset=0, sweepcount=1):
    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
    elif sys.platform == "darwin":
        compiler = 'gcc-7'

    for sweepnumber in range(0, sweepcount):
        simfile = os.path.join(getDirectory(sweepnumber), 'sim')
        call('{} -o {} BG_inh_pathway_spedup.c rando2.h -lm -std=c99'.format(compiler, simfile), shell=True, cwd=_package_dir)

    seed = 1000
    for trial in range(0, trials):
        for sweepnumber in range(0, sweepcount):
            outdir = getDirectory(sweepnumber)
            if (trial * sweepcount + sweepnumber + 1) % parallel == 0:
                call('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)
            else:
                Popen('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)



def mcInfo(**kwargs):

    config = {'BaseStim': 2.3,
              'WrongStim': 2.50,
              'RightStim': 2.54,
              'Start': 400,
              'Choices': 2,
              'Dynamic': 30}

    config.update(kwargs)

    dims = {'brain': 1, 'choices': config['Choices']}

    hts = []
    hts.append(makeHandle('sensory', 'LIP', ['choices'], 'AMPA', 800, 2.1))
    # hts.append(makeHandle('cancel', 'STNE', ['choices'], 'AMPA', 800, 1.6))
    hts.append(makeHandle('out', 'Th', ['choices']))

    hes = []
    hes.append(makeHandleEvent('reset', 0, 'sensory', [], config['BaseStim']))
    hes.append(makeHandleEvent('wrong stimulus',
                               config['Start'], 'sensory', [], config['WrongStim']))
    hes.append(makeHandleEvent('right stimulus', config['Start'],
                               'sensory', [0], config['RightStim']))
    hes.append(makeHandleEvent('dynamic cutoff',
                               config['Start'], 'out', [], config['Dynamic'], 'EndTrial'))

    houts = []
    houts.append(makeHandleEvent('decision made',
                                 config['Start'], 'out', [], config['Dynamic']))

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
            if key == path['name'] and not isinstance(value, dict):
                path['efficacy'] *= value


def configureExperiment(**kwargs):

    if 'preset' in kwargs:
        kwargs.update(kwargs['preset'])

    # get network description
    brain, connections, handletypes = netconfig.describeBG(**kwargs)

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
    constructConnections(dims, connections, poppaths, popcopylist, **kwargs)

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
            if(float(data[0]) > 0):
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
                            if df.at[i, tract['target']
                                     ] >= output['threshold']:
                                if output['time'] is None or curtime < output['time']:
                                    output['time'] = curtime
                                    output['delay'] = curtime - output['start']
                                    output['pathvals'] = handle['pathvals']
                                break
    trialdata['outputs'] = outputs
    return outputs


def setDirectory(prefix='autotest'):
    global directoryprefix
    directoryprefix = os.path.join(os.path.expanduser('~'), prefix)


def getDirectory(sweepnumber=0):
    return ''.join([directoryprefix, str(sweepnumber)])


def configureSweep(sc=0, **kwargs):
    for key, value in kwargs.items():
        if isinstance(value, list):
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

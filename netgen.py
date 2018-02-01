#!usr/bin/env python
import os, sys
import random
from subprocess import call
from subprocess import Popen
import pickle

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# number of clients for multiprocess
parallel = 4
# package_dir
_package_dir = os.path.dirname(os.path.realpath(__file__))


def makeChannel(dim='brain', pops=[], subchannels=[]):
    return {'dim': dim,
            'subchannels': subchannels,
            'pops': pops}


def makePop(name, receptors=[], data={}, data_overrides={}):
    recept_dict = {}
    for receptor in receptors:
        r_overrides = {}
        if isinstance(receptor, list):
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
             STFT=0, STFP=0, STDT=0, STDP=0, name='', cmtype='eff', conmatrix=[]):
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
         efficacy=1, STFT=0, STFP=0, STDT=0, STDP=0, name='', cmtype='eff', conmatrix=[]):
    maxlen = 1
    if isinstance(receptor, list):
        maxlen = len(receptor)
    if isinstance(connectivity, list):
        maxlen = len(connectivity)
    if isinstance(efficacy, list):
        maxlen = len(efficacy)
    if isinstance(preset[0], list):
        maxlen = len(preset)

    if not isinstance(receptor, list):
        receptor = [receptor] * maxlen
    if not isinstance(connectivity, list):
        connectivity = [connectivity] * maxlen
    if not isinstance(efficacy, list):
        efficacy = [efficacy] * maxlen
    if not isinstance(preset[0], list):
        preset = [preset] * maxlen

    for rec, con, eff, pre in zip(receptor, connectivity, efficacy, preset):
        connections.append(makePath(src, targ, rec, pre,
                                    con, eff, STFT, STFP, STDT, STDP, name, cmtype, conmatrix))


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

    seed = np.random.randint(0, 1000)
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

    seed = np.random.randint(0, 1000)
    for trial in range(0, trials):
        for sweepnumber in range(0, sweepcount):
            outdir = getDirectory(sweepnumber)
            if (trial * sweepcount + sweepnumber + 1) % parallel == 0:
                call('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)
            else:
                Popen('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)



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

    config = {'STNExtEff': 1.7,
              'GPiExtEff': 6.0,
              'CxSTR': 0.5,
              'M1STR': 0.5,
              'M1Th': 0.2,
              'STNExtFreq': 4.0}
    config.update(kwargs)
    c = []
    h = []
    cd_pre = getCellDefaults()
    GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})



    LIP = makePop("LIP", [GABA, [AMPA, 800, 2.0, 3],NMDA], cd_pre, {'N': 240})
    camP(c, 'LIP', 'D1STR', 'AMPA', ['syn'], 0.5, config['CxSTR'], name='cxd')
    camP(c, 'LIP', 'D2STR', 'AMPA', ['syn'], 0.5, config['CxSTR'], name='cxi')
    camP(c, 'LIP', 'LIPb', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['syn'], 1, [0.085, 0.2805], name='LIPsyn')
    camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['anti'], 1, [0.043825, 0.14462])
    camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])

    LIPb = makePop("LIPb", [GABA, [AMPA, 800, 2.0, 3],NMDA], cd_pre, {'N': 1120})
    camP(c, 'LIPb', 'LIPb', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    camP(c, 'LIPb', 'LIP', ['AMPA', 'NMDA'], ['all'], 1, [0.043825, 0.14462])
    camP(c, 'LIPb', 'LIPI', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])

    LIPI = makePop("LIPI", [GABA, [AMPA, 800, 1.62, 3], NMDA], cd_pre, {'N': 400, 'C': 0.2, 'Taum': 10})
    camP(c, 'LIPI', 'LIPb', 'GABA', ['all'], 1, 1.3)
    camP(c, 'LIPI', 'LIP', 'GABA', ['all'], 1, 1.3)
    camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1)


    M1 = makePop("M1", [GABA, [AMPA, 800, 2.0, 2.9], NMDA], cd_pre, {'N': 240})
    camP(c, 'M1', 'Th', 'AMPA', ['syn'], 1, config['M1Th'])
    camP(c, 'M1', 'D1STR', 'AMPA', ['syn'], 1, config['M1STR'])
    camP(c, 'M1', 'D2STR', 'AMPA', ['syn'], 1, config['M1STR'])
    camP(c, 'M1', 'M1b', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    camP(c, 'M1', 'M1', ['AMPA', 'NMDA'], ['syn'], 1, [0.085, 0.2805], name='M1syn')
    camP(c, 'M1', 'M1', ['AMPA', 'NMDA'], ['anti'], 1, [0.043825, 0.14462])
    camP(c, 'M1', 'M1I', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])

    M1b = makePop("M1b", [GABA, [AMPA, 800, 2.0, 2.4],NMDA], cd_pre, {'N': 1120})
    camP(c, 'M1b', 'M1b', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    camP(c, 'M1b', 'M1', ['AMPA', 'NMDA'], ['all'], 1, [0.043825, 0.14462])
    camP(c, 'M1b', 'M1I', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])

    M1I = makePop("M1I", [GABA, [AMPA, 800, 1.62, 3], NMDA], cd_pre, {'N': 400, 'C': 0.2, 'Taum': 10})
    camP(c, 'M1I', 'M1b', 'GABA', ['all'], 1, 1.3)
    camP(c, 'M1I', 'M1', 'GABA', ['all'], 1, 1.3)
    camP(c, 'M1I', 'M1I', 'GABA', ['all'], 1, 1)


    D1STR = makePop("D1STR", [GABA, [AMPA, 800, 4, 1.6], NMDA], cd_pre)
    camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], 1, 1)
    camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], 1, 2.64, name='direct')

    D2STR = makePop("D2STR", [GABA, [AMPA, 800, 4, 1.6], NMDA], cd_pre)
    camP(c, 'D2STR', 'D2STR', 'GABA', ['syn'], 1, 1)
    camP(c, 'D2STR', 'GPeP', 'GABA', ['syn'], 1, 3.3, name='indirect')

    FSI = makePop("FSI", [GABA, [AMPA, 800, 4, 1.6], NMDA], cd_pre)
    camP(c, 'FSI', 'FSI', 'GABA', ['all'], 1, 1)
    camP(c, 'FSI', 'D1STR', 'GABA', ['all'], 1, 1)
    camP(c, 'FSI', 'D2STR', 'GABA', ['all'], 1, 1)


    GPeP = makePop("GPeP", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 5], NMDA], cd_pre,{'N': 2500, 'tauhm': 10, 'g_T': 0.01})
    camP(c, 'GPeP', 'GPeP', 'GABA', ['all'], 0.02, 1.5)
    camP(c, 'GPeP', 'STNE', 'GABA', ['syn'], 0.02, 0.4)
    camP(c, 'GPeP', 'GPi', 'GABA', ['syn'], 1, 0.01)

    GPeA = makePop("GPeA", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 4], NMDA], cd_pre,{'N': 2500, 'tauhm': 10, 'g_T': 0.01})
    camP(c, 'GPeA', 'FSI', 'GABA', ['all'], 1, 0.015, name='arkyfsi')
    camP(c, 'GPeA', 'D1STR', 'GABA', ['all'], 1, 0.0125, name='arkyd')
    camP(c, 'GPeA', 'D2STR', 'GABA', ['all'], 1, 0.0125, name='arkyi')
    camP(c, 'GPeA', 'GPeA', 'GABA', ['all'], 0.02, 1.5)


    STNE = makePop("STNE", [GABA, [AMPA, 800, config['STNExtEff'], config['STNExtFreq']], NMDA],
        cd_pre, {'N': 2500, 'g_T': 0.06})
    camP(c, 'STNE', 'GPeA', ['AMPA', 'NMDA'], ['all'], 0.05, [0.025, 1])
    camP(c, 'STNE', 'GPeP', ['AMPA', 'NMDA'], ['syn'], 0.05, [0.05, 4])
    camP(c, 'STNE', 'GPi', 'NMDA', ['all'], 1, 0.03)


    GPi = makePop("GPi", [ GABA, [AMPA, 800, config['GPiExtEff'], 0.8], NMDA], cd_pre)
    camP(c, 'GPi', 'Th', 'GABA', ['syn'], 1, 0.09)

    Th = makePop('Th', [GABA, [AMPA, 800, 2, 3.2], NMDA], cd_pre)
    camP(c, 'Th', 'M1', 'NMDA', ['syn'], 1, 0.37, STDP=0.45, STDT=600, name='ThM1')
    # camP(c, 'Th', 'D1STR', 'AMPA', ['syn'], 0.5, config['CxSTR']/2, STDP=0.45, STDT=600, name='ThSTR')
    # camP(c, 'Th', 'D2STR', 'AMPA', ['syn'], 0.5, config['CxSTR']/2, STDP=0.45, STDT=600, name='ThSTR')


    action_channel = makeChannel('choices', [GPi, STNE, GPeP, D1STR, D2STR, LIP, M1, Th])
    brain = makeChannel('brain', [LIPb, LIPI, M1b, M1I, FSI, GPeA], [action_channel])
    # camP(c, 'Th', 'Th', 'NMDA', ['syn'], 1, 1.5)
    # camP(c, 'Th', 'LIPI', 'NMDA', ['all'], 1, 0.32, STDP=0.45, STDT=600)
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

    config = {'BaseStim': 2.0,
              'WrongStim': 2.50,
              'RightStim': 2.54,
              'Start': 500,
              'Choices': 2,
              'Dynamic': 30}

    config.update(kwargs)

    dims = {'brain': 1, 'choices': config['Choices']}

    hts = []
    hts.append(makeHandle('sensory', 'LIP', ['choices'], 'AMPA', 800, 2.0))
    hts.append(makeHandle('motor', 'M1', ['choices'], 'AMPA', 800, 2.0))
    # hts.append(makeHandle('cancel', 'STNE', ['choices'], 'AMPA', 800, 1.6))
    hts.append(makeHandle('out', 'Th', ['choices']))

    hes = []
    hes.append(makeHandleEvent('reset', 0, 'sensory', [], config['BaseStim']))
    hes.append(makeHandleEvent('reset', 0, 'motor', [], config['BaseStim']))
    hes.append(makeHandleEvent('wrong stimulus',
                               config['Start'], 'sensory', [], config['WrongStim']))
    hes.append(makeHandleEvent('right stimulus', config['Start'],
                               'sensory', [0], config['RightStim']))
    hes.append(makeHandleEvent('dynamic cutoff',
                               config['Start'], 'out', [], config['Dynamic'], 'EndTrial'))

    houts = []
    houts.append(makeHandleEvent('decision made',
                                 config['Start'], 'out', [], config['Dynamic']))

    timelimit = 1800

    return (dims, hts, hes, houts, timelimit)


def ssInfo(**kwargs):

    config = {'BaseStim': 2.0,
              'WrongStim': 2.50,
              'RightStim': 2.54,
              'Start': 500,
              'Choices': 1,
              'Dynamic': 30,
              'CancelDelay': 200,
              'CancelStim': 4.0}

    config.update(kwargs)

    dims = {'brain': 1, 'choices': config['Choices']}

    hts = []
    hts.append(makeHandle('sensory', 'LIP', ['choices'], 'AMPA', 800, 2.0))
    hts.append(makeHandle('motor', 'M1', ['choices'], 'AMPA', 800, 2.0))
    hts.append(makeHandle('cancel', 'STNE', ['choices'], 'AMPA', 800, 1.6))
    hts.append(makeHandle('out', 'Th', ['choices']))

    hes = []
    hes.append(makeHandleEvent('reset', 0, 'sensory', [], config['BaseStim']))
    hes.append(makeHandleEvent('wrong stimulus',
                               config['Start'], 'sensory', [], config['WrongStim']))
    hes.append(makeHandleEvent('right stimulus', config['Start'],
                               'sensory', [0], config['RightStim']))

    hes.append(makeHandleEvent('dynamic cutoff',
                               config['Start'], 'out', [], config['Dynamic'], 'EndTrial'))

    if config['stop'] != 0:
        hes.append(makeHandleEvent('cancel stimulus',
                                   config['Start'] + config['CancelDelay'], 'cancel', [], config['CancelStim']))
        hes.append(makeHandleEvent('cancel input',
                                   config['Start'] + config['CancelDelay'], 'sensory', [], config['BaseStim']))

    houts = []
    houts.append(makeHandleEvent('decision made',
                                 config['Start'], 'out', [], config['Dynamic']))

    timelimit = 1500

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
    brain, connections, handletypes = describeBG(**kwargs)

    # get description relevant to this experiment and merge
    if kwargs['experiment'] == 'mc':
        dims, hts, handleeventlist, outputevents, timelimit = mcInfo(**kwargs)
    if kwargs['experiment'] == 'ss':
        dims, hts, handleeventlist, outputevents, timelimit = ssInfo(**kwargs)
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
    call('mkdir -p ' + directoryprefix, shell=True)
    call('mkdir -p ' + directory, shell=True)
    for filename in ['network.conf', 'network.pro', 'network.pickle']:
        call('mv ' + filename + ' ' + directory + '/' + filename, shell=True)
    return sc + 1

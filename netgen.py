#!usr/bin/env python
import os, sys
import random
from subprocess import call
from subprocess import Popen
from copy import deepcopy
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



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


def makeHandleEvent(label, time, hname='', hpath='', freq='', etype='ChangeExtFreq', rewardflag='', rewardval=''):
    return {'label': label,
            'time': time,
            'hname': hname,
            'hpath': hpath,
            'freq': freq,
            'etype': etype,
            'rewardflag': rewardflag,
            'rewardval': rewardval}


def makeEvent(time, etype, label='', pop='', freq=0, receptor='', rewardflag='', rewardval=''):
    return {'time': time,
            'etype': etype,
            'label': label,
            'pop': pop,
            'receptor': receptor,
            'freq': freq,
            'rewardflag': rewardflag,
            'rewardval': rewardval}


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
    if handleevent['hname'] == '':
        if handleevent['etype'] == 'DivideStage':
            event = makeEvent(handleevent['time'], 'DivideStage')
            eventlist.append(event)
        if handleevent['etype'] == 'EndTrial':
            event = makeEvent(handleevent['time'], 'EndTrial')
            eventlist.append(event)
    else:
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
                                              tract['target'], handleevent['freq'], '',
                                              handleevent['rewardflag'], handleevent['rewardval'])
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
        if event['rewardflag'] != '':
            f.write('RewardFlag=' + str(event['rewardflag']) + '\n')
        if event['rewardval'] != '':
            f.write('RewardVal=' + str(event['rewardval']) + '\n')
        f.write('\nEndEvent\n\n')
    f.flush()
    f.close()


def writePickle(trialdata):
    f = open('network.pickle', 'wb')
    pickle.dump(trialdata, f)
    f.flush()
    f.close()

def compileOnly(trials=1, offset=0, sweepcount=1):
    parallel = 0
    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
        # number of clients for multiprocess
        parallel = 8
    elif sys.platform == "darwin":
        compiler = 'gcc-7'
        parallel = 4

    for sweepnumber in range(0, sweepcount):
        simfile = os.path.join(getDirectory(sweepnumber), 'sim')
        call('{} -o {} BG_inh_pathway_spedup.c rando2.h -lm -std=c99'.format(compiler, simfile), shell=True, cwd=_package_dir)

def compileAndRun(trials=1, offset=0, sweepnumber=0):
    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
    elif sys.platform == "darwin":
        compiler = 'gcc-7'

    simfile = os.path.join(getDirectory(sweepnumber), 'sim')
    call('{} -o {} BG_inh_pathway_spedup.c rando2.h -lm -std=c99'.format(compiler, simfile), shell=True, cwd=_package_dir)

    seed = np.random.randint(0, 1000)
    for trial in range(0, trials):
        outdir = getDirectory(sweepnumber)
        Popen('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)
    #os.chdir(wkdir)



def compileAndRunSweep(trials=1, offset=0, sweepcount=1):
    parallel = 0
    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
        # number of clients for multiprocess
        parallel = 8
    elif sys.platform == "darwin":
        compiler = 'gcc-7'
        parallel = 4

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



def compileAndRunSweepALL(trials=1, offset=0, sweepcount=1):
    parallel = 0
    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
        # number of clients for multiprocess
        parallel = 8
    elif sys.platform == "darwin":
        compiler = 'gcc-7'
        parallel = 4

    for sweepnumber in range(0, sweepcount):
        simfile = os.path.join(getDirectory(sweepnumber), 'sim')
        call('{} -o {} BG_inh_pathway_spedup.c rando2.h -lm -std=c99'.format(compiler, simfile), shell=True, cwd=_package_dir)

    seed = np.random.randint(0, 1000)

    for sweepnumber in range(0, sweepcount):
        for trial in range(0, trials):
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

def getD1CellDefaults():
    return {
                # not specific
                'dpmn_tauDOP':2.0*10,
                 #'dpmn_taug':3.0,
                'dpmn_alpha':0.05,
                'dpmn_DAt':0.2,
                'dpmn_taum':4000.0*5,
                # specific to D1
                'dpmn_type': 1,
                'dpmn_alphaw': 0.00080,
                'dpmn_dPRE': 10,
                'dpmn_dPOST':6,
                'dpmn_tauE':3*3,
                'dpmn_tauPRE':9*3,
                'dpmn_tauPOST':1.2*3,
                'dpmn_wmax':0.13,
                'dpmn_a':1.0,
                'dpmn_b':0.1,
                'dpmn_c':0.05,
                # explicit initial conditions
                'dpmn_w':0.015,
                'dpmn_Q1':0.0,
                'dpmn_Q2':0.0,
                # implicit initial conditions
                'dpmn_m': 1.0,
                'dpmn_E': 0.0,
                'dpmn_DAp': 0.0,
                'dpmn_APRE': 0.0,
                'dpmn_APOST': 0.0,
                'dpmn_XPRE': 0.0,
                'dpmn_XPOST': 0.0}

def getD2CellDefaults():
    return {
                # not specific
                'dpmn_tauDOP':2.0*10,
                 #'dpmn_taug':3.0,
                'dpmn_alpha':0.05,
                'dpmn_DAt':0.2,
                'dpmn_taum':4000.0*5,
                # specific to D1
                'dpmn_type': 2,
                'dpmn_alphaw': -0.00055,
                'dpmn_dPRE': 10,
                'dpmn_dPOST':6,
                'dpmn_tauE':3*3,
                'dpmn_tauPRE':9*3,
                'dpmn_tauPOST':1.2*3,
                'dpmn_wmax':0.03,
                'dpmn_a':0.5,
                'dpmn_b':0.005,
                'dpmn_c':0.05,
                # explicit initial conditions
                'dpmn_w':0.015,
                'dpmn_Q1':0.0,
                'dpmn_Q2':0.0,
                # implicit initial conditions
                'dpmn_m': 1.0,
                'dpmn_E': 0.0,
                'dpmn_DAp': 0.0,
                'dpmn_APRE': 0.0,
                'dpmn_APOST': 0.0,
                'dpmn_XPRE': 0.0,
                'dpmn_XPOST': 0.0}


def describeBG(**kwargs):

    config = {'STNExtEff': 1.7,
              'GPiExtEff': 6.0,
              'CxSTR': 0.5,
              'M1STR': 0.5,
              'CxTh': 0.2,
              'STNExtFreq': 4.0,
              'rampingCTX': False}

    # makePop(name, receptors=[], data={}, data_overrides={})

    # camP(connections, src, targ, receptor, preset=['all'], connectivity=1,
    #       efficacy=1, STFT=0, STFP=0, STDT=0, STDP=0, name='', cmtype='eff', conmatrix=[])


    config.update(kwargs)
    c = []
    h = []
    cd_pre = getCellDefaults()
    GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})

    LIP = makePop("LIP", [GABA, [AMPA, 800, 2.8, 2.2], NMDA], cd_pre, {'N': 680})

    camP(c, 'LIP', 'D1STR', ['AMPA', 'NMDA'], ['syn'], 0.45, [config['CxSTR'], config['CxSTR']], name='cxd')
    camP(c, 'LIP', 'D2STR',  ['AMPA', 'NMDA'], ['syn'], 0.45, [config['CxSTR'], config['CxSTR']], name='cxi')
    camP(c, 'LIP', 'FSI', 'AMPA', ['all'], 0.45, config['CxFSI'], name='cxfsi')
    camP(c, 'LIP', 'Th', ['AMPA', 'NMDA'], ['all'], 0.35, [config['CxTh'], config['CxTh']])

    D1STR = makePop("D1STR", [GABA, [AMPA, 800, 4., 1.3], NMDA], cd_pre, getD1CellDefaults())
    camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], .135, .28)
    camP(c, 'D1STR', 'D2STR', 'GABA', ['syn'], .135, .28)
    camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], .55, 1.05*0.90, name='direct')

    D2STR = makePop("D2STR", [GABA, [AMPA, 800, 4., 1.3], NMDA], cd_pre, getD2CellDefaults())
    camP(c, 'D2STR', 'D2STR', 'GABA', ['anti'], .135, .28)
    camP(c, 'D2STR', 'D1STR', 'GABA', ['syn'], .15, .28/2)
    camP(c, 'D2STR', 'D1STR', 'GABA', ['anti'], .15, .28/2)
    camP(c, 'D2STR', 'GPeP', 'GABA', ['syn'], .74, 1.65, name='indirect')

    FSI = makePop("FSI", [GABA, [AMPA, 800, 1.55, 3.], NMDA], cd_pre, {'C': 0.2, 'Taum': 10})
    camP(c, 'FSI', 'FSI', 'GABA', ['all'], .85, 1.15)
    camP(c, 'FSI', 'D1STR', 'GABA', ['all'], .65, 1.2)
    camP(c, 'FSI', 'D2STR', 'GABA', ['all'], .62, 1.2)

    GPeP = makePop("GPeP", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 4.85], NMDA],
                    cd_pre, {'N': 2500, 'g_T': 0.06})
    camP(c, 'GPeP', 'GPeP', 'GABA', ['all'], 0.02, 1.5)
    camP(c, 'GPeP', 'STNE', 'GABA', ['syn'], 0.02, 0.4)
    camP(c, 'GPeP', 'GPi', 'GABA', ['syn'], 1, 0.012)

    STNE = makePop("STNE", [GABA, [AMPA, 800, config['STNExtEff'],
                config['STNExtFreq']], NMDA], cd_pre, {'N': 2500, 'g_T': 0.06})
    camP(c, 'STNE', 'GPeP', ['AMPA', 'NMDA'], ['syn'], 0.0485, [0.07, 4])
    camP(c, 'STNE', 'GPi', 'NMDA', ['all'], 1, 0.0314)

    GPi = makePop("GPi", [ GABA, [AMPA, 800, config['GPiExtEff'], 0.8], NMDA], cd_pre)
    camP(c, 'GPi', 'Th', 'GABA', ['syn'], .85, 0.067)

    Th = makePop('Th', [GABA, [AMPA, 800, 2.5, 2.2], NMDA], cd_pre)
    camP(c, 'Th', 'D1STR', 'AMPA', ['syn'], 0.45, config['ThSTR'])
    camP(c, 'Th', 'D2STR', 'AMPA', ['syn'], 0.45, config['ThSTR'])
    camP(c, 'Th', 'FSI', 'AMPA', ['all'], 0.25, config['ThSTR'])
    camP(c, 'Th', 'LIP', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcx')

    action_channel = makeChannel('choices', [GPi, STNE, GPeP, D1STR, D2STR, LIP, Th])

    ineuronPops = [FSI]

    if config['rampingCTX']:
        camP(c, 'Th', 'LIPI', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcxi')
        camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['all'], .13, [0.0127, 0.15])
        camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], .0725, [0.013, 0.125])

        LIPI = makePop("LIPI", [GABA, [AMPA, 640, .6, 1.05], NMDA], cd_pre, { 'N': 620, 'C': 0.2, 'Taum': 10})
        camP(c, 'LIPI', 'LIP', 'GABA', ['all'], .5, 1.05)
        camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1.075)

        ineuronPops.append(LIPI)

    brain = makeChannel('brain', ineuronPops, [action_channel])

    return (brain, c, h)


def mcInfo(**kwargs):

    config = {'BaseStim': 2.0,
              'WrongStim': 2.50,
              'RightStim': 2.50,
              'Start': 500,
              'Choices': 2,
              'Dynamic': 30}

    config.update(kwargs)

    dims = {'brain': 1, 'choices': config['Choices']}

    hts = []
    hts.append(makeHandle('sensory', 'LIP', ['choices'], 'AMPA', 800, 2.0))
    # hts.append(makeHandle('motor', 'M1', ['choices'], 'AMPA', 800, 2.0))
    # hts.append(makeHandle('cancel', 'STNE', ['choices'], 'AMPA', 800, 1.6))
    hts.append(makeHandle('threshold', 'STNE', ['choices'], 'AMPA', 800, 1.65))
    hts.append(makeHandle('out', 'Th', ['choices']))

    hes = []
    houts = []
    for i in range(0,50):
        hes.append(makeHandleEvent('reset', 0, 'sensory', [], config['BaseStim']))
        hes.append(makeHandleEvent('wrong stimulus', config['Start'], 'sensory', [], config['WrongStim']+0.025*(i%2)))
        hes.append(makeHandleEvent('right stimulus', config['Start'], 'sensory', [0], config['RightStim']+0.025*((i+1)%2)))
        hes.append(makeHandleEvent('hyperdirect', config['Start'], 'threshold', [], config['STNExtFreq']+.75))
        hes.append(makeHandleEvent('hyperdirect', config['Start'], 'threshold', [0], config['STNExtFreq']+.75))
        hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [0], config['Dynamic'], 'EndTrial', 1, 1))
        hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial', 2, 0))
        hes.append(makeHandleEvent('time limit', 600, etype='EndTrial'))
        houts.append(makeHandleEvent('decision made', config['Start'], 'out', [], config['Dynamic'], 'EndTrial'))
        houts.append(makeHandleEvent('time limit', 600, etype='EndTrial'))

    # timelimit = 1800
    timelimit = 1200

    return (dims, hts, hes, houts)


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
    return (dims, hts, hes, houts)


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
        dims, hts, handleeventlist, outputevents = mcInfo(**kwargs)
    if kwargs['experiment'] == 'ss':
        dims, hts, handleeventlist, outputevents = ssInfo(**kwargs)
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


def readTrialResult(sweepnumber, trial, datastreams = ['popfreqs']):
    directory = getDirectory(sweepnumber)
    g = open(directory + '/network.pickle', 'rb')
    trialdata = pickle.load(g)
    for datastream in datastreams:
        f = open(directory + '/' + datastream + str(trial) + '.dat', "r")
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

        trialdata[datastream] = pd.DataFrame(labeled)

    return(trialdata)


def readAllTrialResults(trials, offset=0, sweepcount=1, datastreams = ['popfreqs']):
    allresults = []
    trialID = lambda f: int(f.split(datastreams[0])[1].split('.')[0])

    for sweepnumber in range(sweepcount):
        results = []
        files = os.listdir(getDirectory(sweepnumber))
        trials = [trialID(f) for f in files if datastreams[0] in f]
        for trial in trials:
            results.append(readTrialResult(sweepnumber, trial + offset, datastreams))
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
                                if output['time'] is None or curtime < output['time']:
                                    output['time'] = curtime
                                    output['delay'] = curtime - output['start']
                                    output['pathvals'] = handle['pathvals']
                                break
    trialdata['outputs'] = outputs
    return outputs

def findOutputs2(trialdata, df=None):
    if df is None:
        df = trialdata['popfreqs']
    outputs = {}
    outevents = trialdata['outputevents']
    for handleevent in outevents:
        outputs[handleevent['label']] = []
    curstage = 0
    stagestart = 0
    firstrelevantevent = 0
    lastrelevantevent = 1
    for e in range(firstrelevantevent, len(outevents)):
        handleevent = outevents[e]
        if len(outputs[handleevent['label']]) <= curstage:
            output = {'time': None,
                      'start': handleevent['time'],
                      'delay': None,
                      'pathvals': None,
                      'threshold': handleevent['freq']}
            outputs[handleevent['label']].append(output)
        if e == lastrelevantevent and not (handleevent['etype'] == 'EndTrial' and handleevent['hname'] == ''):
            lastrelevantevent += 1;
    for i in range(0, df.shape[0]):
        curtime = df.at[i, 'Time (ms)']
        needsmorestaging = 0
        for e in range(firstrelevantevent, lastrelevantevent):
            handleevent = outevents[e]
            output = outputs[handleevent['label']][curstage]
            if curtime < output['start'] + stagestart:
                continue
            if handleevent['etype'] == 'EndTrial' and handleevent['hname'] == '':
                if curtime >= output['start'] + stagestart:
                    needsmorestaging = 1
                    continue
            for handle in trialdata['handles']:
                if handle['name'] == handleevent['hname']:
                    valid = True
                    for spec, val in zip(handleevent['hpath'], handle['pathvals']):
                        if spec != -1 and spec != val:
                            valid = False
                    if valid:
                        for tract in handle['targets']:
                            if df.at[i, tract['target']] >= output['threshold']:
                                if output['time'] is None:
                                    output['time'] = curtime
                                    output['delay'] = curtime - stagestart - output['start']
                                    output['pathvals'] = handle['pathvals']
                                    if handleevent['etype'] == 'EndTrial':
                                        needsmorestaging = 1
        if needsmorestaging == 1:
            curstage += 1
            stagestart = curtime
            firstrelevantevent = lastrelevantevent
            lastrelevantevent += 1
            for e in range(firstrelevantevent, len(outevents)):
                handleevent = outevents[e]
                if len(outputs[handleevent['label']]) <= curstage:
                    output = {'time': None,
                              'start': handleevent['time'],
                              'delay': None,
                              'pathvals': None,
                              'threshold': handleevent['freq']}
                    outputs[handleevent['label']].append(output)
                if e == lastrelevantevent and not (handleevent['etype'] == 'EndTrial' and handleevent['hname'] == ''):
                    lastrelevantevent += 1;
    trialdata['outputs'] = outputs
    return outputs

def setDirectory(prefix='autotest'):
    global directoryprefix
    directoryprefix = os.path.join(os.path.expanduser('~'), prefix, 'sweeps')


def getDirectory(sweepnumber=0):
    return os.path.join(directoryprefix, str(sweepnumber))


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

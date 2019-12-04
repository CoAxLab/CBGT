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


def set_post_learning_weights(dMSN=[1.01, 0.99], iMSN=[1.0, 1.0]):

    preset = [{'cxd': {'dest': [0, 1], 'mult': dMSN, 'src': [0, 1]},
              'cxi': {'dest': [0, 1], 'mult': iMSN, 'src': [0, 1]}}]
    return preset

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



def compileAndRun(trials=1, offset=0, sweepnumber=0, parallel=4):

    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
    elif sys.platform == "darwin":
        compiler = 'gcc-8'

    c_dir = os.path.join(_package_dir, 'src')

    simfile = os.path.join(getDirectory(sweepnumber), 'sim')
    call('{} -o {} cbgt.c rando2.h -lm -std=c99'.format(compiler, simfile), shell=True, cwd=c_dir)

    seed = np.random.randint(0, 1000)
    for trial in range(0, trials):
        outdir = getDirectory(sweepnumber)
        Popen('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)
    #os.chdir(wkdir)



def compileAndRunSweep(trials=1, offset=0, sweepcount=1, parallel=4):

    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
        # number of clients for multiprocess
    elif sys.platform == "darwin":
        compiler = 'gcc-8'

    c_dir = os.path.join(_package_dir, 'src')
    # seed = np.random.randint(0, 1000)
    for sweepnumber in range(0, sweepcount):
        simfile = os.path.join(getDirectory(sweepnumber), 'sim')
        call('{} -o {} cbgt.c rando2.h -lm -std=c99'.format(compiler, simfile), shell=True, cwd=c_dir)

    for trial in range(0, trials):
        for sweepnumber in range(0, sweepcount):
            outdir = getDirectory(sweepnumber)
            seed = np.random.randint(0, 1000)
            if (trial * sweepcount + sweepnumber + 1) % parallel == 0:
                call('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)
            else:
                Popen('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)



def compileAndRunSweepALL(trials=1, offset=0, sweepcount=1, parallel=4):

    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
        # number of clients for multiprocess
    elif sys.platform == "darwin":
        compiler = 'gcc-8'

    c_dir = os.path.join(_package_dir, 'src')

    for sweepnumber in range(0, sweepcount):
        simfile = os.path.join(getDirectory(sweepnumber), 'sim')
        call('{} -o {} cbgt.c rando2.h -lm -std=c99'.format(compiler, simfile), shell=True, cwd=c_dir)

    threadcounter = 1

    for trial in range(0, trials):
        for sweepnumber in range(0, sweepcount):
            outdir = getDirectory(sweepnumber)
            seed = np.random.randint(0, 1000)
            if threadcounter % parallel == 0:
                call('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)
            else:
                Popen('./sim -ns -n{} -s{}'.format(str(trial+offset), str(seed+trial+offset)), shell=True, cwd=outdir)
            threadcounter += 1


def compileAndRunSweepALL_NEW(trials=1, offset=0, sweepcount=1, parallel=4):

    if sys.platform == "linux" or sys.platform == "linux2":
        compiler = 'gcc'
        # number of clients for multiprocess
    elif sys.platform == "darwin":
        compiler = 'gcc-8'

    # c_dir = os.path.join(_package_dir, 'src')

    for sweepnumber in range(0, sweepcount):
        simfile = os.path.join(getDirectory(sweepnumber), 'sim')
        call('{} -o {} cbgt.c rando2.h -lm -std=c99'.format(compiler, simfile), shell=True)

    for sweepnumber in range(0, sweepcount):
        for trial in range(0, trials):
            outdir = getDirectory(sweepnumber)
            seed = np.random.randint(0, 1000)
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
                'dpmn_tauDOP':2,         #2.0*10,  2*5
                 #'dpmn_taug':3.0,
                'dpmn_alpha':0.05*6,
                'dpmn_DAt':0.0,              #0.2,
                'dpmn_taum':0,#4000.0*5,
                # specific to D1
                'dpmn_type': 1,
                'dpmn_alphaw': 55/3.0,          # 0.55
                'dpmn_dPRE': 0.8,              #10,
                'dpmn_dPOST':0.04,           #6,   0.087
                'dpmn_tauE': 3*5,             #3*3,
                'dpmn_tauPRE': 3*5,           #9*3,
                'dpmn_tauPOST':1.2*5,        #1.2*3,
                'dpmn_wmax':0.3,
                'dpmn_a':1.0,
                'dpmn_b':0.1,
                'dpmn_c':0.05,
                # explicit initial conditions
                'dpmn_w':0.2*.9,
                'dpmn_winit':0.2*.9,
                'dpmn_ratio':1.0,
                'dpmn_implied':1.0,
                'dpmn_Q1':0.0,                #0.5,
                'dpmn_Q2':0.0,                #0.5,
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
                'dpmn_tauDOP': 2,          #2.0*10,  2*5
                 #'dpmn_taug':3.0,
                'dpmn_alpha':0.05*6,
                'dpmn_DAt':0,               #0.25,
                'dpmn_taum':0,#4000.0*5,         #4000.0*5,
                # specific to D1
                'dpmn_type': 2,
                'dpmn_alphaw': -45/3.0,     #-0.45
                'dpmn_dPRE': 0.8,         #10,
                'dpmn_dPOST': 0.04,      #6
                'dpmn_tauE':3*5,              #3*3,
                'dpmn_tauPRE':3*5,            #9*3,
                'dpmn_tauPOST':1.2*5,         #1.2*3,
                'dpmn_wmax':0.3,
                'dpmn_a':0.5,
                'dpmn_b':0.005,
                'dpmn_c':0.05,
                # explicit initial conditions
                'dpmn_w':0.2*.9,             #0.015,
                'dpmn_winit':0.2*.9,
                'dpmn_ratio':1.0,
                'dpmn_implied':1.0,
                'dpmn_Q1':0.0,                #0.5,
                'dpmn_Q2':0.0,                #0.5,
                # implicit initial conditions
                'dpmn_m': 1.0,
                'dpmn_E': 0.0,
                'dpmn_DAp': 0.0,
                'dpmn_APRE': 0.0,
                'dpmn_APOST': 0.0,
                'dpmn_XPRE': 0.0,
                'dpmn_XPOST': 0.0}

def getConProb():

    conProb = {'Cx': {'STR': .45,
                        'FSI': 0.45,
                        'Th': .35},
                'D1STR': {'D1STR': .135,
                          'D2STR': .135,
                          'GPi': .57},
                'D2STR': {'D1STR_syn': .15,
                          'D1STR_anti': .135,
                          'D2STR_syn': .135,
                          'GPeP': .74},
                'FSI':  {'FSI': .85,
                        'D1STR': .66,
                        'D2STR': .62},
                'GPeP': {'GPeP': 0.02,
                        'STN': 0.02,
                        'GPi': 1},
                'STN': {'GPeP': 0.0485,
                        'GPi': 1},
                'GPi': {'Th': 0.85},
                'Th': {'STR': 0.45,
                        'FSI': 0.25,
                        'Cx': 0.25,
                        'CxI': 0.25}
                }

    return conProb


def getConEff(**kwargs):

    conEff = {'Cx': {'STR': [0.2, 0.2],
                    'FSI': 0.16*.5,
                    'Th': [0.0335, 0.0335]},
                'D1STR': {'D1STR': .28,
                          'D2STR': .28,
                          'GPi': 1.07},
                'D2STR': {'D1STR_syn': .28,
                          'D1STR_anti': .28,
                          'D2STR_syn': .28,
                          'GPeP': 1.65},
                'FSI':  {'FSI': 1.15,
                        'D1STR': 1.23*.8,
                        'D2STR': 1.23*.8},
                'GPeP': {'GPeP': 1.5,
                        'STN': 0.4,
                        'GPi': 0.012},
                'STN': {'GPeP': [0.07, 4],
                        'GPi': 0.0324},
                'GPi': {'Th': 0.067},
                'Th': {'STR': 0.3,
                        'FSI': 0.3,
                        'Cx': 0.015,
                        'CxI': 0.015}
                }

    kwkeys = list(kwargs)
    nuclei = list(conEff)
    for i in nuclei:
        if i in kwkeys:
            targets = list(kwargs[i])
            for j in targets:
                isList = isinstance(conEff[i][j], list)
                if isList and not isinstance(kwargs[i][j], list):
                    kwargs[i][j] = [kwargs[i][j]]*2
                conEff[i][j] = kwargs[i][j]

    if 'STN' in kwkeys:
        if 'GPeP' in list(kwargs['STN']):
            if not isinstance(kwargs['STN']['GPeP'], list):
                print('STN_GPeP needs AMPA and NMDA efficacies,\nOnly one efficacy found\nfilling with default values')
                conEff['STN']['GPeP'] = [0.07, 4]

    return conEff


def getNetworkDefaults():

    config = {'CxExtEff': 2.8,
              'CxExtFreq': 2.2,

              'STRExtEff': 4.0,
              'STRExtFreq': 1.3,

              'FSIExtEff': 1.55,
              'FSIExtFreq': 3.*1.2,

              'STNExtEff': 1.60,
              'STNExtFreq': 4.45,

              'GPiExtEff': 5.9,
              'GPiExtFreq': 0.8,

              'GPeExtEff': 2,
              'GPeExtFreq': 4, #5, #4.85,

              'ThExtEff': 2.5,
              'ThExtFreq': 2.2,

              'BaseStim': [0.00],
              'Stim': [2.6],
              'Dynamic': [30.0],
              'rampingCTX': True,
              'dpmn_ratio':0,
              'dpmn_implied':1}

    return config


def describeBG(**kwargs):

    # makePop(name, receptors=[], data={}, data_overrides={})
    # camP(connections, src, targ, receptor, preset=['all'], connectivity=1,
    #       efficacy=1, STFT=0, STFP=0, STDT=0, STDP=0, name='', cmtype='eff', conmatrix=[])

    config = getNetworkDefaults()
    config.update(kwargs)

    if 'conEff' in list(kwargs):
        conEff = kwargs['conEff']
        # print(conEff)
    else:
        conEff = getConEff()

    if 'conProb' in list(kwargs):
        conProb = kwargs['conProb']
        # print(conProb)
    else:
        conProb = getConProb()

    c = []
    h = []
    cd_pre = getCellDefaults()
    GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})

    LIP = makePop("LIP", [GABA,
                        [AMPA, 800, config['CxExtEff'],
                        config['CxExtFreq']], NMDA],
                        cd_pre, {'N': 680, 'dpmn_cortex': 1})

    camP(c, 'LIP', 'D1STR', ['AMPA', 'NMDA'], ['syn'], conProb['Cx']['STR'], conEff['Cx']['STR'], name='cxd')
    camP(c, 'LIP', 'D2STR',  ['AMPA', 'NMDA'], ['syn'], conProb['Cx']['STR'], conEff['Cx']['STR'], name='cxi')
    camP(c, 'LIP', 'FSI', 'AMPA', ['all'], conProb['Cx']['FSI'], conEff['Cx']['FSI'], name='cxfsi')
    camP(c, 'LIP', 'Th', ['AMPA', 'NMDA'], ['all'], conProb['Cx']['Th'], conEff['Cx']['Th'])

    d1pmn_mapping = {'dpmn_ratio': config['dpmn_ratio'],
               'dpmn_implied': config['dpmn_implied'],
               'dpmn_alphaw': config['d1aw']
               }

    d1cell = getD1CellDefaults()
    d1cell.update(d1pmn_mapping)

    d2pmn_mapping = {'dpmn_ratio': config['dpmn_ratio'],
           'dpmn_implied': config['dpmn_implied'],
           'dpmn_alphaw': config['d2aw']
           }

    d2cell = getD2CellDefaults()
    d2cell.update(d2pmn_mapping)

    D1STR = makePop("D1STR", [GABA,
                            [AMPA, 800, config['STRExtEff'],
                            config['STRExtFreq']], NMDA], cd_pre, d1cell)
    D2STR = makePop("D2STR", [GABA,
                            [AMPA, 800, config['STRExtEff'],
                            config['STRExtFreq']], NMDA], cd_pre, d2cell)

    camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], conProb['D1STR']['D1STR'], conEff['D1STR']['D1STR'])
    camP(c, 'D1STR', 'D2STR', 'GABA', ['syn'], conProb['D1STR']['D2STR'], conEff['D1STR']['D2STR'])
    camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], conProb['D1STR']['GPi'], conEff['D1STR']['GPi'], name='direct')

    camP(c, 'D2STR', 'D2STR', 'GABA', ['syn'], conProb['D2STR']['D2STR_syn'], conEff['D2STR']['D2STR_syn'])
    camP(c, 'D2STR', 'D1STR', 'GABA', ['syn'], conProb['D2STR']['D1STR_syn'], conEff['D2STR']['D1STR_syn'])
    camP(c, 'D2STR', 'GPeP', 'GABA', ['syn'], conProb['D2STR']['GPeP'], conEff['D2STR']['GPeP'], name='indirect')

    #######################
    #        TEST         #
    #######################
    # camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], .1, .28)
    # camP(c, 'D1STR', 'D2STR', 'GABA', ['syn'], .1, .28)
    # camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], .57, 1.07, name='direct')
    # camP(c, 'D2STR', 'D1STR', 'GABA', ['syn'], .135, .28)
    # camP(c, 'D2STR', 'D2STR', 'GABA', ['syn'], .12, .28)

    # camP(c, 'D2STR', 'D1STR', 'GABA', ['anti'], .135, .28)
    # camP(c, 'D2STR', 'D2STR', 'GABA', ['anti'], .12, .28)
    # camP(c, 'D2STR', 'GPeP', 'GABA', ['syn'], .74, 1.65, name='indirect')
    # camP(c, 'D2STR', 'GPeP', 'GABA', ['syn'], .74, 1.65, name='indirect')

    FSI = makePop("FSI", [GABA,
                        [AMPA, 800, config['FSIExtEff'],
                        config['FSIExtFreq']], NMDA],
                        cd_pre, {'C': 0.2, 'Taum': 10})
    camP(c, 'FSI', 'FSI', 'GABA', ['all'], conProb['FSI']['FSI'], conEff['FSI']['FSI'])
    camP(c, 'FSI', 'D1STR', 'GABA', ['all'], conProb['FSI']['D1STR'], conEff['FSI']['D1STR'])
    camP(c, 'FSI', 'D2STR', 'GABA', ['all'], conProb['FSI']['D2STR'], conEff['FSI']['D2STR'])


    GPeP = makePop("GPeP", [[GABA, 2000, 2, 2],
                [AMPA, 800, config['GPeExtEff'],
                config['GPeExtFreq']], NMDA],
                cd_pre, {'N': 2500, 'g_T': 0.06, 'taum':10})
    camP(c, 'GPeP', 'GPeP', 'GABA', ['all'], conProb['GPeP']['GPeP'], conEff['GPeP']['GPeP'])
    camP(c, 'GPeP', 'STNE', 'GABA', ['syn'], conProb['GPeP']['STN'], conEff['GPeP']['STN'])
    camP(c, 'GPeP', 'GPi', 'GABA', ['syn'], conProb['GPeP']['GPi'], conEff['GPeP']['GPi'])


    STNE = makePop("STNE", [GABA,
                            [AMPA, 800, config['STNExtEff'],
                            config['STNExtFreq']], NMDA],
                            cd_pre, {'N': 2500, 'g_T': 0.06})
    camP(c, 'STNE', 'GPeP', ['AMPA', 'NMDA'], ['syn'], conProb['STN']['GPeP'], conEff['STN']['GPeP'])
    camP(c, 'STNE', 'GPi', 'NMDA', ['all'], conProb['STN']['GPi'], conEff['STN']['GPi'])


    GPi = makePop("GPi", [GABA,
                        [AMPA, 800, config['GPiExtEff'],
                        config['GPiExtFreq']], NMDA], cd_pre)
    camP(c, 'GPi', 'Th', 'GABA', ['syn'], conProb['GPi']['Th'], conEff['GPi']['Th'])


    Th = makePop('Th', [GABA,
                        [AMPA, 800, config['ThExtEff'],
                        config['ThExtFreq']], NMDA], cd_pre)
    camP(c, 'Th', 'D1STR', 'AMPA', ['syn'], conProb['Th']['STR'], conEff['Th']['STR'])
    camP(c, 'Th', 'D2STR', 'AMPA', ['syn'], conProb['Th']['STR'], conEff['Th']['STR'])
    camP(c, 'Th', 'FSI', 'AMPA', ['all'], conProb['Th']['FSI'], conEff['Th']['FSI'])
    camP(c, 'Th', 'LIP', 'NMDA', ['all'], conProb['Th']['Cx'], conEff['Th']['Cx'], name='thcx')

    ineuronPops = [FSI]

    if config['rampingCTX']:
        # print('ramping')
        camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['all'], .13, [0.0127, 0.15])
        camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], .0725, [0.013, 0.125])

        LIPI = makePop("LIPI", [GABA, [AMPA, 640, .6, 1.05], NMDA], cd_pre, { 'N': 620, 'C': 0.2, 'Taum': 10})
        camP(c, 'LIPI', 'LIP', 'GABA', ['all'], .5, 1.05)
        camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1.075)
        ineuronPops.append(LIPI)

        camP(c, 'Th', 'LIPI', 'NMDA', ['all'], conProb['Th']['CxI'], conEff['Th']['CxI'], name='thcxi')

    action_channel = makeChannel('choices', [GPi, STNE, GPeP, D1STR, D2STR, LIP, Th])

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

    random.seed(config['seed'] + int(config['d1aw']*100) + int(config['d2aw']*10000) + int(config['rewardprob']*1000000))

    hes = []
    houts = []
    for i in range(0,50):
        hes.append(makeHandleEvent('reset', 0, 'sensory', [], config['BaseStim']))
        hes.append(makeHandleEvent('wrong stimulus', config['Start'], 'sensory', [], config['WrongStim']))
        hes.append(makeHandleEvent('right stimulus', config['Start'], 'sensory', [0], config['RightStim']))
        #hes.append(makeHandleEvent('hyperdirect', config['Start'], 'threshold', [], config['STNExtFreq']+.75))
        #hes.append(makeHandleEvent('hyperdirect', config['Start'], 'threshold', [0], config['STNExtFreq']+.75))
        #hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial', 2, 0.1)) #Right reward 0.1
        #if random.uniform(0, 1) < config['rewardprob']:
        if i < 20:
            if random.uniform(0, 1) < 0.5:
                hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [0], config['Dynamic'], 'EndTrial', 1, 1.0)) #Left reward 1.0
                hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial', 2, 0.0)) #Right reward 0.0
                houts.append(makeHandleEvent('decision made', config['Start'], 'out', [0], config['Dynamic'], 'EndTrial'))
                houts.append(makeHandleEvent('decision made', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial'))
            else:
                hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial', 2, 0.0)) #Right reward 0.0
                hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [0], config['Dynamic'], 'EndTrial', 1, 1.0)) #Left reward 1.0
                houts.append(makeHandleEvent('decision made', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial'))
                houts.append(makeHandleEvent('decision made', config['Start'], 'out', [0], config['Dynamic'], 'EndTrial'))
        else:
            if random.uniform(0, 1) < 0.5:
                hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [0], config['Dynamic'], 'EndTrial', 1, 0.0)) #Left reward 0.0
                hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial', 2, 1.0)) #Right reward 1.0
                houts.append(makeHandleEvent('decision made', config['Start'], 'out', [0], config['Dynamic'], 'EndTrial'))
                houts.append(makeHandleEvent('decision made', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial'))
            else:
                hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial', 2, 1.0)) #Right reward 1.0
                hes.append(makeHandleEvent('dynamic cutoff', config['Start'], 'out', [0], config['Dynamic'], 'EndTrial', 1, 0.0)) #Left reward 0.0
                houts.append(makeHandleEvent('decision made', config['Start'], 'out', [1], config['Dynamic'], 'EndTrial'))
                houts.append(makeHandleEvent('decision made', config['Start'], 'out', [0], config['Dynamic'], 'EndTrial'))
        hes.append(makeHandleEvent('time limit', config['Start']+800, etype='EndTrial'))


        houts.append(makeHandleEvent('decision made', config['Start']+800, etype='EndTrial'))


    # timelimit = 1800
    timelimit = 1200

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
    #eventlist.append(makeEvent(timelimit, 'EndTrial'))

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
                            if df.at[i, tract['target']
                                     ] >= output['threshold']:
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
    lastrelevantevent = 0
    for e in range(firstrelevantevent, len(outevents)):
        handleevent = outevents[e]
        # print('he start ' + str(handleevent['time']))
        if len(outputs[handleevent['label']]) <= curstage:
            output = {'time': None,
                      'start': handleevent['time'],
                      'delay': None,
                      'pathvals': None,
                      'threshold': handleevent['freq']}
            outputs[handleevent['label']].append(output)
            # print('test ' + handleevent['label'])
        if e == lastrelevantevent and not (handleevent['etype'] == 'EndTrial' and handleevent['hname'] == ''):
            lastrelevantevent += 1
    lastrelevantevent += 1
    for i in range(0, df.shape[0]):
        curtime = df.at[i, 'Time (ms)']
        needsmorestaging = 0
        # print(firstrelevantevent, lastrelevantevent, curtime)
        for e in range(firstrelevantevent, lastrelevantevent):
            handleevent = outevents[e]
            output = outputs[handleevent['label']][curstage]
            if curtime < handleevent['time'] + stagestart:
                continue
            if handleevent['etype'] == 'EndTrial' and handleevent['hname'] == '':
                if curtime >= output['start'] + stagestart:
                    if output['time'] is None:
                        output['time'] = curtime
                    needsmorestaging = 1
                    # print('timeout triggered')
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
                                        # print('threshold triggered')
        if needsmorestaging == 1:
            curstage += 1
            stagestart = curtime
            firstrelevantevent = lastrelevantevent
            for e in range(firstrelevantevent, len(outevents)):
                # print(e)
                handleevent = outevents[e]
                if len(outputs[handleevent['label']]) <= curstage:
                    output = {'time': None,
                              'start': handleevent['time'],
                              'delay': None,
                              'pathvals': None,
                              'threshold': handleevent['freq']}
                    outputs[handleevent['label']].append(output)
                if e  == lastrelevantevent and not (handleevent['etype'] == 'EndTrial' and handleevent['hname'] == ''):
                    lastrelevantevent += 1
            lastrelevantevent += 1
    trialdata['outputs'] = outputs
    return outputs

def setDirectory(prefix='autotest'):
    global directoryprefix
    directoryprefix = os.path.join(os.path.expanduser('~'), prefix, 'sweeps')


def getDirectory(sweepnumber=0):
    return os.path.join(directoryprefix, str(sweepnumber))


def configureSweep(sc=0, **kwargs):
    config = getNetworkDefaults()
    config.update(kwargs)
    for key, value in kwargs.items():
        if isinstance(value, list):
            selected = {}
            selected.update(kwargs)
            for opt in value:
                selected[key] = opt
                sc = configureSweep(sc, **selected)
            return sc
    configureExperiment(**config)#kwargs)
    directory = getDirectory(sc)
    call('mkdir -p ' + directoryprefix, shell=True)
    call('mkdir -p ' + directory, shell=True)
    for filename in ['network.conf', 'network.pro', 'network.pickle']:
        call('mv ' + filename + ' ' + directory + '/' + filename, shell=True)
    return sc + 1

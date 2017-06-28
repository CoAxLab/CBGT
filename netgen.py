import random
from subprocess import call

# class PopChannel:
#     name = ""
#     dim = ""
#     subchannels = []
#     pops = []
#
# class Pop:
#     name = ""
#     preset = ""
#
# class Connection:
#     name = ""
#     source = ""
#     target = ""
#     preset = ""
#     pathways = []
#     contype = ""
#     connectivity = []
#     path = []


# break

# class NetPop:
#     name = ""
#     targets = []
#
# class Target:
#     targetname = ""

# def printFinal(network):
#     for popvalue in network:
#         print(popvalue['name'])
#         for targvalue in popvalue['targets']:
#             print("  " + targvalue['targetname'])
#
# network = [{'name':'middle', 'targets':[{'targetname':'left'}]}]
# printFinal(network)

# print(glblpg)

# def gendimadj(dims):
#     dimadj = {}
#     for k1, v1 in dims.items():
#         dimadj[k1] = {}
#         for k2, v2 in dims.items():
#             dimadj[k1][k2] = {}
#             adj = []
#             for dist1 in range(0, v1):
#                 adjrow = []
#                 for dist2 in range(0, v2):
#                     con = 0
#                     if k1 != k2:
#                         con = 1
#                     if k1 == k2 and dist1 == dist2:
#                         con = 1
#                     adjrow.append(con)
#                 adj.append(adjrow)
#             dimadj[k1][k2]['syn'] = adj
#             adj = []
#             for dist1 in range(0, v1):
#                 adjrow = []
#                 for dist2 in range(0, v2):
#                     con = 0
#                     if k1 == k2 and dist1 != dist2:
#                         con = 1
#                     adjrow.append(con)
#                 adj.append(adjrow)
#             dimadj[k1][k2]['anti'] = adj
#     return dimadj
#
# dimadj = gendimadj(dims)
#
# def printDimAdj(dimadj):
#     for k1, v1 in dimadj.items():
#         for k2, adj in v1.items():
#             print(k1)
#             print(k2)
#             for row in adj['syn']:
#                 print(row)
#
# printDimAdj(dimadj)
# print(dimadj)

# def lastCommon(path1, path2):
#     result = -1
#     while result + 1 < len(path1) and result + 1 < len(path2):
#         if path1[result + 1] == path2[result + 1]:
#             result = result + 1
#         else:
#             return result
#     return result

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
        STFT=0, STFP=0, name='', cmtype='con', conmatrix=[]):
    return {'src': src,
            'targ': targ,
            'name': name,
            'receptor': receptor,
            'connectivity': connectivity,
            'efficacy': efficacy,
            'STFT': STFT,
            'STFP': STFP,
            'preset': preset,
            'cmtype': cmtype,
            'conmatrix': conmatrix}


def camP(connections, src, targ, receptor, preset=['all'], connectivity=1,
        efficacy=1, STFT=0, STFP=0, name='', cmtype='con', conmatrix=[]):
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
                                    con, eff, STFT, STFP, name, cmtype, conmatrix))


def makeHandle(name, targ, path, receptor, con, eff, preset=['syn'], conmatrix=[]):
    return {'name': name,
            'targ': targ,
            'path': path,
            'receptor': receptor,
            'connectivity': con,
            'efficacy': eff,
            'STFT': 0,
            'STFP': 0,
            'preset': preset,
            'cmtype': 'con',
            'conmatrix': conmatrix}


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


def constructHandleCopies(dims, handlelist, poppaths, popcopylist):
    handles = []
    for handle in handlelist:
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
                    if tract['target'] == pop['uniquename']:
                        pop['receptors'][handlecopy['receptor']
                                         ]['MeanExtCon'] = tract['data']['Connectivity']
                        pop['receptors'][handlecopy['receptor']
                                         ]['MeanExtEff'] = tract['data']['MeanEff']
            handles.append(handlecopy)
    return handles


def constructEvents(time, label, hname, hpath, freq, handles, eventlist):
    for handle in handles:
        if handle['name'] == hname:
            valid = True
            for spec, val in zip(hpath, handle['pathvals']):
                if spec != -1 and spec != val:
                    valid = False
            if valid:
                for tract in handle['targets']:
                    event = makeEvent(time, 'ChangeExtFreq', label,
                                      tract['target'], tract['data']['TargetReceptor'], freq)
                    eventlist.append(event)

def transformScaling(scale, popcopylist, connections):
    for pop in popcopylist:
        pop['data']['N'] *= scale
    for path in connections:
        # scale C and then E only if needed
        # maybe some other form of balancing is better
        path['connectivity'] /= scale
        if path['connectivity'] > 1:
            path['efficacy'] *= path['connectivity']
            path['connectivity'] = 1


def printNetData(poppaths, popcopylist, handles):
    for handle in handles:
        print(handle)
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


def compileAndRun(trials=1):
    call('mkdir -p autotest', shell=True)
    call('gcc -o autotest/sim BG_inh_pathway_spedup.c rando2.h -lm', shell=True)
    call('mv network.conf autotest/network.conf', shell=True)
    call('mv network.pro autotest/network.pro', shell=True)
    for trial in range(0, trials):
        call('./sim -ns -n' + str(trial), shell=True, cwd='autotest')


def describeBG():
    c = []
    h = []

    cd_pre = {'N': 250,
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

    GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})

    SNr = makePop("SNr", [GABA, [AMPA, 800, 14, 1], NMDA], cd_pre)
    camP(c, 'SNr', 'E', 'GABA', ['syn'], 1, 2.5)
    STNE = makePop("STNE", [GABA, [AMPA, 800, 1.6, 5], NMDA], cd_pre,
                   {'N': 2500, 'g_T': 0.06})
    camP(c, 'STNE', 'GPe', ['AMPA', 'NMDA'], ['syn'], 0.05, [0.05, 2])
    camP(c, 'STNE', 'SNr', 'NMDA', ['syn'], 1, 0.06)
    GPe = makePop("GPe", [[GABA, 2000, 2, 1], [AMPA, 800, 3, 4], NMDA], cd_pre,
                  {'N': 2500, 'tauhm': 10, 'g_T': 0.01})
    camP(c, 'GPe', 'GPe', 'GABA', ['syn'], 0.05, 1.5)
    camP(c, 'GPe', 'STNE', 'GABA', ['syn'], 0.02, 0.6)
    camP(c, 'GPe', 'SNr', 'GABA', ['syn'], 1, 0.08)
    camP(c, 'GPe', 'CD', 'GABA', ['syn'], 1, 0.03)
    CD = makePop("CD", [GABA, [AMPA, 800, 4, 1], NMDA], cd_pre)
    camP(c, 'CD', 'CD', 'GABA', ['syn'], 1, 1)
    camP(c, 'CD', 'SNr', 'GABA', ['syn'], 1, 3)
    camP(c, 'CD', 'GPe', 'GABA', ['syn'], 1, 4)
    LIP = makePop("LIP", [GABA, [AMPA, 800, 2.1, 3],
                          NMDA], cd_pre, {'N': 240})
    camP(c, 'LIP', 'E', 'AMPA', ['syn'], 1, 3.5)
    camP(c, 'LIP', 'CD', 'AMPA', ['syn'], 1, 3.0)
    camP(c, 'LIP', 'LIPb', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['syn'], 1, [0.085, 0.2805])
    camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['anti'], 1, [0.043825, 0.14462])
    camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])
    E = makePop('E', [GABA, [AMPA, 800, 0.19, 1.6], NMDA],
                cd_pre, {'Alpha_ca': 2, 'Tau_ca': 200})
    camP(c, 'E', 'E', 'NMDA', ['syn'], 1, 1.5)
    camP(c, 'E', 'I0', 'NMDA', ['all'], 1, 0.7, 1000, 0.15)
    camP(c, 'E', 'LIPI', 'NMDA', ['all'], 1, 0.15)
    camP(c, 'E', 'LIP', 'NMDA', ['all'], 1, 0.05)
    action_channel = makeChannel('choices', [SNr, STNE, GPe, CD, LIP, E])

    I0 = makePop("I0", [GABA, [AMPA, 800, 2, 1.6], NMDA],
                 cd_pre, {'C': 0.2, 'Taum': 10})
    camP(c, 'I0', 'E', 'GABA', ['all'], 1, 2.5)
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
    brain = makeChannel('brain', [I0, LIPb, LIPI], [action_channel])

    return (brain, c, h)


def multichoiceExperiment(choices=1, trials=0):
    brain, connections, handlelist = describeBG()
    handlelist.append(makeHandle('sensory', 'LIP', ['choices'], 'AMPA', 800, 2.1))
    handlelist.append(makeHandle('cancel', 'STNE', ['choices'], 'AMPA', 800, 1.6))

    dims = {'brain': 1, 'choices': choices}

    poppaths = constructPopPaths(brain)
    popcopylist = constructPopCopies(dims, brain, poppaths)
    transformScaling(1, popcopylist, connections)

    handles = constructHandleCopies(dims, handlelist, poppaths, popcopylist)
    constructConnections(dims, connections, poppaths, popcopylist)

    eventlist = []
    constructEvents(0, 'reset', 'sensory', [], 3, handles, eventlist)
    constructEvents(100, 'wrong stimulus', 'sensory',
                    [], 3.0372, handles, eventlist)
    constructEvents(100, 'right stimulus', 'sensory',
                    [0], 3.0884, handles, eventlist)
    # constructEvents(550, 'abort signal', 'cancel',
    #                 [0], 20, handles, eventlist)
    eventlist.append(makeEvent(800, 'EndTrial'))

    printNetData(poppaths, popcopylist, handles)
    writeCsv(popcopylist)
    writeConf(popcopylist)
    writePro(eventlist)

    compileAndRun(trials)


# STNE = makePop('STNE', [GABA, [AMPA, 800, 1, 4], NMDA], cd_pre, {'N':2500, 'g_T':0.06})
# camP(c,'STNE', 'GPeI', 'AMPA', ['syn'], 0.05, 0.05)
# camP(c,'STNE', 'GPeI', 'NMDA', ['syn'], 0.05, 10)
# GPeI = makePop('GPeI', [[GABA,2500,22,1], [AMPA, 800, 1.6, 5], NMDA], cd_pre, {'N':2500, 'g_T':0.06})
# camP(c,'GPeI', 'GPeI', 'GABA', ['syn'], 0.05, 0.02)
# camP(c,'GPeI', 'STNE', 'GABA', ['syn'], 0.02, 10)
# brain = makeChannel('brain', [GPeI, STNE])


# for row in bg_in['conmatrix']:
#     print(row)

multichoiceExperiment(2, 1)

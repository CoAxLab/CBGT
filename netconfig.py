#!usr/bin/env python

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

    config = {'STNExtEff': 1.6,
              'GPiExtEff': 6.,
              'CxD1STR': .75,
              'CxD2STR': .75,
              'CxSTN': .5}
    c, h = [], []
    config.update(kwargs)
    cd_pre = getCellDefaults()

    GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})

    GPi = makePop("GPi", [GABA, [AMPA, 800,  config['GPiExtEff'], 0.8], NMDA], cd_pre)
    camP(c, 'GPi', 'Th', 'GABA', ['syn'], 1, 0.09)

    STNE = makePop("STNE", [GABA, [AMPA, 800, config['STNExtEff'], 4], NMDA], cd_pre,
                   {'N': 2500, 'g_T': 0.06})
    camP(c, 'STNE', 'GPe', ['AMPA', 'NMDA'], ['syn'], 0.05, [0.05, 2])
    camP(c, 'STNE', 'GPi', 'NMDA', ['all'], 1, 0.03)

    GPe = makePop("GPe", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 4], NMDA], cd_pre,
                  {'N': 2500, 'tauhm': 10, 'g_T': 0.01})
    camP(c, 'GPe', 'GPe', 'GABA', ['syn'], 0.05, 1.5)
    camP(c, 'GPe', 'STNE', 'GABA', ['syn'], 0.02, 0.8)
    camP(c, 'GPe', 'GPi', 'GABA', ['syn'], 1, 0.04)
    # camP(c, 'GPe', 'D1STR', 'GABA', ['all'], 1, 0.03, name='arkipallidal')
    # camP(c, 'GPe', 'D2STR', 'GABA', ['all'], 1, 0.03, name='arkipallidal')

    D1STR = makePop("D1STR", [GABA, [AMPA, 800, 4, 1.6], NMDA], cd_pre)
    camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], 1, 1)
    camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], 1, 2.4, name='direct')

    D2STR = makePop("D2STR", [GABA, [AMPA, 800, 4, 1.6], NMDA], cd_pre)
    camP(c, 'D2STR', 'D2STR', 'GABA', ['syn'], 1, 1)
    camP(c, 'D2STR', 'GPe', 'GABA', ['syn'], 1, 3, name='indirect')


    LIP = makePop("LIP", [GABA, [AMPA, 800, 2.1, 3],
                          NMDA], cd_pre, {'N': 240})
    # camP(c, 'LIP', 'Th', 'AMPA', ['syn'], 1, 0)
    camP(c, 'LIP', 'D1STR', 'AMPA', ['syn'], 1, config['CxD1STR'], name='cxd')
    camP(c, 'LIP', 'D2STR', 'AMPA', ['syn'], 1, config['CxD2STR'], name='cxi')
    # camP(c, 'LIP', 'STNE', 'AMPA', ['syn'], 1, config['CxSTN'])

    camP(c, 'LIP', 'LIPb', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['syn'], 1, [0.085, 0.2805])
    camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['anti'], 1, [0.043825, 0.14462])
    camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])

    # M1 = makePop("M1", [GABA, [AMPA, 800, 2.0, 3],
    #                     NMDA], cd_pre, {'N': 240})
    # camP(c, 'M1', 'Th', 'AMPA', ['syn'], 1, 0.2)
    # camP(c, 'M1', 'D1STR', 'AMPA', ['syn'], 1, config['CxSTR'])
    # camP(c, 'M1', 'D2STR', 'AMPA', ['syn'], 1, config['CxSTR'])

    Th = makePop('Th', [GABA, [AMPA, 800, 2, 3.2], NMDA], cd_pre)
    # camP(c, 'Th', 'Th', 'NMDA', ['syn'], 1, 1.5)
    # camP(c, 'Th', 'LIPI', 'NMDA', ['all'], 1, 0.32, STDP=0.45, STDT=600)
    camP(c, 'Th', 'LIP', 'NMDA', ['syn'], 1, 0.32, STDP=0.45, STDT=600)

    action_channel = makeChannel('choices', [GPi, STNE, GPe, D1STR, D2STR, LIP, Th])

    LIPb = makePop("LIPb", [GABA, [AMPA, 800, 2.1, 3], NMDA], cd_pre, {'N': 1120})
    camP(c, 'LIPb', 'LIPb', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    camP(c, 'LIPb', 'LIP', ['AMPA', 'NMDA'], ['all'], 1, [0.043825, 0.14462])
    camP(c, 'LIPb', 'LIPI', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])

    LIPI = makePop("LIPI", [GABA, [AMPA, 800, 1.62, 3], NMDA], cd_pre, {'N': 400, 'C': 0.2, 'Taum': 10})
    camP(c, 'LIPI', 'LIPb', 'GABA', ['all'], 1, 1.3)
    camP(c, 'LIPI', 'LIP', 'GABA', ['all'], 1, 1.3)
    camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1)

    brain = makeChannel('brain', [LIPb, LIPI], [action_channel])

    return (brain, c, h)


def describeSubcircuit(**kwargs):
    c, h = [], []
    cd_pre = getCellDefaults()
    GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})

    STNE = makePop('STNE', [GABA, [AMPA, 800, 1, 4], NMDA],
                   cd_pre, {'N': 2500, 'g_T': 0.06})
    camP(c, 'STNE', 'GPeI', 'AMPA', ['syn'], 0.05, 0.05)
    camP(c, 'STNE', 'GPeI', 'NMDA', ['syn'], 0.05, 10)
    GPeI = makePop('GPeI', [[GABA, 2500, 22, 1], [AMPA, 800, 1.6, 5], NMDA], cd_pre, {'N': 2500, 'g_T': 0.06})
    camP(c, 'GPeI', 'GPeI', 'GABA', ['syn'], 0.05, 0.02)
    camP(c, 'GPeI', 'STNE', 'GABA', ['syn'], 0.02, 10)
    brain = makeChannel('brain', [GPeI, STNE])
    return (brain, c, h)


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

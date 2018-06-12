

def describeBG(**kwargs):

    config = {'STNExtEff': 1.7,
              'GPiExtEff': 6.0,
              'CxSTR': 0.5,
              'M1STR': 0.5,
              'CxTh': 0.2,
              'STNExtFreq': 4.0,
              'rampingCTX': False}

    config.update(kwargs)
    c = []; h = []
    cd_pre = getCellDefaults()
    GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})

    # makePop(name,
    #       receptorList=[[R1, ExtCon1, ExtEff1, FreqExt1],
    #                     R2, ExtCon2, ExtEff2, FreqExt2]]
    #       cd_pre)

    # camP(connections, src, targ, receptor, preset=['all'],
    #       connectivity=1, efficacy=1, STFT=0, STFP=0,
    #       STDT=0, STDP=0, name='', cmtype='eff', conmatrix=[])

    LIP = makePop("LIP", [GABA, [AMPA, 800, 2.85, 2.2], NMDA], cd_pre, {'N': 680})
    camP(c, 'LIP', 'D1STR', ['AMPA', 'NMDA'], ['syn'], 0.5, [config['CxSTR'], config['CxSTR']*1.1], name='cxd')
    camP(c, 'LIP', 'D2STR',  ['AMPA', 'NMDA'], ['syn'], 0.5, [config['CxSTR'], config['CxSTR']*1.1], name='cxi')
    camP(c, 'LIP', 'FSI', 'AMPA', ['all'], 0.5, config['CxFSI'], name='cxfsi')
    camP(c, 'LIP', 'Th', ['AMPA', 'NMDA'], ['all'], 0.35, [config['CxTh'], config['CxTh']])

    D1STR = makePop("D1STR", [GABA, [AMPA, 800, 3.8, 1.29], NMDA], cd_pre)
    camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], .14, .25)
    camP(c, 'D1STR', 'D2STR', 'GABA', ['syn'], .14, .25)
    camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], .55, 1., name='direct')

    D2STR = makePop("D2STR", [GABA, [AMPA, 800, 3.8, 1.29], NMDA], cd_pre)
    camP(c, 'D2STR', 'D2STR', 'GABA', ['syn'], .14, .25)
    camP(c, 'D2STR', 'D1STR', 'GABA', ['syn'], .16, .25)
    camP(c, 'D2STR', 'GPeP', 'GABA', ['syn'], .7, 1.74, name='indirect')

    FSI = makePop("FSI", [GABA, [AMPA, 800, 1.5, 3.], NMDA], cd_pre, {'C': 0.2, 'Taum': 10})
    camP(c, 'FSI', 'FSI', 'GABA', ['all'], .8, 1.08)
    camP(c, 'FSI', 'D1STR', 'GABA', ['all'], .66, 1.215)
    camP(c, 'FSI', 'D2STR', 'GABA', ['all'], .64, 1.215)

    # GPeP = makePop("GPeP", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 5], NMDA],
                    # cd_pre, {'N': 2000, 'tauhm': 10, 'g_T': 0.01})
    GPeP = makePop("GPeP", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 5], NMDA],
                    cd_pre, {'N': 2000, 'g_T': 0.06})
    camP(c, 'GPeP', 'GPeP', 'GABA', ['all'], 0.02, 1.5)
    camP(c, 'GPeP', 'STNE', 'GABA', ['syn'], 0.02, 0.4)
    camP(c, 'GPeP', 'GPi', 'GABA', ['syn'], 1, 0.0122)

    # STNE = makePop("STNE", [GABA, [AMPA, 800, config['STNExtEff'],
                # config['STNExtFreq']], NMDA], cd_pre, {'N': 2000, 'g_T': 0.03})
    STNE = makePop("STNE", [GABA, [AMPA, 800, config['STNExtEff'],
                config['STNExtFreq']], NMDA], cd_pre, {'N': 2000, 'g_T': 0.06})
    camP(c, 'STNE', 'GPeP', ['AMPA', 'NMDA'], ['syn'], 0.0485, [0.07, 4])
    camP(c, 'STNE', 'GPi', 'NMDA', ['all'], 1, 0.0315)

    GPi = makePop("GPi", [ GABA, [AMPA, 800, config['GPiExtEff'], 0.8], NMDA], cd_pre)
    camP(c, 'GPi', 'Th', 'GABA', ['syn'], .9, 0.0715)

    Th = makePop('Th', [GABA, [AMPA, 800, 2.56, 2.22], NMDA], cd_pre)
    camP(c, 'Th', 'D1STR', 'AMPA', ['all'], 0.35, config['ThSTR'])
    camP(c, 'Th', 'D2STR', 'AMPA', ['all'], 0.35, config['ThSTR'])
    # camP(c, 'Th', 'FSI', 'AMPA', ['all'], 0.15, config['ThSTR']/1.65)
    camP(c, 'Th', 'LIP', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcx')

    action_channel = makeChannel('choices',[GPi,STNE,GPeP,D1STR,D2STR,LIP,Th])
    ineuronPops = [FSI]

    if config['rampingCTX']:
        camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['all'], .135, [0.018, 0.15])
        camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], .05, [0.021, 0.09])
        LIPI = makePop("LIPI", [GABA, [AMPA, 800, 1.15, 3], NMDA], cd_pre, { 'N': 480, 'C': 0.2, 'Taum': 10})
        camP(c, 'LIPI', 'LIP', 'GABA', ['all'], .57, 1.07)
        camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1.075)
        camP(c, 'Th', 'LIPI', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcxi')
        ineuronPops.append(LIPI)

    brain = makeChannel('brain', ineuronPops, [action_channel])
    return (brain, c, h)

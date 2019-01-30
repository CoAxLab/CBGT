
# def describeBG(**kwargs):
#
#     config = {'STNExtEff': 1.7,
#               'GPiExtEff': 6.0,
#               'CxSTR': 0.5,
#               'M1STR': 0.5,
#               'CxTh': 0.2,
#               'STNExtFreq': 4.0,
#               'rampingCTX': False}
#
#     # makePop(name, receptors=[], data={}, data_overrides={})
#
#     # camP(connections, src, targ, receptor, preset=['all'], connectivity=1,
#     #       efficacy=1, STFT=0, STFP=0, STDT=0, STDP=0, name='', cmtype='eff', conmatrix=[])
#
#
#
#     config.update(kwargs)
#     c = []
#     h = []
#     cd_pre = getCellDefaults()
#     GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
#     AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
#     NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})
#
#     LIP = makePop("LIP", [GABA, [AMPA, 800, 2.8, 2.2], NMDA], cd_pre, {'N': 680})
#
#     camP(c, 'LIP', 'D1STR', ['AMPA', 'NMDA'], ['syn'], 0.5, [config['CxSTR'], config['CxSTR']*1.05], name='cxd')
#     camP(c, 'LIP', 'D2STR',  ['AMPA', 'NMDA'], ['syn'], 0.5, [config['CxSTR'], config['CxSTR']*1.05], name='cxi')
#     camP(c, 'LIP', 'FSI', 'AMPA', ['all'], 0.5, config['CxFSI'], name='cxfsi')
#     camP(c, 'LIP', 'Th', ['AMPA', 'NMDA'], ['all'], 0.35, [config['CxTh'], config['CxTh']])
#
#     D1STR = makePop("D1STR", [GABA, [AMPA, 800, 4.05, 1.3], NMDA], cd_pre)
#     camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], .14, .28)
#     camP(c, 'D1STR', 'D2STR', 'GABA', ['syn'], .14, .28)
#     camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], .55, .9, name='direct')
#
#     D2STR = makePop("D2STR", [GABA, [AMPA, 800, 4.05, 1.3], NMDA], cd_pre)
#     camP(c, 'D2STR', 'D2STR', 'GABA', ['syn'], .14, .28)
#     camP(c, 'D2STR', 'D1STR', 'GABA', ['syn'], .16, .30)
#     camP(c, 'D2STR', 'GPeP', 'GABA', ['syn'], .7, 1.72, name='indirect')
#
#     FSI = makePop("FSI", [GABA, [AMPA, 800, 1.5, 3.], NMDA], cd_pre, {'C': 0.2, 'Taum': 10})
#     camP(c, 'FSI', 'FSI', 'GABA', ['all'], .85, 1.05)
#     camP(c, 'FSI', 'D1STR', 'GABA', ['all'], .74, 1.22)
#     camP(c, 'FSI', 'D2STR', 'GABA', ['all'], .7, 1.205)
#
#     GPeP = makePop("GPeP", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 5], NMDA],
#                     cd_pre, {'N': 2500, 'tauhm': 10, 'g_T': 0.06})
#     camP(c, 'GPeP', 'GPeP', 'GABA', ['all'], 0.02, 1.5)
#     camP(c, 'GPeP', 'STNE', 'GABA', ['syn'], 0.02, 0.4)
#     camP(c, 'GPeP', 'GPi', 'GABA', ['syn'], 1, 0.0122)
#
#     STNE = makePop("STNE", [GABA, [AMPA, 800, config['STNExtEff'],
#                 config['STNExtFreq']], NMDA], cd_pre, {'N': 2500, 'g_T': 0.06})
#     camP(c, 'STNE', 'GPeP', ['AMPA', 'NMDA'], ['syn'], 0.0485, [0.07, 4])
#     camP(c, 'STNE', 'GPi', 'NMDA', ['all'], 1, 0.03125)
#
#     GPi = makePop("GPi", [ GABA, [AMPA, 800, config['GPiExtEff'], 0.8], NMDA], cd_pre)
#     camP(c, 'GPi', 'Th', 'GABA', ['syn'], .95, 0.07)
#
#     Th = makePop('Th', [GABA, [AMPA, 800, 2.65, 2.328], NMDA], cd_pre)
#     camP(c, 'Th', 'D1STR', 'AMPA', ['all'], 0.5, config['ThSTR'])
#     camP(c, 'Th', 'D2STR', 'AMPA', ['all'], 0.5, config['ThSTR'])
#     camP(c, 'Th', 'FSI', 'AMPA', ['all'], 0.25, config['ThSTR']/1.25)
#     camP(c, 'Th', 'LIP', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcx')
#     action_channel = makeChannel('choices', [GPi, STNE, GPeP, D1STR, D2STR, LIP, Th])
#
#     ineuronPops = [FSI]
#
#     if config['rampingCTX']:
#         camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['all'], .15, [0.02, 0.15])
#         camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], .07, [0.024, 0.12])
#
#         LIPI = makePop("LIPI", [GABA, [AMPA, 800, 1.0, 3], NMDA], cd_pre, { 'N': 450, 'C': 0.2, 'Taum': 10})
#         camP(c, 'LIPI', 'LIP', 'GABA', ['all'], .6, 1.05)
#         camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1.075)
#         camP(c, 'Th', 'LIPI', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcxi')
#         ineuronPops.append(LIPI)
#
#     brain = makeChannel('brain', ineuronPops, [action_channel])
#
#     return (brain, c, h)
#
#
#
#
# def describeBG(**kwargs):
#
#     config = {'STNExtEff': 1.7,
#               'GPiExtEff': 6.0,
#               'CxSTR': 0.5,
#               'M1STR': 0.5,
#               'CxTh': 0.2,
#               'STNExtFreq': 4.0,
#               'rampingCTX': False}
#
#     # makePop(name, receptors=[], data={}, data_overrides={})
#
#     # camP(connections, src, targ, receptor, preset=['all'], connectivity=1,
#     #       efficacy=1, STFT=0, STFP=0, STDT=0, STDP=0, name='', cmtype='eff', conmatrix=[])
#
#
#
#     config.update(kwargs)
#     c = []
#     h = []
#     cd_pre = getCellDefaults()
#     GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
#     AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
#     NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})
#
#     LIP = makePop("LIP", [GABA, [AMPA, 800, 2.8, 2.2], NMDA], cd_pre, {'N': 680})
#
#     camP(c, 'LIP', 'D1STR', ['AMPA', 'NMDA'], ['syn'], 0.5, [config['CxSTR'], config['CxSTR']*1.05], name='cxd')
#     camP(c, 'LIP', 'D2STR',  ['AMPA', 'NMDA'], ['syn'], 0.5, [config['CxSTR'], config['CxSTR']*1.05], name='cxi')
#     camP(c, 'LIP', 'FSI', 'AMPA', ['all'], 0.5, config['CxFSI'], name='cxfsi')
#     camP(c, 'LIP', 'Th', ['AMPA', 'NMDA'], ['all'], 0.35, [config['CxTh'], config['CxTh']])
#
#     D1STR = makePop("D1STR", [GABA, [AMPA, 800, 4., 1.3], NMDA], cd_pre)
#     camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], .175, .28)
#     camP(c, 'D1STR', 'D2STR', 'GABA', ['syn'], .175, .28)
#     camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], .6, .90, name='direct')
#
#     D2STR = makePop("D2STR", [GABA, [AMPA, 800, 4., 1.3], NMDA], cd_pre)
#     camP(c, 'D2STR', 'D2STR', 'GABA', ['syn'], .175, .28)
#     camP(c, 'D2STR', 'D1STR', 'GABA', ['syn'], .20, .28)
#     camP(c, 'D2STR', 'GPeP', 'GABA', ['syn'], .7, 1.72, name='indirect')
#
#     FSI = makePop("FSI", [GABA, [AMPA, 800, 1.5, 3.], NMDA], cd_pre, {'C': 0.2, 'Taum': 10})
#     camP(c, 'FSI', 'FSI', 'GABA', ['all'], .85, 1.05)
#     camP(c, 'FSI', 'D1STR', 'GABA', ['all'], .73, 1.25)
#     camP(c, 'FSI', 'D2STR', 'GABA', ['all'], .7, 1.25)
#
#     GPeP = makePop("GPeP", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 5], NMDA],
#                     cd_pre, {'N': 2500, 'tauhm': 10, 'g_T': 0.06})
#     camP(c, 'GPeP', 'GPeP', 'GABA', ['all'], 0.02, 1.5)
#     camP(c, 'GPeP', 'STNE', 'GABA', ['syn'], 0.02, 0.4)
#     camP(c, 'GPeP', 'GPi', 'GABA', ['syn'], 1, 0.0122)
#
#     STNE = makePop("STNE", [GABA, [AMPA, 800, config['STNExtEff'],
#                 config['STNExtFreq']], NMDA], cd_pre, {'N': 2500, 'g_T': 0.06})
#     camP(c, 'STNE', 'GPeP', ['AMPA', 'NMDA'], ['syn'], 0.0485, [0.07, 4])
#     camP(c, 'STNE', 'GPi', 'NMDA', ['all'], 1, 0.0315)
#
#     GPi = makePop("GPi", [ GABA, [AMPA, 800, config['GPiExtEff'], 0.8], NMDA], cd_pre)
#     camP(c, 'GPi', 'Th', 'GABA', ['syn'], .85, 0.07)
#
#     Th = makePop('Th', [GABA, [AMPA, 800, 2.52, 2.4], NMDA], cd_pre)
#     camP(c, 'Th', 'D1STR', 'AMPA', ['all'], 0.5, config['ThSTR'])
#     camP(c, 'Th', 'D2STR', 'AMPA', ['all'], 0.5, config['ThSTR'])
#     camP(c, 'Th', 'FSI', 'AMPA', ['all'], 0.25, config['ThSTR']/1.25)
#     camP(c, 'Th', 'LIP', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcx')
#     camP(c, 'Th', 'LIPI', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcxi')
#     action_channel = makeChannel('choices', [GPi, STNE, GPeP, D1STR, D2STR, LIP, Th])
#
#     ineuronPops = [FSI]
#
#     if config['rampingCTX']:
#         camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['all'], .15, [0.018, 0.15])
#         camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], .07, [0.014, 0.13])
#
#         LIPI = makePop("LIPI", [GABA, [AMPA, 800, 1., 3], NMDA], cd_pre, { 'N': 580, 'C': 0.2, 'Taum': 10})
#         camP(c, 'LIPI', 'LIP', 'GABA', ['all'], .6, 1.05)
#         camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1.075)
#
#         ineuronPops.append(LIPI)
#
#     brain = makeChannel('brain', ineuronPops, [action_channel])
#
#     return (brain, c, h)

#
# def describeBG(**kwargs):
#
#     config = {'STNExtEff': 1.7,
#               'GPiExtEff': 6.0,
#               'CxSTR': 0.5,
#               'M1STR': 0.5,
#               'CxTh': 0.2,
#               'STNExtFreq': 4.0,
#               'rampingCTX': False}
#
#     # makePop(name, receptors=[], data={}, data_overrides={})
#
#     # camP(connections, src, targ, receptor, preset=['all'], connectivity=1,
#     #       efficacy=1, STFT=0, STFP=0, STDT=0, STDP=0, name='', cmtype='eff', conmatrix=[])
#
#
#     config.update(kwargs)
#     c = []
#     h = []
#     cd_pre = getCellDefaults()
#     GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
#     AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
#     NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})
#
#     LIP = makePop("LIP", [GABA, [AMPA, 800, 2.85, 2.2], NMDA], cd_pre, {'N': 680})
#
#     camP(c, 'LIP', 'D1STR', ['AMPA', 'NMDA'], ['syn'], 0.5, [config['CxSTR'], config['CxSTR']*1.05], name='cxd')
#     camP(c, 'LIP', 'D2STR',  ['AMPA', 'NMDA'], ['syn'], 0.5, [config['CxSTR'], config['CxSTR']*1.05], name='cxi')
#     camP(c, 'LIP', 'FSI', 'AMPA', ['all'], 0.5, config['CxFSI'], name='cxfsi')
#     camP(c, 'LIP', 'Th', ['AMPA', 'NMDA'], ['all'], 0.35, [config['CxTh'], config['CxTh']])
#
#     D1STR = makePop("D1STR", [GABA, [AMPA, 800, 4., 1.3], NMDA], cd_pre)
#     camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], .1, .06)
#     camP(c, 'D1STR', 'D2STR', 'GABA', ['syn'], .1, .06)
#     camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], .5, 1.0, name='direct')
#
#     D2STR = makePop("D2STR", [GABA, [AMPA, 800, 4., 1.3], NMDA], cd_pre)
#     camP(c, 'D2STR', 'D2STR', 'GABA', ['syn'], .1, .06)
#     camP(c, 'D2STR', 'D1STR', 'GABA', ['syn'], .11, .06)
#     camP(c, 'D2STR', 'GPeP', 'GABA', ['syn'], .8, 1.725, name='indirect')
#
#     FSI = makePop("FSI", [GABA, [AMPA, 800, 1.5, 3.], NMDA], cd_pre, {'C': 0.2, 'Taum': 10})
#     camP(c, 'FSI', 'FSI', 'GABA', ['all'], .85, 1.1)
#     camP(c, 'FSI', 'D1STR', 'GABA', ['all'], .7, 1.32)
#     camP(c, 'FSI', 'D2STR', 'GABA', ['all'], .68, 1.32)
#
#     GPeP = makePop("GPeP", [[GABA, 2500, 2, 2], [AMPA, 800, 2, 5], NMDA],
#                     cd_pre, {'N': 2000,  'g_T': 0.06})
#     camP(c, 'GPeP', 'GPeP', 'GABA', ['all'], 0.02, 1.5)
#     camP(c, 'GPeP', 'STNE', 'GABA', ['syn'], 0.02, 0.4)
#     camP(c, 'GPeP', 'GPi', 'GABA', ['syn'], 1, 0.0122)
#
#     STNE = makePop("STNE", [GABA, [AMPA, 800, config['STNExtEff'],
#                 config['STNExtFreq']], NMDA], cd_pre, {'N': 2000, 'g_T': 0.06})
#     camP(c, 'STNE', 'GPeP', ['AMPA', 'NMDA'], ['syn'], 0.0485, [0.07, 4])
#     camP(c, 'STNE', 'GPi', 'NMDA', ['all'], .9, 0.0325)
#
#     GPi = makePop("GPi", [ GABA, [AMPA, 800, config['GPiExtEff'], 0.8], NMDA], cd_pre)
#     camP(c, 'GPi', 'Th', 'GABA', ['syn'], .85, 0.09)
#
#     Th = makePop('Th', [GABA, [AMPA, 800, 2.7, 2.3], NMDA], cd_pre)
#     camP(c, 'Th', 'D1STR', 'AMPA', ['all'], 0.5, config['ThSTR'])
#     camP(c, 'Th', 'D2STR', 'AMPA', ['all'], 0.5, config['ThSTR'])
#     camP(c, 'Th', 'FSI', 'AMPA', ['all'], 0.25, config['ThSTR']/1.5)
#     camP(c, 'Th', 'LIP', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcx')
#     action_channel = makeChannel('choices', [GPi, STNE, GPeP, D1STR, D2STR, LIP, Th])
#
#     ineuronPops = [FSI]
#
#     if config['rampingCTX']:
#         camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['all'], .145, [0.0127, 0.14])
#         camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], .07, [0.02, 0.09])
#         LIPI = makePop("LIPI", [GABA, [AMPA, 800, 1.15, 1], NMDA], cd_pre, { 'N': 420, 'C': 0.2, 'Taum': 10})
#         camP(c, 'LIPI', 'LIP', 'GABA', ['all'], .46, 1.075)
#         camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1.075)
#         camP(c, 'Th', 'LIPI', 'NMDA', ['all'], 0.25, config['ThCx'], name='thcxi')
#         ineuronPops.append(LIPI)
#
#     brain = makeChannel('brain', ineuronPops, [action_channel])
#     return (brain, c, h)



# def describeSubcircuit(**kwargs):
#     c = []
#     h = []
#
#     cd_pre = getCellDefaults()
#
#     GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
#     AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
#     NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})
#
#     STNE = makePop('STNE', [GABA, [AMPA, 800, 1, 4], NMDA], cd_pre, {'N': 2500, 'g_T': 0.06})
#     camP(c, 'STNE', 'GPeI', 'AMPA', ['syn'], 0.05, 0.05)
#     camP(c, 'STNE', 'GPeI', 'NMDA', ['syn'], 0.05, 10)
#     GPeI = makePop('GPeI', [[GABA, 2500, 22, 1], [AMPA, 800, 1.6, 5], NMDA], cd_pre, {'N': 2500, 'g_T': 0.06})
#     camP(c, 'GPeI', 'GPeI', 'GABA', ['syn'], 0.05, 0.02)
#     camP(c, 'GPeI', 'STNE', 'GABA', ['syn'], 0.02, 10)
#     brain = makeChannel('brain', [GPeI, STNE])
#     return (brain, c, h)

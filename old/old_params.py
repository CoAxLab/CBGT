
    #
    # config = {'STNExtEff': 1.6,
    #           'GPiExtEff': 6,
    #           'CxSTR': 0.5}
    #
    # config.update(kwargs)
    #
    # c = []
    # h = []
    #
    # cd_pre = getCellDefaults()
    #
    # GABA = makeReceptor('GABA', {'Tau': 5, 'RevPot': -70})
    # AMPA = makeReceptor('AMPA', {'Tau': 2, 'RevPot': 0})
    # NMDA = makeReceptor('NMDA', {'Tau': 100, 'RevPot': 0})
    #
    # GPi = makePop(
    #     "GPi", [
    #         GABA, [
    #             AMPA, 800, config['GPiExtEff'], 0.8], NMDA], cd_pre)
    # camP(c, 'GPi', 'Th', 'GABA', ['syn'], 1, 0.09)
    # STNE = makePop("STNE", [GABA, [AMPA, 800, config['STNExtEff'], 4], NMDA], cd_pre,
    #                {'N': 2500, 'g_T': 0.06})
    # camP(c, 'STNE', 'GPe', ['AMPA', 'NMDA'], ['syn'], 0.05, [0.05, 2])
    # camP(c, 'STNE', 'GPi', 'NMDA', ['all'], 1, 0.03)
    # GPe = makePop("GPe", [[GABA, 2000, 2, 2], [AMPA, 800, 2, 4], NMDA], cd_pre,
    #               {'N': 2500, 'tauhm': 10, 'g_T': 0.01})
    # camP(c, 'GPe', 'GPe', 'GABA', ['syn'], 0.05, 1.5)
    # camP(c, 'GPe', 'STNE', 'GABA', ['syn'], 0.02, 0.8)
    # camP(c, 'GPe', 'GPi', 'GABA', ['syn'], 1, 0.04)
    # camP(c, 'GPe', 'FSI', 'GABA', ['syn'], 1, 0.03, name='arkipallidal')
    # D1STR = makePop("D1STR", [GABA, [AMPA, 800, 4, 1.6], NMDA], cd_pre)
    # camP(c, 'D1STR', 'D1STR', 'GABA', ['syn'], 1, 1)
    # camP(c, 'D1STR', 'GPi', 'GABA', ['syn'], 1, 2.64, name='direct')
    # D2STR = makePop("D2STR", [GABA, [AMPA, 800, 4, 1.6], NMDA], cd_pre)
    # camP(c, 'D2STR', 'D2STR', 'GABA', ['syn'], 1, 1)
    # camP(c, 'D2STR', 'GPe', 'GABA', ['syn'], 1, 3.3, name='indirect')
    # FSI = makePop("FSI", [GABA, [AMPA, 800, 4, 1.6], NMDA], cd_pre)
    # camP(c, 'FSI', 'FSI', 'GABA', ['syn'], 1, 1)
    # camP(c, 'FSI', 'D1STR', 'GABA', ['syn'], 1, 1)
    # camP(c, 'FSI', 'D2STR', 'GABA', ['syn'], 1, 1)
    # LIP = makePop("LIP", [GABA, [AMPA, 800, 2.0, 3],
    #                       NMDA], cd_pre, {'N': 240})
    # camP(c, 'LIP', 'D1STR', 'AMPA', ['syn'], 0.5, config['CxSTR'])
    # camP(c, 'LIP', 'D2STR', 'AMPA', ['syn'], 0.5, config['CxSTR'])
    # camP(c, 'LIP', 'LIPb', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    # camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['syn'], 1, [0.085, 0.2805])
    # camP(c, 'LIP', 'LIP', ['AMPA', 'NMDA'], ['anti'], 1, [0.043825, 0.14462])
    # camP(c, 'LIP', 'LIPI', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])
    # M1 = makePop("M1", [GABA, [AMPA, 800, 2.0, 3],
    #                     NMDA], cd_pre, {'N': 240})
    # camP(c, 'M1', 'Th', 'AMPA', ['syn'], 1, 0.2)
    # camP(c, 'M1', 'D1STR', 'AMPA', ['syn'], 1, config['CxSTR'])
    # camP(c, 'M1', 'D2STR', 'AMPA', ['syn'], 1, config['CxSTR'])
    # camP(c, 'M1', 'M1b', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    # camP(c, 'M1', 'M1', ['AMPA', 'NMDA'], ['syn'], 1, [0.085, 0.2805])
    # camP(c, 'M1', 'M1', ['AMPA', 'NMDA'], ['anti'], 1, [0.043825, 0.14462])
    # camP(c, 'M1', 'M1I', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])
    # Th = makePop('Th', [GABA, [AMPA, 800, 2, 3.2], NMDA],
    #              cd_pre)
    # # camP(c, 'Th', 'Th', 'NMDA', ['syn'], 1, 1.5)
    # # camP(c, 'Th', 'LIPI', 'NMDA', ['all'], 1, 0.32, STDP=0.45, STDT=600)
    # camP(c, 'Th', 'M1', 'NMDA', ['syn'], 1, 0.32, STDP=0.45, STDT=600)
    # camP(c, 'Th', 'D1STR', 'AMPA', ['syn'], 0.5, config['CxSTR']/2)
    # camP(c, 'Th', 'D2STR', 'AMPA', ['syn'], 0.5, config['CxSTR']/2)
    # action_channel = makeChannel(
    #     'choices', [GPi, STNE, GPe, D1STR, D2STR, FSI, LIP, M1, Th])
    # LIPb = makePop("LIPb", [GABA, [AMPA, 800, 2.0, 3],
    #                         NMDA], cd_pre, {'N': 1120})
    # camP(c, 'LIPb', 'LIPb', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    # camP(c, 'LIPb', 'LIP', ['AMPA', 'NMDA'], ['all'], 1, [0.043825, 0.14462])
    # camP(c, 'LIPb', 'LIPI', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])
    # LIPI = makePop("LIPI", [GABA, [AMPA, 800, 1.62, 3], NMDA], cd_pre, {
    #                'N': 400, 'C': 0.2, 'Taum': 10})
    # camP(c, 'LIPI', 'LIPb', 'GABA', ['all'], 1, 1.3)
    # camP(c, 'LIPI', 'LIP', 'GABA', ['all'], 1, 1.3)
    # camP(c, 'LIPI', 'LIPI', 'GABA', ['all'], 1, 1)
    # M1b = makePop("M1b", [GABA, [AMPA, 800, 2.0, 3],
    #                       NMDA], cd_pre, {'N': 1120})
    # camP(c, 'M1b', 'M1b', ['AMPA', 'NMDA'], ['all'], 1, [0.05, 0.165])
    # camP(c, 'M1b', 'M1', ['AMPA', 'NMDA'], ['all'], 1, [0.043825, 0.14462])
    # camP(c, 'M1b', 'M1I', ['AMPA', 'NMDA'], ['all'], 1, [0.04, 0.13])
    # M1I = makePop("M1I", [GABA, [AMPA, 800, 1.62, 3], NMDA], cd_pre, {
    #     'N': 400, 'C': 0.2, 'Taum': 10})
    # camP(c, 'M1I', 'M1b', 'GABA', ['all'], 1, 1.3)
    # camP(c, 'M1I', 'M1', 'GABA', ['all'], 1, 1.3)
    # camP(c, 'M1I', 'M1I', 'GABA', ['all'], 1, 1)
    # brain = makeChannel('brain', [LIPb, LIPI, M1b, M1I], [action_channel])

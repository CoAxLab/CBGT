# old preset dicts (cosyne18)
# presetHi = [{'cxd': {'src':[0,1],'dest':[0,1],'mult':[1.8, .5]},
#              'cxi': {'src':[0,1],'dest':[0,1],'mult':[.5, 1.8]}}]
# presetMed = [{'cxd': {'src':[0,1],'dest':[0,1],'mult':[1.25, .9]},
#               'cxi': {'src':[0,1],'dest':[0,1],'mult':[.8, 1.1]}}]
# presetLo = [{'cxd': {'src':[0,1],'dest':[0,1],'mult':[1.1, .9]},
#              'cxi': {'src':[0,1],'dest':[0,1],'mult':[.8, 1.1]}}]



# latest preset dicts (master branch Jan. 2018)
presetHi = [{'cxd': {'src':[0,1],'dest':[0,1],'mult':[1.5, .5]},
             'cxi': {'src':[0,1],'dest':[0,1],'mult':[.8, 1.2]}}]
presetMod = [{'cxd': {'src':[0,1],'dest':[0,1],'mult':[1.25, .75]},
             'cxi': {'src':[0,1],'dest':[0,1],'mult':[.9, 1.1]}}]
presetBal = [{'cxd': {'src':[0,1],'dest':[0,1],'mult':[1., 1.]},
              'cxi': {'src':[0,1],'dest':[0,1],'mult':[1., 1.]}}]

# High wD/wI ratio ("Phasic")
ng.setDirectory('hiDI')
sweepcount = ng.configureSweep(experiment='mc', Start=400, popscale=0.5, BaseStim=[0.], WrongStim = [3.75], RightStim = [3.75], Dynamic=[30.0], Choices=2, M1Th=0., M1STR=.5, CxSTR=.5, GPiExtEff=6.2, STNExtEff=1.7, STNExtFreq=4.5, preset=presetHi)
ng.compileAndRunSweep(ntrials, 0, sweepcount)

# Moderate wD/wI ratio ("Phasic")
ng.setDirectory('modDI')
sweepcount = ng.configureSweep(experiment='mc', Start=400, popscale=0.5, BaseStim=[0.], WrongStim = [3.75], RightStim = [3.75], Dynamic=[30.0], Choices=2, M1Th=0., M1STR=.5, CxSTR=.5, GPiExtEff=6.2, STNExtEff=1.7, STNExtFreq=4.5, preset=presetMod)
ng.compileAndRunSweep(ntrials, 0, sweepcount)

# Balanced wD/wI ratio ("Phasic")
ng.setDirectory('balDI')
sweepcount = ng.configureSweep(experiment='mc', Start=400, popscale=0.5, BaseStim=[0.], WrongStim = [3.75], RightStim = [3.75], Dynamic=[30.0], Choices=2, M1Th=0., M1STR=.5, CxSTR=.5, GPiExtEff=6.2, STNExtEff=1.7, STNExtFreq=4.5, preset=presetBal)
ng.compileAndRunSweep(ntrials, 0, sweepcount)

import os
import numpy as np
import pandas as pd
import cbgt.netgen as ng
import random
import warnings

warnings.simplefilter('ignore', np.RankWarning)

def run_cbgt_sweeps(stimArray, preset=None, rampingCTX=True, savedir=None,
                    cond='bal', ntrials=1000, Start=200,
                    popscale=0.5, BaseStim=0.0, Dynamic=30.0, Choices=2,
                    **kwargs):

    if savedir is None:
        savedir = os.path.join(os.path.expanduser('~'), 'cbgt')

    if not os.path.isdir(savedir):
        os.mkdir(savedir)
    ng.setDirectory(savedir)

    for t, stim in enumerate(stimArray):
        np.random.seed(seed=t)
        sweepcount = ng.configureSweep(t, experiment='mc',
        rampingCTX=rampingCTX, preset=preset, Start=Start, popscale=popscale,
        BaseStim=BaseStim, WrongStim=stim, RightStim=stim,
        Dynamic=Dynamic, Choices=Choices, **kwargs)

    ng.compileAndRunSweep(1, 0, ntrials)
    results = np.hstack(ng.readAllTrialResults(1,0,ntrials))
    return results


# def run_cbgt_sweeps_OLD(stimArray, preset=None, rampingCTX=False, savedir=None,
#                     cond='bal', ntrials=1000, Start=200,
#                     popscale=0.5, BaseStim=0.0, Dynamic=48.0, Choices=2,
#                     CxSTR=1.0, GPiExtEff=6.35, STNExtEff=1.65,
#                     STNExtFreq=4.6, CxFSI=0.18, CxTh=0.2, ThSTR=0.18, ThCx=0.05):
#
#     if savedir is None:
#         savedir = os.path.join(os.path.expanduser('~'), 'cbgt')
#     ng.setDirectory(savedir); t=0
#
#     for stim in stimArray:
#         sweepcount = ng.configureSweep(t, experiment='mc',
#         rampingCTX=rampingCTX, preset=preset, Start=Start, popscale=popscale,
#         BaseStim=BaseStim, WrongStim=stim, RightStim=stim,
#         Dynamic=Dynamic, Choices=Choices, CxSTR=CxSTR, GPiExtEff=GPiExtEff,
#         SNExtEff=STNExtEff, STNExtFreq=STNExtFreq, CxFSI=CxFSI, CxTh=CxTh,
#         ThSTR=ThSTR, ThCx=ThCx)
#         t += 1
#
#     ng.compileAndRunSweep(1, 0, ntrials)
#     results = np.hstack(ng.readAllTrialResults(1,0,ntrials))
#     return results


def single_trial_sim(t=0, stim=2.52, preset_dict=None):

    Choices     =    2
    BaseStim    =    [0.00]
    Dynamic     =    [20.0]
    Start       =    200
    popscale    =    0.3

    GPiExtEff   =   5.925
    STNExtEff   =   1.59
    STNExtFreq  =   4.45

    CxSTR      =    0.25
    CxTh       =    0.015
    CxFSI      =    0.2
    ThSTR      =    0.2
    ThCx       =    0.01


    sweepcount = ng.configureSweep(0, experiment='mc', preset=preset_dict,
                                    Start=Start, popscale=popscale,
                                    BaseStim=BaseStim,
                                    WrongStim=stim, RightStim=stim,
                                    Dynamic=Dynamic,  Choices=Choices,
                                    CxSTR=CxSTR, GPiExtEff=GPiExtEff,
                                    STNExtEff=STNExtEff, STNExtFreq=STNExtFreq,
                                    CxFSI=CxFSI, CxTh=CxTh, ThSTR=ThSTR,
                                    ThCx=ThCx, rampingCTX=True)
    ng.compileAndRunSweepALL(1, 0, 1)

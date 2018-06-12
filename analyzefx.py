import os
import bgNetwork.netgen as ng
import numpy as np
import pandas as pd

def print_results_summary(behavdf):
    cond = behavdf.cond.iloc[0]
    pLeft = behavdf.acc.mean()
    corRT = behavdf[behavdf.acc==1].rtms.mean()
    corMedRT = behavdf[behavdf.acc==1].rtms.median()
    corRTvar = behavdf[behavdf.acc==1].rtms.sem()*2
    errRT = 999.99; errRTvar = 0.0
    if behavdf[behavdf.acc==0].shape[0]>1:
        errRT = behavdf[behavdf.acc==0].rtms.mean()
        errRTvar = behavdf[behavdf.acc==0].rtms.sem()*2
    resultsSummary = 'Cond: {}\n\tMean CorRT:\t{:.2f} ({:.2f})\n\tMed CorRT:\t{:.2f}\n\tAvg ErrRT:\t{:.2f} ({:.2f})\n\tP(Left):\t{:.4f}'
    print(resultsSummary.format(cond.upper(),corRT, corRTvar, corMedRT, errRT, errRTvar, pLeft))

def print_trial_acc_rt(results, t=0):
    bdata = ng.findOutputs(results[t])['decision made']
    rt = bdata['time']
    if bdata['pathvals'] is not None:
        acc = ['Error' if bdata['pathvals'][0] else 'Correct'][0]
        print('RT:\t{:.2f}ms\nAcc:\t{}\n'.format(rt,acc))
        return 1
    else:
        return 0

def get_msn_rates(sdf):
    dL = sdf[sdf['population']=='dMSN0'].reset_index(drop=True)
    dR = sdf[sdf['population']=='dMSN1'].reset_index(drop=True)
    iL = sdf[sdf['population']=='iMSN0'].reset_index(drop=True)
    iR = sdf[sdf['population']=='iMSN1'].reset_index(drop=True)
    dlx = dL.fillna(method='pad', axis=1).convert_objects(convert_numeric=True)
    drx = dR.fillna(method='pad', axis=1).convert_objects(convert_numeric=True)
    ilx = iL.fillna(method='pad', axis=1).convert_objects(convert_numeric=True)
    irx = iR.fillna(method='pad', axis=1).convert_objects(convert_numeric=True)
    return [dlx, drx, ilx, irx]

def get_avgMSN_traces(msnDFs, window=None):
    rolltime = lambda df, w: df.rolling(w, axis=1).mean()
    getMean = lambda df: df.groupby('cond2').mean().ix[:, 200:].values
    getErr = lambda df: df.groupby('cond2').std().ix[:, 200:].values / 1.5
    if window is not None:
        msnDFs = [rolltime(msnPop, window) for msnPop in msnDFs]
    ys = [getMean(msnPop) for msnPop in msnDFs]
    ysErr = [getErr(msnPop) for msnPop in msnDFs]
    return ys, ysErr

def get_single_trial_ratedf(spikedf, trial=0):
    spikedf = spikedf.drop(columns=['cond', 'cond2'])
    sdf = spikedf[spikedf.trial==trial].T.reset_index(drop=True)
    sdf.columns = sdf.iloc[0, :].values
    sdf = sdf.drop(0)
    sdf = sdf.fillna(np.nan)
    return sdf

def get_mean_firing_rates(spikedf, window=None):
    avgdf = spikedf.groupby(['population']).mean().iloc[:, 1:].T.reset_index(drop=True)
    return avgdf

def get_firing_rates(results, window=None, getavg=False, cond='test'):
    dflist = []
    condABC = {'low': 'a', 'med': 'b', 'high': 'c', 'test':'x'}
    for i, res in enumerate(results):
        ratedf = res['popfreqs']
        if window is not None:
            ratedf = ratedf.rolling(window).mean()
        ratedf = ratedf.T
        if ratedf.shape[1]==0:
            break
        ratedf.insert(0, 'trial', i)
        dflist.append(ratedf)
    sdf = pd.concat(dflist).reset_index()
    sdf = sdf.rename(columns={'index':'population'})
    sdf = rename_populations(sdf)
    sdf.insert(1, 'cond2', condABC[cond])
    sdf.insert(1, 'cond', cond)
    if getavg:
        return get_mean_firing_rates(sdf)
    return sdf

def analyze_network_behavior(results, preset, stimArray, cond='test', outdir=None):
    rtms, choice, acc, decisions = [], [], [], []
    condABC = {'low': 'a', 'med': 'b', 'high': 'c'}
    condLevel = {'low': 1, 'med': 2, 'high': 3, 'test': 0}
    for result in results:
        decisions.append(ng.findOutputs(result)['decision made'])
    for decision in decisions:
        if decision['pathvals'] is None:
            choice.append(np.nan)
            acc.append(np.nan)
            rtms.append(np.nan)
            continue
        elif decision['pathvals'] == [0]:
            choice.append(0)
            acc.append(1)
        else:
            choice.append(1)
            acc.append(0)
        rtms.append(decision['delay'])
    behav_arr = [np.asarray(arr) for arr in [choice, acc, rtms]]
    behavdf = pd.DataFrame(dict(zip(['choice', 'acc', 'rtms'], behav_arr)))
    behavdf['rtms'] = behavdf.rtms.values + 200
    behavdf['rt'] = behavdf.rtms.values * .001
    behavdf.insert(0, 'trial', np.arange(1, behavdf.shape[0]+1))
    behavdf.insert(0, 'response', behavdf.acc.values)
    behavdf.insert(0, 'cond', cond)
    behavdf.insert(0, 'stim', stimArray[:behavdf.shape[0]])
    behavdf.insert(0, 'subj_idx', 1)
    behavdf['cond2'] = condABC[cond]
    behavdf['level'] = condLevel[cond]
    dL,dR = preset[0]['cxd']['mult']
    iL,iR = preset[0]['cxi']['mult']
    behavdf['wdL'] = dL
    behavdf['wdR'] = dR
    behavdf['wiL'] = iL
    behavdf['wiR'] = iR
    behavdf = behavdf[['subj_idx', 'cond', 'cond2', 'level', 'trial', 'stim', 'wdL', 'wiL', 'wdR', 'wiR', 'response', 'acc', 'choice', 'rtms', 'rt']]
    print_results_summary(behavdf)
    if outdir is not None:
        behavdfName = os.path.join(outdir,'cbgt_behavdf_{}.csv'.format(cond))
        outdir = os.path.join(outdir, behavdfName)
        behavdf.to_csv(behavdfName, index=False)
    return behavdf


def make_wts_df(presets=None, conds=['low', 'med', 'high'], ntrials=1000):

    if presets is None:
        presetLow = [{'cxd': {'dest': [0, 1], 'mult': [1.02, 0.99], 'src': [0, 1]},
              'cxi': {'dest': [0, 1], 'mult': [1.0, 1.0], 'src': [0, 1]}}]
        presetMed = [{'cxd': {'dest': [0, 1], 'mult': [1.035, 0.98], 'src': [0, 1]},
                      'cxi': {'dest': [0, 1], 'mult': [1.0, 1.0], 'src': [0, 1]}}]
        presetHi = [{'cxd': {'dest': [0, 1], 'mult': [1.045, 0.97], 'src': [0, 1]},
                     'cxi': {'dest': [0, 1], 'mult': [1.0, 1.0], 'src': [0, 1]}}]
        presets = [presetLow, presetMed, presetHi]

    condlist, dleft, dright, ileft, iright = [], [], [], [], []
    for i, pre in enumerate(presets):
        dL,dR = pre[0]['cxd']['mult']
        iL,iR = pre[0]['cxi']['mult']
        condlist.extend([conds[i]]*ntrials)
        dleft.extend([dL]*ntrials)
        dright.extend([dR]*ntrials)
        ileft.extend([iL]*ntrials)
        iright.extend([iR]*ntrials)
    weightdf = pd.DataFrame({'cond':condlist, 'wdL': dleft, 'wiL':ileft, 'wdR':dright, 'wiR':iright})[['cond', 'wdL', 'wiL', 'wdR', 'wiR']]
    return weightdf

def rename_populations(sdf):
    popNames = []
    oldPopNames = sdf.population.unique().tolist()
    for pop in oldPopNames:
        poplist = pop.split('_')
        if len(poplist)==2:
            popName = poplist[0]
        else:
            popName = ''.join(poplist[:2])
        if 'D1STR' in popName:
            popName = 'dMSN'+popName[-1]
        elif 'D2STR' in popName:
            popName = 'iMSN'+popName[-1]
        elif 'STNE' in popName:
            popName = 'STN'+popName[-1]
        elif 'GPeP' in popName:
            popName = 'GPe'+popName[-1]
        elif 'Time (ms)' in popName:
            popName = 'time'
        popNames.append(popName)

    sdfNew = sdf.replace({'population': dict(zip(oldPopNames, popNames))})
    return sdfNew

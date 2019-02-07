import os
import cbgt.netgen as ng
import numpy as np
import pandas as pd

roundRT = lambda x, ndec: int(round(float(str(x)[:5]), ndec)*1000)
zscore_series = lambda s: (s - s.mean()) / s.std()
normalize_series = lambda s: (s - s.min()) / (s.max() - s.min())

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

    #rolltime = lambda df, w: df.rolling(w, axis=1).mean()
    rolltime = lambda df, w: df.ix[:, 200:].rolling(w, axis=1).mean().iloc[:, w:]
    getMean = lambda df: df.groupby('cond2').mean().ix[:, 205:].values
    getErr = lambda df: df.groupby('cond2').std().ix[:, 205:].values / 1.4
    if window is not None:
        for i, msndf in enumerate(msnDFs):
            msndf.ix[:, 200+window:] = rolltime(msndf, window)
            msnDFs[i] = msndf
            #msnDFs = [rolltime(msnPop, window) for msnPop in msnDFs]
    ys = [getMean(msnPop) for msnPop in msnDFs]
    ysErr = [getErr(msnPop) for msnPop in msnDFs]
    return ys, ysErr

def get_single_trial_ratedf(spikedf, trial=0):
    spikedf = spikedf.drop(columns=['idx', 'cond', 'cond2'])
    sdf = spikedf[spikedf.trial==trial].T.reset_index(drop=True)
    sdf.columns = sdf.iloc[0, :].values
    sdf = sdf.drop(0)
    sdf = sdf.fillna(np.nan)
    return sdf

def get_mean_firing_rates(spikedf, window=None):
    avgdf = spikedf.groupby(['population']).mean().iloc[:, 1:].T.reset_index(drop=True)
    return avgdf

def get_firing_rates(results, window=None, getavg=False, cond='test', idx=1):
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
    sdf.insert(1, 'idx', idx)
    sdf['trial'] = sdf.trial.values #+ 1

    if getavg:
        return get_mean_firing_rates(sdf)
    return sdf

def analyze_network_behavior(results, preset, stimArray, cond='test', outdir=None, idx=1, conEff=None):
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
    behavdf.insert(0, 'trial', np.arange(behavdf.shape[0]))
    behavdf.insert(0, 'response', behavdf.acc.values)
    behavdf.insert(0, 'cond', cond)
    behavdf.insert(0, 'stim', stimArray[:behavdf.shape[0]])
    behavdf.insert(0, 'subj_idx', idx)
    behavdf['cond2'] = condABC[cond]
    behavdf['level'] = condLevel[cond]

    dL,dR = preset[0]['cxd']['mult']
    iL,iR = preset[0]['cxi']['mult']

    idx_CxSTR_w = 1
    if conEff is not None:
        idx_CxSTR_w = conEff['Cx']['STR'][0]

    behavdf['wdL'] = dL * idx_CxSTR_w
    behavdf['wdR'] = dR * idx_CxSTR_w
    behavdf['wiL'] = iL * idx_CxSTR_w
    behavdf['wiR'] = iR * idx_CxSTR_w

    behavdf = behavdf[['subj_idx', 'cond', 'cond2', 'level', 'trial', 'stim', 'wdL', 'wiL', 'wdR', 'wiR', 'response', 'acc', 'choice', 'rtms', 'rt']]
    print_results_summary(behavdf)
    if outdir is not None:
        behavdfName = os.path.join(outdir,'cbgt_behavdf_{}_idx{}.csv'.format(cond, idx))
        outdir = os.path.join(outdir, behavdfName)
        behavdf.to_csv(behavdfName, index=False)
    return behavdf


def make_wts_df(presets=None, conds=['low', 'med', 'high'], ntrials=1000):

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


def get_cbgt_covariates(df, msndf, conds=['low', 'med', 'high']):

    if np.any(msndf.isna()):
        msnPad = msndf.fillna(method='pad', axis=1).convert_objects(convert_numeric=True)
    else:
        msnPad = msndf.copy()

    c_list = []
    for c in conds:
        msn_c = msnPad[msnPad.cond==c]

        idx_list = []
        for idx in df.subj_idx.unique():
            idf = df[(df.subj_idx==idx)&(df.cond==c)&(~df.rt.isna())]
            trials = idf.trial.values
            msn_ci = msn_c[(msn_c.idx==idx)&(msn_c.trial.isin(trials))]
            msn_ci = msn_ci.drop_duplicates()

            DL = msn_ci[msn_ci.population=='dMSN0'].iloc[:, 205:].values
            DR = msn_ci[msn_ci.population=='dMSN1'].iloc[:, 205:].values
            IL = msn_ci[msn_ci.population=='iMSN0'].iloc[:, 205:].values
            IR = msn_ci[msn_ci.population=='iMSN1'].iloc[:, 205:].values

            idf['dL_rate'] = DL.sum(axis=1)
            idf['dR_rate'] = DR.sum(axis=1)
            idf['iL_rate'] = IL.sum(axis=1)
            idf['iR_rate'] = IR.sum(axis=1)

            idf['D_lrdiff_sum'] = np.sum(DL - DR, axis=1)
            idf['DI_ldiff_sum'] = np.sum(DL - IL, axis=1)
            idf['I_lrdiff_sum'] = np.sum(IL - IR, axis=1)
            idf['I_LR_mean'] = (idf.iL_rate + idf.iR_rate)/2

            idx_list.append(idf)

        c_list.append(pd.concat(idx_list).reset_index(drop=True))

    df_new = pd.concat(c_list).reset_index(drop=True)
    return df_new


def norm_covariates(bdf):
    zscore_series = lambda s: (s - s.mean()) / s.std()
    normalize_series = lambda s: (s - s.min()) / (s.max() - s.min())
    xdf = bdf.copy() #fillna(bdf.mean())

    xdf['ndL_rate'] = normalize_series(xdf.dL_rate.values)
    xdf['niL_rate'] = normalize_series(xdf.iL_rate.values)
    xdf['ndR_rate'] = normalize_series(xdf.dR_rate.values)
    xdf['niR_rate'] = normalize_series(xdf.iR_rate.values)

    xdf['nD_lrdiff_sum'] = normalize_series(xdf.D_lrdiff_sum.values)
    xdf['nDI_ldiff_sum'] = normalize_series(xdf.DI_ldiff_sum.values)
    xdf['nI_lrdiff_sum'] = normalize_series(xdf.I_lrdiff_sum.values)
    xdf['nI_LR_mean'] = normalize_series(xdf.I_LR_mean.values)
    #xdf['I_LR_mean2'] = (xdf.iL_rate + xdf.iR_rate)/2
    #xdf['nI_LR_mean2'] = normalize_series(xdf['I_LR_mean2'])
    xdf = xdf.reset_index(drop=True)
    return xdf



##########################################################
#                       OLD                              #
##########################################################


#
# def get_cbgt_covariates(df, msnDFs):
#
#     conds = df.cond.unique().tolist()
#
#     dlx, drx, ilx, irx = msnDFs
#     dL = dlx.reset_index(drop=True)
#     iL = ilx.reset_index(drop=True)
#     dR = drx.reset_index(drop=True)
#     iR = irx.reset_index(drop=True)
#
#     for c in conds:
#
#         trials = df[(df.cond==c)&(~df.rt.isna())].trial.values
#         rt = df[(df.cond==c)&(~df.rt.isna())]['rtms'].astype(int).reset_index(drop=True).values
#         acc = df[(df.cond==c)&(~df.rt.isna())]['acc'].astype(int).reset_index(drop=True).values
#
#         dL_rate_list = []; iL_rate_list = [];
#         dR_rate_list = []; iR_rate_list = [];
#
#         d_lrdiff_sum_list = []
#         di_ldiff_sum_list = []
#         i_lrdiff_sum_list = []
#         i_lrmean_sum_list = []
#
#         for i, t in enumerate(trials):
#             DLFull = np.squeeze(dL[(dL.cond==c)&(dL.trial==t)].ix[:, 205:].dropna(axis=1).values)
#             ILFull = np.squeeze(iL[(iL.cond==c)&(iL.trial==t)].ix[:, 205:].dropna(axis=1).values)
#             DRFull = np.squeeze(dR[(dR.cond==c)&(dR.trial==t)].ix[:, 205:].dropna(axis=1).values)
#             IRFull = np.squeeze(iR[(iR.cond==c)&(iR.trial==t)].ix[:, 205:].dropna(axis=1).values)
#
#             dL_rate_list.append(np.sum(DLFull))
#             iL_rate_list.append(np.sum(ILFull))
#             dR_rate_list.append(np.sum(DRFull))
#             iR_rate_list.append(np.sum(IRFull))
#
#             d_lrdiff_sum_list.append(np.sum(DLFull - DRFull))
#             di_ldiff_sum_list.append(np.sum(DLFull - ILFull))
#             i_lrdiff_sum_list.append(np.sum(ILFull - IRFull))
#             i_lrmean_sum_list.append(np.column_stack([ILFull, IRFull]).mean(1).sum())
#
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'dL_rate'] = dL_rate_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'iL_rate'] = iL_rate_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'dR_rate'] = dR_rate_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'iR_rate'] = iR_rate_list
#
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'D_lrdiff_sum'] = d_lrdiff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'DI_ldiff_sum'] = di_ldiff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'I_lrdiff_sum'] = i_lrdiff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'I_LR_mean'] = i_lrmean_sum_list
#         # df.ix[(df.cond==c)&(~df.rt.isna()), 'I_LR_mean2'] = (df.ix[(df.cond==c)&(~df.rt.isna())].iL_rate + df.ix[(df.cond==c)&(~df.rt.isna())].iR_rate)/2
#
#     return df


# def get_cbgt_covariates(df, msnDFs):
#
#     conds = df.cond.unique().tolist()
#
#     dlx, drx, ilx, irx = msnDFs
#     dL = dlx.reset_index(drop=True)
#     iL = ilx.reset_index(drop=True)
#     dR = drx.reset_index(drop=True)
#     iR = irx.reset_index(drop=True)
#
#     for c in conds:
#
#         trials = df[(df.cond==c)&(~df.rt.isna())].trial.values
#         rt = df[(df.cond==c)&(~df.rt.isna())]['rtms'].astype(int).reset_index(drop=True).values
#         acc = df[(df.cond==c)&(~df.rt.isna())]['acc'].astype(int).reset_index(drop=True).values
#
#         d_diff_list, di_diff_list, id_diff_list, imax_list = [], [], [], []
#         d_diff_sum_list = []; d_lrdiff_sum_list = []; di_ldiff_sum_list = []
#         di_lrdiff_sum_list = []; di_rdiff_sum_list = []; di_lrdiff_sum_list = []
#         i_lrmean_sum_list = []; id_rldiff_sum_list = []; i_rldiff_sum_list = []
#         dL_rate_list = []; iL_rate_list = []; dR_rate_list = []; iR_rate_list = []; i_lrdiff_sum_list = []
#
#         for i, t in enumerate(trials):
#             DLFull = np.squeeze(dL[(dL.cond==c)&(dL.trial==t)].ix[:, 205:].dropna(axis=1).values)
#             ILFull = np.squeeze(iL[(iL.cond==c)&(iL.trial==t)].ix[:, 205:].dropna(axis=1).values)
#             DRFull = np.squeeze(dR[(dR.cond==c)&(dR.trial==t)].ix[:, 205:].dropna(axis=1).values)
#             IRFull = np.squeeze(iR[(iR.cond==c)&(iR.trial==t)].ix[:, 205:].dropna(axis=1).values)
#
#             dL_rate_list.append(np.sum(DLFull))
#             iL_rate_list.append(np.sum(ILFull))
#             dR_rate_list.append(np.sum(DRFull))
#             iR_rate_list.append(np.sum(IRFull))
#
#             d_lrdiff_sum_list.append(np.sum(DLFull - DRFull))
#             di_ldiff_sum_list.append(np.sum(DLFull - ILFull))
#             i_lrdiff_sum_list.append(np.sum(ILFull - IRFull))
#             i_lrmean_sum_list.append(np.column_stack([ILFull, IRFull]).mean(1).sum())
#             i_lrmean_sum_list2.append(np.column_stack([ILFull, IRFull]).mean(1).sum())
#
#             di_rdiff_sum_list.append(np.sum(DRFull - IRFull))
#             di_lrdiff_sum_list.append(np.sum(DLFull - ILFull) - np.sum(DRFull - IRFull))
#             id_rldiff_sum_list.append(np.sum(IRFull - DRFull) - np.sum(ILFull - DLFull))
#             i_rldiff_sum_list.append(np.sum(IRFull - ILFull))
#
#             if acc[i]:
#                 id_diff_list.append(np.sum(ILFull - DLFull))
#                 di_diff_list.append(np.sum(DLFull - ILFull))
#                 d_diff_sum_list.append(np.sum(DLFull - DRFull))
#                 imax_list.append(np.sum(ILFull))
#             else:
#                 d_diff_sum_list.append(np.sum(DRFull - DLFull))
#                 id_diff_list.append(np.sum(IRFull - DRFull))
#                 di_diff_list.append(np.sum(DRFull - IRFull))
#                 imax_list.append(np.sum(IRFull))
#
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'dL_rate'] = dL_rate_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'iL_rate'] = iL_rate_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'dR_rate'] = dR_rate_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'iR_rate'] = iR_rate_list
#
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'D_lrdiff_sum'] = d_lrdiff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'DI_ldiff_sum'] = di_ldiff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'I_lrdiff_sum'] = i_lrdiff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'I_LR_mean'] = i_lrmean_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'DI_rdiff_sum'] = di_rdiff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'DI_lrdiff_sum'] = di_lrdiff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'ID_diff_chosen'] = id_diff_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'DI_diff_chosen'] = di_diff_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'D_diff_sum'] = d_diff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'I_sum_chosen'] = imax_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'I_LR_mean'] = (df.iL_rate + df.iR_rate)/2
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'I_avgLR_sum'] = i_lrmean_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'ID_rldiff_sum'] = id_rldiff_sum_list
#         df.ix[(df.cond==c)&(~df.rt.isna()), 'I_rldiff_sum'] = i_rldiff_sum_list
#     return df
#
#
# def norm_covariates(bdf):
#     zscore_series = lambda s: (s - s.mean()) / s.std()
#     normalize_series = lambda s: (s - s.min()) / (s.max() - s.min())
#     xdf = bdf.copy() #fillna(bdf.mean())
#
#     xdf['ndL_rate'] = normalize_series(xdf.dL_rate.values)
#     xdf['niL_rate'] = normalize_series(xdf.iL_rate.values)
#     xdf['ndR_rate'] = normalize_series(xdf.dR_rate.values)
#     xdf['niR_rate'] = normalize_series(xdf.iR_rate.values)
#
#     xdf['nD_lrdiff_sum'] = normalize_series(xdf.D_lrdiff_sum.values)
#     xdf['nDI_ldiff_sum'] = normalize_series(xdf.DI_ldiff_sum.values)
#     xdf['nI_lrdiff_sum'] = normalize_series(xdf.I_lrdiff_sum.values)
#     xdf['nI_LR_mean'] = normalize_series(xdf.I_LR_mean.values)
#
#     xdf['zD_diff_sum'] = zscore_series(xdf.D_diff_sum.values)
#     xdf['zD_lrdiff_sum'] = zscore_series(xdf.D_lrdiff_sum.values)
#     xdf['nD_diff_sum'] = normalize_series(xdf.D_diff_sum.values)
#     xdf['nDI_diff_chosen'] = normalize_series(xdf.DI_ldiff_sum.values)
#
#     xdf['nDI_rdiff_sum'] = normalize_series(xdf.DI_rdiff_sum.values)
#     xdf['nDI_lrdiff_sum'] = normalize_series(xdf.DI_lrdiff_sum.values)
#     xdf['nI_sum_chosen'] = normalize_series(xdf.I_sum_chosen.values)
#     xdf['nID_diff_chosen'] = normalize_series(xdf.ID_diff_chosen.values)
#     xdf['nI_avgLR_sum'] = normalize_series(xdf.I_avgLR_sum.values)
#     xdf['nID_rldiff_sum'] = normalize_series(xdf.ID_rldiff_sum.values)
#     xdf['nI_rldiff_sum'] = normalize_series(xdf.I_rldiff_sum.values)
#
#     for dff in [xdf]:
#         dff['IL_DR_diff'] = dff.iL_rate - dff.dR_rate
#         dff['nIL_DR_diff'] = normalize_series(dff.IL_DR_diff)
#         dff['iLdR_diff'] = dff.iL_rate - dff.dR_rate
#         dff['niLdR_diff'] = normalize_series(dff.iLdR_diff)
#         dff['dLiR_avg'] = (dff.dL_rate + dff.iR_rate)/2
#         dff['dLiR_avg'] = normalize_series(dff.dLiR_avg)
#         dff['I_lrdiff_sum'] = dff.iL_rate - dff.iR_rate
#         dff['nI_lrdiff_sum'] = normalize_series(dff['I_lrdiff_sum'])
#         dff['ID_lrdiff_sum'] = (dff.iL_rate - dff.dL_rate) - (dff.iR_rate - dff.dR_rate)
#         dff['nID_lrdiff_sum'] = normalize_series(dff['ID_lrdiff_sum'])
#         #dff['I_LR_mean'] = (dff.iL_rate + dff.iR_rate)/2
#         #dff['nI_LR_mean'] = normalize_series(dff['I_LR_mean'])
#         dff['di_ldiff_sum'] = dff.dL_rate - dff.iL_rate
#         dff['ndi_ldiff_sum'] = normalize_series(dff.dL_rate - dff.iL_rate)
#
#     xdf = xdf.reset_index(drop=True)
#     return xdf

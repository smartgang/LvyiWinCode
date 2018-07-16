# -*- coding: utf-8 -*-
'''
LvyiWin辅助功能
'''
import pandas as pd
import numpy as np
import os
import LvyiWin_Parameter as Parameter
import DATA_CONSTANTS as DC

def resultCalc():
    '''
    重新统计多品种多周期的回测结果
    将各文件夹中的finalResult文件汇总到一起
    :return:
    '''
    upperpath=DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    allsymbolresult = pd.DataFrame(columns=
                                   ['Setname', 'MA_Short', 'MA_Long', 'KDJ_N', 'DMI_N', 'opentimes', 'end_cash',
                                    'SR', 'Annual', 'Sharpe', 'DrawBack', 'max_single_loss_rate',
                                    'strategyName', 'exchange_id', 'sec_id', 'K_MIN'])
    symbolset = pd.read_excel(resultpath + Parameter.symbol_KMIN_set_filename)
    symbolsetNum = symbolset.shape[0]
    for i in range(symbolsetNum):
        strategyName=symbolset.ix[i, 'strategyName']
        exchangeid = symbolset.ix[i, 'exchange_id']
        secid = symbolset.ix[i, 'sec_id']
        symbol = '.'.join([exchangeid, secid])
        K_MIN=symbolset.ix[i, 'K_MIN']
        foldername=' '.join([strategyName, exchangeid, secid, str(K_MIN)])
        print ("collecting %s %d final results"%(symbol,K_MIN))
        result = pd.read_csv(foldername+'\\'+"%s %d finalresults.csv" % (symbol, K_MIN))
        result['strategyName']=strategyName
        result['exchange_id']=exchangeid
        result['sec_id'] = secid
        result['K_MIN'] = K_MIN
        allsymbolresult=pd.concat([allsymbolresult,result])

    allsymbolresult.to_csv(Parameter.strategyName + "_symbol_KMIN_results.csv")
    pass

def successiveEarnDistribut(resultdf,filename,new=True):
    '''连续盈亏分布统计'''
    if new:
        ret_col='new_ret'
    else:
        ret_col='ret'
    df1 = pd.DataFrame()
    df1[ret_col] = resultdf[ret_col]
    df1['tradetype'] = resultdf['tradetype']
    df1['oprindex'] = np.arange(df1.shape[0])
    df1['win'] = -1
    df1.loc[df1[ret_col] > 0, 'win'] = 1
    df1['win_shift1'] = df1['win'].shift(1).fillna(0)
    df1['win_cross'] = 0
    df1.loc[df1['win'] != df1['win_shift1'], 'win_cross'] = df1['oprindex']
    df1.ix[0, 'win_cross'] = 1
    df2 = pd.DataFrame()
    df2['oprindex'] = df1.loc[df1['win_cross'] != 0, 'oprindex']
    df2[ret_col] = df1.loc[df1['win_cross'] != 0,ret_col]
    df2['count'] = df2['oprindex'].shift(-1).fillna(0) - df2['oprindex']
    df2.ix[df2.iloc[-1].oprindex, 'count'] = 0
    win_count = df2.loc[df2[ret_col] > 0, 'count']
    loss_count = df2.loc[df2[ret_col] <= 0, 'count']
    df2.to_csv(filename+'successiveEarnDis.csv')

def parasetGenerator():
    upperpath=DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    setlist = []
    i = 0
    for ms in [5, 6, 7]:
        for ml in [24,25,26, 27, 28, 29, 30]:
            for kn in [6, 8, 20, 22, 24, 26, 28, 30]:
                for dn in [28, 30, 32, 34, 36]:
                    setname = 'Set' + str(i) + ' MS' + str(ms) + ' ML' + str(ml) + ' KN' + str(kn) + ' DN' + str(dn)
                    l = [setname, ms, ml, kn, dn]
                    setlist.append(l)
                    i += 1

    setpd = pd.DataFrame(setlist, columns=['Setname', 'MA_Short', 'MA_Long', 'KDJ_N', 'DMI_N'])
    setpd.to_csv(resultpath+'ParameterOptSet_simple.csv')


if __name__=='__main__':
    #resultCalc()
    parasetGenerator()
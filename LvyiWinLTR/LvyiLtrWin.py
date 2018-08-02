# -*- coding: utf-8 -*-
"""
LvyiWin模式的波动行情特征分析
"""

import pandas as pd
import numpy as np
import MA
import DMI
import KDJ
import DATA_CONSTANTS as DC
import ConfigParser
import ResultStatistics as RS
import os

def LvyiLtrWin(symbolinfo, rawdata, paraset):
    setname = paraset['Setname']
    LTR_TIME = paraset['LTR_TIME']
    KDJ_N = paraset['KDJ_N']
    KDJ_M = paraset['KDJ_M']
    KDJ_HLim = paraset['KDJ_HLim']
    KDJ_LLim = paraset['KDJ_LLim']
    DMI_N = paraset['DMI_N']
    DMI_M = paraset['DMI_M']
    MA_Short = paraset['MA_Short']
    MA_Long = paraset['MA_Long']
    rawdata['Unnamed: 0'] = range(rawdata.shape[0])
    beginindex = rawdata.ix[0, 'Unnamed: 0']

    # 处理KDJ数据：KDJ_OPEN做为最终KDJ的触发信号
    df_KDJ = KDJ.KDJ(rawdata, N=KDJ_N, M=KDJ_M)
    df_KDJ['KDJ_True'] = 0
    df_KDJ.loc[(KDJ_HLim > df_KDJ['KDJ_K']) & (df_KDJ['KDJ_K'] > df_KDJ['KDJ_D']), 'KDJ_True'] = 1
    df_KDJ.loc[(KDJ_LLim < df_KDJ['KDJ_K']) & (df_KDJ['KDJ_K'] < df_KDJ['KDJ_D']), 'KDJ_True'] = -1
    df_DMI = DMI.DMI(rawdata, N=DMI_N, M=DMI_M)
    df_MA = MA.MA(rawdata['close'], MA_Short, MA_Long)
    df_MA.drop('close', axis=1, inplace=True)
    df = pd.concat([rawdata, df_DMI, df_KDJ, df_MA], axis=1)

    goldcrosslist = pd.DataFrame({'goldcrosstime': df.loc[df['MA_Cross'] == 1, 'strtime']})
    goldcrosslist['goldcrossutc'] = df.loc[df['MA_Cross'] == 1, 'utc_time']
    goldcrosslist['goldcrossindex'] = df.loc[df['MA_Cross'] == 1, 'Unnamed: 0'] - beginindex
    goldcrosslist['goldcrossprice'] = df.loc[df['MA_Cross'] == 1, 'close']

    # 取出死叉点
    deathcrosslist = pd.DataFrame({'deathcrosstime': df.loc[df['MA_Cross'] == -1, 'strtime']})
    deathcrosslist['deathcrossutc'] = df.loc[df['MA_Cross'] == -1, 'utc_time']
    deathcrosslist['deathcrossindex'] = df.loc[df['MA_Cross'] == -1, 'Unnamed: 0'] - beginindex
    deathcrosslist['deathcrossprice'] = df.loc[df['MA_Cross'] == -1, 'close']
    goldcrosslist = goldcrosslist.reset_index(drop=True)
    deathcrosslist = deathcrosslist.reset_index(drop=True)

    # 生成多仓序列（金叉在前，死叉在后）
    if goldcrosslist.ix[0, 'goldcrossindex'] < deathcrosslist.ix[0, 'deathcrossindex']:
        longcrosslist = pd.concat([goldcrosslist, deathcrosslist], axis=1)
    else:  # 如果第一个死叉的序号在金叉前，则要将死叉往上移1格
        longcrosslist = pd.concat([goldcrosslist, deathcrosslist.shift(-1).fillna(0)], axis=1)
    longcrosslist = longcrosslist.set_index(pd.Index(longcrosslist['goldcrossindex']), drop=True)

    # 生成空仓序列（死叉在前，金叉在后）
    if deathcrosslist.ix[0, 'deathcrossindex'] < goldcrosslist.ix[0, 'goldcrossindex']:
        shortcrosslist = pd.concat([deathcrosslist, goldcrosslist], axis=1)
    else:  # 如果第一个金叉的序号在死叉前，则要将金叉往上移1格
        shortcrosslist = pd.concat([deathcrosslist, goldcrosslist.shift(-1).fillna(0)], axis=1)
    shortcrosslist = shortcrosslist.set_index(pd.Index(shortcrosslist['deathcrossindex']), drop=True)

    longcrosslist['tradetype'] = 1
    longcrosslist.rename(columns={'goldcrosstime': 'opentime',
                            'goldcrossutc': 'openutc',
                            'goldcrossindex': 'openindex',
                            'goldcrossprice': 'openprice',
                            'deathcrosstime': 'closetime',
                            'deathcrossutc': 'closeutc',
                            'deathcrossindex': 'closeindex',
                            'deathcrossprice': 'closeprice'}, inplace=True)

    shortcrosslist['tradetype'] = -1
    shortcrosslist.rename(columns={'deathcrosstime': 'opentime',
                             'deathcrossutc': 'openutc',
                             'deathcrossindex': 'openindex',
                             'deathcrossprice': 'openprice',
                             'goldcrosstime': 'closetime',
                             'goldcrossutc': 'closeutc',
                             'goldcrossindex': 'closeindex',
                             'goldcrossprice': 'closeprice'}, inplace=True)

    result = pd.concat([longcrosslist, shortcrosslist])
    result = result.sort_index()
    result = result.reset_index(drop=True)
    result['wave_time'] = result['closeindex'] - result['openindex']
    result['wave_height'] = np.abs(result['closeprice'] - result['openprice'])  # 高度取绝对值

    result['ltr_flag'] = 0
    result.loc[result['wave_time'] > LTR_TIME, 'ltr_flag'] = 1
    result['wave_index'] = range(0, result.shape[0])
    result.loc[result['ltr_flag']==1, 'ltr_index'] = result['wave_index']
    result.fillna(method='ffill', axis=0, inplace=True)
    result.fillna(0, inplace=True)
    result.loc[result['ltr_index'] == 0, 'ltr_index'] = result['wave_index'] + 1    # 加1是为了确保开始没有大行情的操作的距离为0
    result['ltr_distance'] = result['wave_index'] - result['ltr_index'].shift(1).fillna(0)
    result.fillna(0, inplace=True)
    # 从多仓序列中取出开多序号的内容，即为开多操作
    longopr = result.loc[(df['MA_Cross'] == 1) & (df['KDJ_True'] == 1) & (df['DMI_True'] == 1)]
    # 从空仓序列中取出开空序号的内容，即为开空操作
    shortopr = result.loc[(df['MA_Cross'] == -1) & (df['KDJ_True'] == -1) & (df['DMI_True'] == -1)]
    # 结果分析
    result1 = pd.concat([longopr, shortopr])
    result1 = result1.sort_index()
    result1 = result1.reset_index(drop=True)
    result1.dropna(inplace=True)

    slip = symbolinfo.getSlip()
    result1['ret'] = ((result1['closeprice'] - result1['openprice']) * result1['tradetype']) - slip
    result1['ret_r'] = result1['ret'] / result1['openprice']
    return result1

if __name__ == '__main__':
    domain_symbol = 'SHFE.RB'
    bar_type = 600
    strategyName = 'LvyiLtrWin'
    paraset = {
        'Setname': 'test1',
        'KDJ_N': 28,
        'KDJ_M': 3,
        'KDJ_HLim': 85,
        'KDJ_LLim': 15,
        'DMI_N': 30,
        'DMI_M': 6,
        'MA_Short': 6,
        'MA_Long': 15,
        'LTR_TIME': 50
    }
    symbolinfo = DC.SymbolInfo(domain_symbol)
    rawdataDic = DC.getBarBySymbolList(domain_symbol, symbolinfo.getSymbolList(), bar_type)
    r = LvyiLtrWin(symbolinfo, rawdataDic['RB1810'], paraset)
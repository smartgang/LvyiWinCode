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
import multiprocessing


def LvyiWin_wave(rawdata, paraset):
    # 计算双均线的金叉死叉，形成多空操作文件
    MA_Short = paraset['MA_Short']
    MA_Long = paraset['MA_Long']
    rawdata['Unnamed: 0'] = range(rawdata.shape[0])
    beginindex = rawdata.ix[0, 'Unnamed: 0']

    df_MA = MA.MA(rawdata['close'], MA_Short, MA_Long)

    df_MA.drop('close', axis=1, inplace=True)
    df = pd.concat([rawdata, df_MA], axis=1)

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
        longcrosslist = pd.concat([goldcrosslist, deathcrosslist.shift(-1)], axis=1)
    longcrosslist = longcrosslist.set_index(pd.Index(longcrosslist['goldcrossindex']), drop=True)

    # 生成空仓序列（死叉在前，金叉在后）
    if deathcrosslist.ix[0, 'deathcrossindex'] < goldcrosslist.ix[0, 'goldcrossindex']:
        shortcrosslist = pd.concat([deathcrosslist, goldcrosslist], axis=1)
    else:  # 如果第一个金叉的序号在死叉前，则要将金叉往上移1格
        shortcrosslist = pd.concat([deathcrosslist, goldcrosslist.shift(-1)], axis=1)
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

    # 结果分析
    result = pd.concat([longcrosslist, shortcrosslist])
    result = result.sort_index()
    result = result.reset_index(drop=True)
    result['wave_time'] = result['closeindex'] - result['openindex']
    result['wave_height'] = np.abs(result['closeprice'] - result['openprice'])  # 高度取绝对值
    result.dropna(inplace=True)
    return result


def LvyiWin_wave_cal(strategyName, symbolinfo, K_MIN, rawdataDic, para):
    symbollist = symbolinfo.getSymbolList()
    symbolDomainDic = symbolinfo.getSymbolDomainDic()
    result = pd.DataFrame()
    last_domain_utc = None
    setname = para['Setname']
    for symbol in symbollist:
        if last_domain_utc:
            # 如果上一个合约的最后一次平仓时间超过其主力合约结束时间，则要修改本次合约的开始时间为上一次平仓后
            symbol_domain_start = last_domain_utc
            symbolDomainDic[symbol][0] = last_domain_utc
        else:
            symbol_domain_start = symbolDomainDic[symbol][0]
        symbol_domain_end = symbolDomainDic[symbol][1]
        rawdata = rawdataDic[symbol]
        r = LvyiWin_wave(rawdata=rawdata, paraset=para)
        r['symbol'] = symbol  # 增加主力全约列
        r = r.loc[(r['openutc'] >= symbol_domain_start) & (r['openutc'] <= symbol_domain_end)]
        last_domain_utc = None
        if r.shape[0] > 0:
            last_close_utc = r.iloc[-1]['closeutc']
            if last_close_utc > symbol_domain_end:
                # 如果本合约最后一次平仓时间超过其主力合约结束时间，则要修改本合约的主力结束时间为平仓后
                symbolDomainDic[symbol][1] = last_close_utc
                last_domain_utc = last_close_utc
            result = pd.concat([result, r])
    result.reset_index(drop=True, inplace=True)

    wave_time_mean = result['wave_time'].mean()
    wave_time_median = result['wave_time'].median()
    #wave_time_mode = result['wave_time'].mode()
    wave_time_75quanter = result['wave_time'].quantile(0.75)
    wave_height_mean = result['wave_height'].mean()
    wave_height_median = result['wave_height'].median()
    #wave_height_mode = result['wave_height'].mode()
    wave_height_75quanter = result['wave_height'].quantile(0.75)

    result.to_csv(strategyName + ' ' + symbolinfo.domain_symbol + str(K_MIN) + ' ' + setname + ' result.csv', index=False)

    results = [setname, wave_time_mean, wave_time_median, wave_time_75quanter,
               wave_height_mean, wave_height_median, wave_height_75quanter]  # 在这里附上setname

    print results
    return results


def getParallelResult(domain_symbol, bar_type, parasetlist):
    strategyName = 'LvyiWin_wave'
    # ======================数据准备==============================================
    symbolinfo = DC.SymbolInfo(domain_symbol)
    rawdataDic = DC.getBarBySymbolList(domain_symbol, symbolinfo.getSymbolList(), bar_type)
    foldername = ' '.join([strategyName, domain_symbol, str(bar_type)])
    try:
        os.mkdir(foldername)
    except:
        print ("%s folder already exsist!" % foldername)
    os.chdir(foldername)
    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    l = []
    resultlist = pd.DataFrame(columns=['Setname', 'wave_time_mean', 'wave_time_median',  'wave_time_75quanter',
                                       'wave_height_mean', 'wave_height_median', 'wave_height_75quanter'])

    ma_short_list = parasetlist['MA_Short'].drop_duplicates()
    ma_long_list = parasetlist['MA_Long'].drop_duplicates()
    for ma_short in ma_short_list:
        for ma_long in ma_long_list:
            paraset = {
                'Setname': "ms%d_ml%d" % (ma_short, ma_long),
                'MA_Short': ma_short,
                'MA_Long': ma_long
            }
            #l.append(LvyiWin_wave_cal(strategyName, symbolinfo, bar_type, rawdataDic, paraset))
            l.append(pool.apply_async(LvyiWin_wave_cal, (strategyName, symbolinfo, bar_type, rawdataDic, paraset)))
    pool.close()
    pool.join()
    # 显示结果
    i = 0
    for res in l:
        resultlist.loc[i] = res.get()
        i += 1
    finalresults = ("%s %s %d finalresults.csv" % (strategyName, domain_symbol, bar_type))
    resultlist.to_csv(finalresults)
    return resultlist


if __name__ == '__main__':
    # ====================参数和文件夹设置======================================
    # 文件路径
    upperpath = DC.getUpperPath(2)
    resultpath = upperpath + '\\Results\\'
    os.chdir(resultpath)
    # 取参数集
    parasetlist = pd.read_csv(resultpath + 'ParameterOptSet_simple.csv')
    getParallelResult('SHFE.RB', 600, parasetlist)

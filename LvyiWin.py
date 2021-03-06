# -*- coding: utf-8 -*-
'''
开多条件：
    MA5与MA10金叉，且多空仓差连续3周期变大
平多条件：
    MA_Cross=-1: close<MA20

开空条件：
    KDJ_True=-1:20<K<D
    DMI_True=-1:and PDI<MDI
    MA_True=-1 or BOLL_True=1:and (close<MA20) or close>BOLL.TOP
平空条件：
    MA_Cross=-1:close>MA20
    BOLL_Cross=-1:or close<BOLL.BOTTOM
'''
'''
2017-10-26
    将dfxCross（）函数转移到MA模块中实现
'''
import pandas as pd
import numpy as np
import MA
import DMI
import KDJ
import DATA_CONSTANTS as DC
import ConfigParser
import ResultStatistics as RS


def removeContractSwap(resultlist, contractswaplist):
    results = resultlist
    resultnum = results.shape[0]
    i = 0
    for utc in contractswaplist:
        while i < resultnum:
            result = results.loc[i]
            if result.openutc < utc and result.closeutc > utc:
                results.drop(i, inplace=True)
                i += 1
                break
            if result.openutc > utc and result.closeutc > utc:
                i += 1
                break
            i += 1
    results = results.reset_index(drop=True)
    return results


# def LvyiWin(symbolinfo,rawdata,paraset,contractswaplist,positionRatio=1,initialCash=20000,calcResult=True):
def LvyiWin(symbolinfo, rawdata, paraset):
    setname = paraset['Setname']
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
    # KDJ_True=1:80>k>D
    # KDJ_True=-1:20<K<D
    df_KDJ = KDJ.KDJ(rawdata, N=KDJ_N, M=KDJ_M)
    df_KDJ['KDJ_True'] = 0
    df_KDJ.loc[(KDJ_HLim > df_KDJ['KDJ_K']) & (df_KDJ['KDJ_K'] > df_KDJ['KDJ_D']), 'KDJ_True'] = 1
    df_KDJ.loc[(KDJ_LLim < df_KDJ['KDJ_K']) & (df_KDJ['KDJ_K'] < df_KDJ['KDJ_D']), 'KDJ_True'] = -1

    # 处理DMI数据：DMI_GOLD_CROSS做为DMI的触发信号
    # DMI_True=1:and PDI>MDI
    # DMI_True=-1:and PDI<MDI
    df_DMI = DMI.DMI(rawdata, N=DMI_N, M=DMI_M)
    '''
    #2017-10-26 10:44
        DMI_True的计算，移到DMI模块中执行
    df_DMI['DMI_True']=0
    df_DMI.loc[df_DMI['PDI']> df_DMI['MDI'], 'DMI_True'] = 1
    df_DMI.loc[df_DMI['PDI']< df_DMI['MDI'], 'DMI_True'] = -1
    '''
    # 处理MA数据：MA_Cross做为MA的触发信号
    # MA20_True=1:close>MA20
    # MA20_True=-1:close<MA20
    df_MA = MA.MA(rawdata['close'], MA_Short, MA_Long)
    '''
    #2017-10-26:
        MA的计算转移到MA模块中
    df_MA=pd.DataFrame({'close':rawdata['close']})
    df_MA['MA_Short']=MA.calMA(df_MA['close'],MA_Short)
    df_MA['MA_Long']=MA.calMA(df_MA['close'],MA_Long)
    df_MA['MA_True'],df_MA['MA_Cross']=MA.dfCross(df_MA,'MA_Short','MA_Long')
    
    '''
    '''
    #处理BOLL数据：BOLL_Cross做为BOLL平仓的触发信号
    df_BOLL=BOLL.BOLL(rawdata,N=BOLL_N,M=BOLL_M,P=BOLL_P)
    df_BOLL['BOLL_True']=0
    df_BOLL.loc[df_BOLL['close']< df_BOLL['BOTTOM'], 'BOLL_True'] = -1
    df_BOLL.loc[df_BOLL['close']> df_BOLL['TOP'], 'BOLL_True'] = 1
    #BOLL的金叉，BOLL_True从0变成1是金叉，从0变成-1是死叉
    df_BOLL['BOLL_Cross']=0
    df_BOLL['bigger1'] = df_BOLL['BOLL_True'].shift(1).fillna(0)
    df_BOLL.loc[(df_BOLL['BOLL_True']==1)&(df_BOLL['bigger1']==0), 'BOLL_Cross'] = 1
    df_BOLL.loc[(df_BOLL['BOLL_True']==-1)&(df_BOLL['bigger1']==0), 'BOLL_Cross'] = -1
    df_BOLL.drop('bigger1', axis=1, inplace=True)
    df_BOLL.to_csv('df_BOLL.csv')
    df_BOLL.drop('close',axis=1,inplace=True)
    '''

    df_MA.drop('close', axis=1, inplace=True)
    df = pd.concat([rawdata, df_DMI, df_KDJ, df_MA], axis=1)

    # 找出买卖点：
    # 1.先找出MA金叉的买卖点
    # 2.找到结合判决条件的买点
    # 3.从MA买点中滤出真实买卖点
    # 取出金叉点
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

    # 取出开多序号和开空序号
    openlongindex = df.loc[(df['MA_Cross'] == 1) & (df['KDJ_True'] == 1) & (df['DMI_True'] == 1)].index
    openshortindex = df.loc[(df['MA_Cross'] == -1) & (df['KDJ_True'] == -1) & (df['DMI_True'] == -1)].index

    # 从多仓序列中取出开多序号的内容，即为开多操作
    longopr = longcrosslist.loc[openlongindex]
    longopr['tradetype'] = 1
    longopr.rename(columns={'goldcrosstime': 'opentime',
                            'goldcrossutc': 'openutc',
                            'goldcrossindex': 'openindex',
                            'goldcrossprice': 'openprice',
                            'deathcrosstime': 'closetime',
                            'deathcrossutc': 'closeutc',
                            'deathcrossindex': 'closeindex',
                            'deathcrossprice': 'closeprice'}, inplace=True)

    # 从空仓序列中取出开空序号的内容，即为开空操作
    shortopr = shortcrosslist.loc[openshortindex]
    shortopr['tradetype'] = -1
    shortopr.rename(columns={'deathcrosstime': 'opentime',
                             'deathcrossutc': 'openutc',
                             'deathcrossindex': 'openindex',
                             'deathcrossprice': 'openprice',
                             'goldcrosstime': 'closetime',
                             'goldcrossutc': 'closeutc',
                             'goldcrossindex': 'closeindex',
                             'goldcrossprice': 'closeprice'}, inplace=True)

    # 结果分析
    result = pd.concat([longopr, shortopr])
    result = result.sort_index()
    result = result.reset_index(drop=True)
    result.drop(result.shape[0] - 1, inplace=True)
    # 去掉跨合约的操作
    # 使用单合约，不用再去掉跨合约
    # result = removeContractSwap(result, contractswaplist)

    slip = symbolinfo.getSlip()
    result['ret'] = ((result['closeprice'] - result['openprice']) * result['tradetype']) - slip
    result['ret_r'] = result['ret'] / result['openprice']

    results = {}

    '''
    # 使用单合约，策略核心内不再计算结果
    if calcResult:
        result['commission_fee'], result['per earn'], result['own cash'], result['hands'] = RS.calcResult(result,
                                                                                                          symbolinfo,
                                                                                                          initialCash,
                                                                                                          positionRatio)
    
        endcash = result['own cash'].iloc[-1]
        Annual = RS.annual_return(result)
        Sharpe = RS.sharpe_ratio(result)
        DrawBack = RS.max_drawback(result)[0]
        SR = RS.success_rate(result)
        max_single_loss_rate = abs(result['ret_r'].min())

        results = {
            'Setname':setname,
            'opentimes': result.shape[0],
            'end_cash': endcash,
            'SR': SR,
            'Annual': Annual,
            'Sharpe': Sharpe,
            'DrawBack': DrawBack,
            'max_single_loss_rate': max_single_loss_rate
        }
    closeopr = result.loc[:, 'closetime':'tradetype']
    return result, df, closeopr, results
    '''
    return result


if __name__ == '__main__':
    ini_file = 'LvyiWinConfig.ini'
    conf = ConfigParser.ConfigParser()
    conf.read(ini_file)
    symbol = conf.get('backtest', 'symbols')
    K_MIN = conf.getint('backtest', 'bar_type')
    backtest_startdate = conf.get('backtest', 'start_time')
    backtest_enddate = conf.get('backtest', 'end_time')
    initial_cash = conf.getint('backtest', 'initial_cash')
    margin_rate = conf.getfloat('backtest', 'margin_rate')
    symbolinfo = DC.SymbolInfo(symbol)
    commission_ratio = conf.getfloat('backtest', 'commission_ratio')
    slip = conf.getfloat('backtest', 'slip')

    DMI_N = conf.getint('para', 'DMI_N')
    DMI_M = conf.getint('para', 'DMI_M')
    KDJ_N = conf.getint('para', 'KDJ_N')
    KDJ_M = conf.getint('para', 'KDJ_M')
    KDJ_HLim = conf.getint('para', 'KDJ_HLim')
    KDJ_LLim = conf.getint('para', 'KDJ_LLim')

    MA_Short = conf.getint('para', 'MA_Short')
    MA_Long = conf.getint('para', 'MA_Long')

    '''
    BOLL_N=conf.getint('para','BOLL_N')
    BOLL_M=conf.getint('para','BOLL_M')
    BOLL_P=conf.getint('para','BOLL_P')
    '''
    rawdata = DC.getBarData(symbol, K_MIN, backtest_startdate, backtest_enddate).reset_index(drop=True)
    contractswaplist = DC.getContractSwaplist(symbol)
    swaplist = np.array(contractswaplist.swaputc)
    paraset = {
        'symbol': symbol,
        'Setname': 'sigletest',
        'KDJ_N': KDJ_N,
        'KDJ_M': KDJ_M,
        'KDJ_HLim': KDJ_HLim,
        'KDJ_LLim': KDJ_LLim,
        'DMI_N': DMI_N,
        'DMI_M': DMI_M,
        'MA_Short': MA_Short,
        'MA_Long': MA_Long,
        'initial_cash': initial_cash,
        'commission_ratio': commission_ratio,
        'margin_rate': margin_rate,
        'slip': slip
    }
    result, df, closeopr, results = LvyiWin(symbolinfo, rawdata, paraset, swaplist)
    print results
    result.to_csv(symbol + str(K_MIN) + 'result.csv')
    # df.to_csv(symbol+str(K_MIN)+'all.csv')
    # closeopr.to_csv(symbol+str(K_MIN)+'closeopr.csv')

# -*- coding: utf-8 -*-
'''
3MA:
    短中MA金叉死叉做开平仓，长MA做过滤
    长MA以上只做多，长MA以下只做空
'''
import pandas as pd
import numpy as np
import MA
#import DMI
#import KDJ
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


#def Lvyi3MAWin(symbolinfo, rawdata, paraset, contractswaplist, positionRatio,initialCash,calcResult=True):
def Lvyi3MAWin(symbolinfo, rawdata, paraset):
    setname = paraset['Setname']
    MA_Short = paraset['MA_Short']
    MA_Mid = paraset['MA_Mid']
    MA_Long = paraset['MA_Long']
    rawdata['Unnamed: 0'] = range(rawdata.shape[0])
    beginindex = rawdata.ix[0, 'Unnamed: 0']

    #df_MA = MA.MA(rawdata['close'], MA_Short, MA_Mid)
    #df_MA.drop('close', axis=1, inplace=True)
    #df = pd.concat([rawdata, df_MA], axis=1)
    df = rawdata
    df['MA_Short'] = MA.calMA(df['close'],MA_Short)
    df['MA_Mid'] = MA.calMA(df['close'],MA_Mid)
    df['MA_Long'] = MA.calMA(df['close'],MA_Long)
    df['MA_True'],df['MA_Cross'] = MA.dfCross(df,'MA_Short','MA_Mid')

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
    openlongindex = df.loc[(df['MA_Cross'] == 1) & (df['MA_Short'] >= df['MA_Long']) & (df['MA_Mid'] >= df['MA_Long'])].index
    openshortindex = df.loc[(df['MA_Cross'] == -1) & (df['MA_Short'] <= df['MA_Long']) & (df['MA_Mid'] <= df['MA_Long'])].index

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
    #result = removeContractSwap(result, contractswaplist)

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
    #参数配置
    strategyName='Lvyi3MAWin'
    exchange_id = 'SHFE'
    sec_id = 'RB'
    symbol = '.'.join([exchange_id, sec_id])
    K_MIN = 600
    starttime = '2016-01-01 00:00:00'
    endtime = '2018-01-01 00:00:00'
    symbolinfo=DC.SymbolInfo(symbol)
    # 优化参数
    MA_Short = 5
    MA_Mid = 15
    MA_Long = 30

    rawdata = DC.getBarData(symbol, K_MIN, starttime, endtime).reset_index(drop=True)
    contractswaplist = DC.getContractSwaplist(symbol)
    swaplist = np.array(contractswaplist.swaputc)
    paraset = {
        'Setname':'singletest',
        'symbol': symbol,
        'MA_Short': MA_Short,
        'MA_Mid': MA_Mid,
        'MA_Long': MA_Long,
    }
    result, df, closeopr, results = Lvyi3MAWin(symbolinfo, rawdata, paraset,swaplist, 1,20000)
    print results
    result.to_csv(symbolinfo.symbol + str(K_MIN) + 'result.csv')
# -*- coding: utf-8 -*-
'''
3MA:
    短中MA金叉死叉做开平仓，长MA做过滤
    长MA以上只做多，长MA以下只做空
'''
import pandas as pd
import numpy as np
import MA
import DMI
import DATA_CONSTANTS as DC
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


def LvyiNoKDJWin(symbolinfo, setname,rawdata, paraset, contractswaplist, calcResult=True):
    print setname
    DMI_N=paraset['DMI_N']
    DMI_M=paraset['DMI_M']
    MA_Short=paraset['MA_Short']
    MA_Long=paraset['MA_Long']

    beginindex = rawdata.ix[0, 'Unnamed: 0']

    df_DMI = DMI.DMI(rawdata, N=DMI_N, M=DMI_M)
    df_MA = MA.MA(rawdata['close'], MA_Short, MA_Long)
    df_MA.drop('close', axis=1, inplace=True)
    df = pd.concat([rawdata, df_DMI, df_MA], axis=1)

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

    #取出开多序号和开空序号
    openlongindex=df.loc[(df['MA_Cross']==1)&(df['DMI_True']==1)].index
    openshortindex=df.loc[(df['MA_Cross']==-1)&(df['DMI_True']==-1)].index

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
    result = removeContractSwap(result, contractswaplist)

    initial_cash = 20000
    margin_rate = 0.2
    slip = symbolinfo.getSlip()
    multiplier = symbolinfo.getMultiplier()
    poundgeType, poundgeFee, poundgeRate = symbolinfo.getPoundage()

    result['ret'] = ((result['closeprice'] - result['openprice']) * result['tradetype']) - slip
    result['ret_r'] = result['ret'] / result['openprice']
    results = {}

    if calcResult:
        firsttradecash = initial_cash / margin_rate
        result['commission_fee'] = 0
        if poundgeType == symbolinfo.POUNDGE_TYPE_RATE:
            result.ix[0, 'commission_fee'] = firsttradecash * poundgeRate * 2
        else:
            result.ix[0, 'commission_fee'] = firsttradecash / (multiplier * result.ix[0, 'openprice']) * poundgeFee * 2
        result['per earn'] = 0  # 单笔盈亏
        result['own cash'] = 0  # 自有资金线
        result['trade money'] = 0  # 杠杆后的可交易资金线

        result.ix[0, 'per earn'] = firsttradecash * result.ix[0, 'ret_r']
        result.ix[0, 'own cash'] = initial_cash + result.ix[0, 'per earn'] - result.ix[0, 'commission_fee']
        result.ix[0, 'trade money'] = result.ix[0, 'own cash'] / margin_rate
        oprtimes = result.shape[0]
        for i in np.arange(1, oprtimes):
            # 根据手续费类型计算手续费
            if poundgeType == symbolinfo.POUNDGE_TYPE_RATE:
                commission = result.ix[i - 1, 'trade money'] * poundgeRate * 2
            else:
                commission = result.ix[i - 1, 'trade money'] / (multiplier * result.ix[i, 'openprice']) * poundgeFee * 2
            perearn = result.ix[i - 1, 'trade money'] * result.ix[i, 'ret_r']
            owncash = result.ix[i - 1, 'own cash'] + perearn - commission
            result.ix[i, 'own cash'] = owncash
            result.ix[i, 'commission_fee'] = commission
            result.ix[i, 'per earn'] = perearn
            result.ix[i, 'trade money'] = owncash / margin_rate

        endcash = result.ix[oprtimes - 1, 'own cash']
        Annual = RS.annual_return(result)
        Sharpe = RS.sharpe_ratio(result)
        DrawBack = RS.max_drawback(result)[0]
        SR = RS.success_rate(result)
        max_single_loss_rate = abs(result['ret_r'].min())

        results = {
            'Setname':setname,
            'MA_Short':MA_Short,
            'MA_Long':MA_Long,
            'DMI_N':DMI_N,
            'opentimes': oprtimes,
            'end_cash': endcash,
            'SR': SR,
            'Annual': Annual,
            'Sharpe': Sharpe,
            'DrawBack': DrawBack,
            'max_single_loss_rate': max_single_loss_rate
        }
    closeopr = result.loc[:, 'closetime':'tradetype']
    return result, df, closeopr, results


if __name__ == '__main__':
    #参数配置
    strategyName='LvyiNoKDJWin'
    exchange_id = 'SHFE'
    sec_id = 'RB'
    symbol = '.'.join([exchange_id, sec_id])
    K_MIN = 600
    starttime = '2016-01-01 00:00:00'
    endtime = '2018-01-01 00:00:00'
    symbolinfo=DC.SymbolInfo(symbol)
    # 优化参数
    MA_Short = 5
    MA_Long = 30
    DMI_N = 26

    rawdata = DC.getBarData(symbol, K_MIN, starttime, endtime).reset_index(drop=True)
    contractswaplist = DC.getContractSwaplist(symbol)
    swaplist = np.array(contractswaplist.swaputc)
    paraset = {
        'symbol': symbol,
        'MA_Short': MA_Short,
        'MA_Long': MA_Long,
        'DMI_N':DMI_N,
        'DMI_M':6
    }
    setname= "testset"
    result, df, closeopr, results = LvyiNoKDJWin(symbolinfo, setname,rawdata, paraset, swaplist)
    print results
    result.to_csv(symbolinfo.symbol + str(K_MIN) + 'result.csv')
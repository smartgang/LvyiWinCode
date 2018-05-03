# -*- coding: utf-8 -*-
'''
多策略结果联合统计
'''
import pandas as pd
import DATA_CONSTANTS as DC
import os
import ResultStatistics as RS
openheader=['opentime','openutc','openindex','openprice','tradetype','ret','ret_r']
new_openheader=['opentime','openutc','openindex','openprice','tradetype','new_ret','new_ret_r']
closeheaders=['closetime','closeutc','closeindex','closeprice','tradetype','ret','ret_r']
new_closeheaders=['new_closetime','new_closeutc','new_closeindex','new_closeprice','tradetype','new_ret','new_ret_r']

def sortOpr(strategyList):
    resultDf = pd.DataFrame()
    for st in strategyList:
        symbol=st['symbol']
        symbolinfo=DC.SymbolInfo(symbol)
        if st['new']:
            opendf = pd.read_csv(st['filePath'] + st['fileName'], usecols=new_openheader)
            closedf = pd.read_csv(st['filePath'] + st['fileName'], usecols=new_closeheaders)
            opendf.rename(columns={'opentime': 'oprtime',
                                   'openutc': 'oprutc',
                                   'openindex': 'oprindex',
                                   'openprice': 'oprprice',
                                   'new_ret': 'ret',
                                   'new_ret_r': 'ret_r'}, inplace=True)
            opendf['oprtype'] = 1  # 1表示开仓
            closedf.rename(columns={'new_closetime': 'oprtime',
                                    'new_closeutc': 'oprutc',
                                    'new_closeindex': 'oprindex',
                                    'new_closeprice': 'oprprice',
                                    'new_ret': 'ret',
                                    'new_ret_r': 'ret_r'}, inplace=True)
            closedf['oprtype'] = -1  # -1表示平仓
        else:
            opendf = pd.read_csv(st['filePath'] + st['fileName'], usecols=openheader)
            closedf = pd.read_csv(st['filePath'] + st['fileName'], usecols=closeheaders)
            opendf.rename(columns={'opentime': 'oprtime',
                                   'openutc': 'oprutc',
                                   'openindex': 'oprindex',
                                   'openprice': 'oprprice',
                                   'ret': 'ret',
                                   'ret_r': 'ret_r'}, inplace=True)
            opendf['oprtype'] = 1  # 1表示开仓
            closedf.rename(columns={'closetime': 'oprtime',
                                    'closeutc': 'oprutc',
                                    'closeindex': 'oprindex',
                                    'closeprice': 'oprprice',
                                    'ret': 'ret',
                                    'ret_r': 'ret_r'}, inplace=True)
            closedf['oprtype'] = -1  # -1表示平仓
        df = pd.concat([opendf, closedf])
        df.set_index('oprutc', inplace=True)
        df['strategy'] = st['name']
        df['positionRate'] = st['positionRate']
        df['multiplier'] = symbolinfo.getMultiplier()  # 乘数
        df['poundgeType'], df['poundgeFee'], df['poundgeRate'] = symbolinfo.getPoundage()  # 手续费率
        df['marginRatio'] = symbolinfo.getMarginRatio()  # 保证金率
        resultDf = pd.concat([resultDf, df])
    resultDf.sort_index(inplace=True)
    resultDf.reset_index(drop=False, inplace=True)
    #resultDf.to_csv('resultCostatistics.csv')
    #print resultDf.head(10)
    return resultDf

def coStatistics(strategyList,initialCash):
    oprdf=sortOpr(strategyList)
    oprdf['commission_fee'] = 0 #手续费
    oprdf['per earn'] = 0  # 单笔盈亏
    oprdf['own cash'] = 0  # 自有资金线
    oprdf['hands'] = 0 #每次手数
    #计算第一次交易的结果
    availableFund = initialCash*oprdf.ix[0,'positionRate']
    cashPerHand = oprdf.ix[0,'oprprice'] * oprdf.ix[0,'multiplier']
    hands=availableFund//(cashPerHand*oprdf.ix[0,'marginRatio'])
    if oprdf.ix[0,'poundgeType'] == 'rate':
        oprdf.ix[0, 'commission_fee'] = cashPerHand * hands * oprdf.ix[0,'poundgeRate'] * 2
    else:
        oprdf.ix[0, 'commission_fee'] = hands * oprdf.ix[0,'poundgeFee'] * 2
    oprdf.ix[0, 'per earn'] = oprdf.ix[0, 'ret'] * hands * oprdf.ix[0,'multiplier']
    oprdf.ix[0, 'own cash'] = initialCash + oprdf.ix[0, 'per earn'] - oprdf.ix[0, 'commission_fee']
    oprdf.ix[0, 'hands'] = hands

    #计算后续交易的结果
    oprtimes = oprdf.shape[0]
    for i in range(1, oprtimes):
        if oprdf.ix[i,'oprtype']== 1:#开仓只要复制资金
            oprdf.ix[i,'own cash']=oprdf.ix[i-1,'own cash']
        else:
            lastOwnCash=oprdf.ix[i-1,'own cash']
            availableFund = lastOwnCash * oprdf.ix[i,'positionRate'] #本次可用资金等于上一次操作后的资金*持仓率
            cashPerHand = oprdf.ix[i, 'oprprice'] * oprdf.ix[i,'multiplier']
            hands = availableFund // (cashPerHand * oprdf.ix[i,'marginRatio'])
            if oprdf.ix[i,'poundgeType'] == 'rate':
                commission = cashPerHand * hands * oprdf.ix[i,'poundgeRate'] * 2
            else:
                commission = hands * oprdf.ix[i,'poundgeFee'] * 2
            oprdf.ix[i,'commission_fee'] = commission
            oprdf.ix[i, 'per earn'] = oprdf.ix[i, 'ret'] * hands * oprdf.ix[i,'multiplier']
            oprdf.ix[i, 'own cash'] = lastOwnCash + oprdf.ix[i, 'per earn'] - commission
            oprdf.ix[i, 'hands'] = hands
    endcash = oprdf['own cash'].iloc[-1]
    Annual = RS.annual_return(oprdf, cash_col='own cash', closeutc_col='oprutc',openutc_col='oprutc')
    Sharpe = RS.sharpe_ratio(oprdf, cash_col='own cash', closeutc_col='oprutc', retr_col='ret_r',openutc_col='oprutc')
    DrawBack = RS.max_drawback(oprdf, cash_col='own cash',opentime_col='oprtime')[0]
    SR = RS.success_rate(oprdf, ret_col='ret')
    print ("endcash:%f"%endcash,
           "Annual:%f"%Annual,
           "Sharpe:%f"%Sharpe,
           "DrawBack:%f"%DrawBack,
           "SuccessRate:%f"%SR)
    return oprdf

if __name__=="__main__":
    strategyList=[
        {
            'name':'Lvyi3MAWin SHFE.RB 900',
            'symbol':'SHFE.RB',
            'positionRate':0.5,
            'filePath':'costatistics\\',
            'fileName':'Lvyi3MAWin SHFE.RB900_Rank1_win12_oprResult.csv',
            'new':True},
        {
            'name': 'LvyiWin SHFE.RB 3600',
            'symbol': 'SHFE.RB',
            'positionRate': 0.5,
            'filePath': 'costatistics\\',
            'fileName': 'Lvyi3MAWin SHFE.RB3600_Rank7_win11_oprResult.csv',
            'new':True}
    ]
    upperpath = DC.getUpperPath(1)
    resultpath = upperpath + '\\Results\\'
    os.chdir(resultpath)
    initialCash=200000
    oprdf=coStatistics(strategyList,initialCash)
    oprdf.to_csv('resultCostatistics.csv')
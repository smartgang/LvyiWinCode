# -*- coding: utf-8 -*-
import LvyiWin
import pandas as pd
import numpy
import ConfigParser
import DATA_CONSTANTS as DC

ini_file = 'LvyiWinConfig.ini'
conf = ConfigParser.ConfigParser()
conf.read(ini_file)
symbol = conf.get('backtest', 'symbols')
K_MIN = conf.getint('backtest', 'bar_type')
backtest_startdate = conf.get('backtest', 'start_time')
backtest_enddate = conf.get('backtest', 'start_time')
initial_cash = conf.getint('backtest', 'initial_cash')
commission_ratio = conf.getfloat('backtest', 'commission_ratio')
margin_rate=conf.getfloat('backtest','margin_rate')

parasetlist=pd.read_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\ParameterOptSet_1.csv')
parasetlen=parasetlist.shape[0]
rawdata = DC.GET_DATA(DC.DATA_TYPE_RAW, symbol, K_MIN, backtest_startdate).reset_index(drop=True)
resultlist=pd.DataFrame(columns=['Setname','MA_Short','MA_Long','KDJ_N','DMI_N','opentimes','successrate', 'initial_cash','commission_fee', 'end_cash','min_cash','max_cash'])
for i in numpy.arange(0, parasetlen):
    setname=parasetlist.ix[i,'Setname']
    kdj_n=parasetlist.ix[i,'KDJ_N']
    dmi_n=parasetlist.ix[i,'DMI_N']
    ma_short=parasetlist.ix[i, 'MA_Short']
    ma_long=parasetlist.ix[i,'MA_Long']
    paraset = {
        'KDJ_N': kdj_n,
        'KDJ_M': 3,
        'KDJ_HLim': 85,
        'KDJ_LLim': 15,
        'DMI_N': dmi_n,
        'DMI_M': 6,
        'MA_Short': ma_short,
        'MA_Long': ma_long,
        'initial_cash': initial_cash,
        'commission_ratio': commission_ratio,
        'margin_rate':margin_rate
    }
    result, df, closeopr,results = LvyiWin.LvyiWin(rawdata, paraset)
    r=[
        setname,
        ma_short,
        ma_long,
        kdj_n,
        dmi_n,
        results['opentimes'],
        results['successrate'],
        results['initial_cash'],
        results['commission_fee'],
        results['end_cash'],
        results['min_cash'],
        results['max_cash']
    ]
    resultlist.loc[i]=r
    result.to_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\'+symbol + str(K_MIN) +' '+setname+ ' result.csv')
    #df.to_csv('Results\\'+symbol + str(K_MIN) +' '+setname+ ' all.csv')
    #closeopr.to_csv('Results\\'+symbol + str(K_MIN) +' '+setname+ 'closeopr.csv')
    print setname+" finished"
print resultlist
resultlist.to_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\'+symbol+ str(K_MIN)+' finanlresults.csv')

def getParallelResult(rawdata,setname,para):
    result ,df ,closeopr,results = LvyiWin.LvyiWin(rawdata, para)
    r = [
        setname,
        para['MA_Short'],
        para['MA_Long'],
        para['KDJ_N'],
        para['DMI_N'],
        results['opentimes'],
        results['successrate'],
        results['initial_cash'],
        results['commission_fee'],
        results['end_cash'],
        results['min_cash'],
        results['max_cash']
    ]
    result.to_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\' + symbol + str(K_MIN) + ' ' + setname + ' result.csv')
    return r

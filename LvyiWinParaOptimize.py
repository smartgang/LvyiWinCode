# -*- coding: utf-8 -*-
import LvyiWin
import pandas as pd
import numpy
import ConfigParser
import DATA_CONSTANTS as DC
import multiprocessing


def getParallelResult(symbol,K_MIN,backtest_startdate,setname,para):
    rawdata = DC.GET_DATA(DC.DATA_TYPE_RAW, symbol, K_MIN, backtest_startdate).reset_index(drop=True)
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
    print setname + " finished"
    result.to_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\' + symbol + str(K_MIN) + ' ' + setname + ' result.csv')
    del result
    return r

if __name__ == '__main__':
    ini_file = 'LvyiWinConfig.ini'
    conf = ConfigParser.ConfigParser()
    conf.read(ini_file)
    symbol = conf.get('backtest', 'symbols')
    K_MIN = conf.getint('backtest', 'bar_type')
    backtest_startdate = conf.get('backtest', 'start_time')
    backtest_enddate = conf.get('backtest', 'start_time')
    initial_cash = conf.getint('backtest', 'initial_cash')
    commission_ratio = conf.getfloat('backtest', 'commission_ratio')
    margin_rate = conf.getfloat('backtest', 'margin_rate')

    parasetlist=pd.read_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\ParameterOptSet_1.csv')
    parasetlen=parasetlist.shape[0]
    resultlist=pd.DataFrame(columns=['Setname','MA_Short','MA_Long','KDJ_N','DMI_N','opentimes','successrate', 'initial_cash','commission_fee', 'end_cash','min_cash','max_cash'])

    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)
    l = []

    for i in numpy.arange(0, parasetlen):
        #rawdata = DC.GET_DATA(DC.DATA_TYPE_RAW, symbol, K_MIN, backtest_startdate).reset_index(drop=True)
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
        l.append(pool.apply_async(getParallelResult, (symbol,K_MIN,backtest_startdate,setname,paraset)))
    pool.close()
    pool.join()

    # 显示结果
    i = 0
    for res in l:
        resultlist.loc[i]=res.get()
        i+=1
    print resultlist
    resultlist.to_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\'+symbol+ str(K_MIN)+' finanlresults.csv')

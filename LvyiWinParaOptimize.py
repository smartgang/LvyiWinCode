# -*- coding: utf-8 -*-
import LvyiWin
import pandas as pd
import numpy as np
import ConfigParser
import DATA_CONSTANTS as DC
import multiprocessing


def getParallelResult(symbol,K_MIN,backtest_startdate,backtest_enddate,setname,para,contractswaplist):
    rawdata = DC.getBarData(symbol, K_MIN, backtest_startdate,backtest_enddate,).reset_index(drop=True)
    result ,df ,closeopr,results = LvyiWin.LvyiWin(rawdata, para,contractswaplist)
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
        results['max_cash'],
        results['max_single_loss_rate'],
        results['max_retrace_rate']
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
    backtest_enddate = conf.get('backtest', 'end_time')
    initial_cash = conf.getint('backtest', 'initial_cash')
    commission_ratio = conf.getfloat('backtest', 'commission_ratio')
    margin_rate = conf.getfloat('backtest', 'margin_rate')
    slip=conf.getfloat('backtest','slip')

    parasetlist=pd.read_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\ParameterOptSet1.csv')
    parasetlen=parasetlist.shape[0]
    resultlist=pd.DataFrame(columns=
                            ['Setname','MA_Short','MA_Long','KDJ_N','DMI_N','opentimes','successrate',
                             'initial_cash','commission_fee', 'end_cash','min_cash','max_cash','max_single_loss_rate','max_retrace_rate'])

    contractswaplist = DC.getContractSwaplist(symbol)
    swaplist = np.array(contractswaplist.swaputc)


    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    l = []

    for i in np.arange(0, parasetlen):
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
            'margin_rate':margin_rate,
            'slip':slip
        }
        l.append(pool.apply_async(getParallelResult, (symbol,K_MIN,backtest_startdate,backtest_enddate,setname,paraset,swaplist)))
    pool.close()
    pool.join()

    # 显示结果
    i = 0
    for res in l:
        resultlist.loc[i]=res.get()
        i+=1
    print resultlist
    resultlist.to_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\'+symbol+ str(K_MIN)+' finanlresults.csv')

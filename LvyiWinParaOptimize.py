# -*- coding: utf-8 -*-
import LvyiWin
import pandas as pd
import numpy as np
import ConfigParser
import DATA_CONSTANTS as DC
import multiprocessing
import os

def getParallelResult(symbolinfo,K_MIN,backtest_startdate,backtest_enddate,setname,para,contractswaplist):
    rawdata = DC.getBarData(symbolinfo.symbol, K_MIN, backtest_startdate,backtest_enddate,).reset_index(drop=True)
    result ,df ,closeopr,results = LvyiWin.LvyiWin(symbolinfo,rawdata, para,contractswaplist)
    r = [
        setname,
        para['MA_Short'],
        para['MA_Long'],
        para['KDJ_N'],
        para['DMI_N'],
        results['opentimes'],
        results['end_cash'],
        results['SR'],
        results['Annual'],
        results['Sharpe'],
        results['DrawBack'],
        results['max_single_loss_rate']
    ]
    print setname + " finished"
    result.to_csv(symbolinfo.symbol + str(K_MIN) + ' ' + setname + ' result.csv')
    del result
    return r

if __name__ == '__main__':

    #参数配置
    K_MIN = 600
    backtest_startdate = '2016-01-01 00:00:00'
    backtest_enddate = '2018-03-31 23:59:59'
    symbollist=['SHFE.RB']
    upperpath = DC.getUpperPath(uppernume=1)
    resultpath = upperpath + "\\Results\\"

    for symbol in symbollist:
        #exchange_id = 'DCE'
        #sec_id='JM'
        exchange_id,sec_id =symbol.split('.')
        #symbol = '.'.join([exchange_id, sec_id])

        initial_cash=20000
        commission_ratio=0.00012 #自适应手续费，这个值其实没有意义
        margin_rate=0.2

        symbolinfo=DC.SymbolInfo(symbol)
        slip = symbolinfo.getSlip()

        #文件路径
        foldername = ' '.join([exchange_id, sec_id, str(K_MIN)])
        rawdatapath=resultpath+foldername+'\\'
        datapath = resultpath + foldername + '\\'
        parasetlist = pd.read_csv(resultpath+'ParameterOptSet1.csv')

        #创建结果文件夹
        try:
            os.chdir(resultpath)
            os.mkdir(foldername)
        except:
            print ('%s folder already exist!'%foldername)
        #进入工作目录
        os.chdir(datapath)

        parasetlen=parasetlist.shape[0]
        resultlist=pd.DataFrame(columns=
                                ['Setname','MA_Short','MA_Long','KDJ_N','DMI_N','opentimes','end_cash',
                                 'SR','Annual', 'Sharpe','DrawBack','max_single_loss_rate'])

        contractswaplist = DC.getContractSwaplist(symbol)
        swaplist = np.array(contractswaplist.swaputc)
        '''
        for i in np.arange(0,10):
            setname = parasetlist.ix[i, 'Setname']
            kdj_n = parasetlist.ix[i, 'KDJ_N']
            dmi_n = parasetlist.ix[i, 'DMI_N']
            ma_short = parasetlist.ix[i, 'MA_Short']
            ma_long = parasetlist.ix[i, 'MA_Long']
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
                'margin_rate': margin_rate,
                'slip': slip
            }
            getParallelResult(symbolinfo, K_MIN, backtest_startdate, backtest_enddate, setname, paraset, swaplist)
        '''
        # 多进程优化，启动一个对应CPU核心数量的进程池
        pool = multiprocessing.Pool(multiprocessing.cpu_count()-1)
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
            l.append(pool.apply_async(getParallelResult, (symbolinfo,K_MIN,backtest_startdate,backtest_enddate,setname,paraset,swaplist)))
        pool.close()
        pool.join()

        # 显示结果
        i = 0
        for res in l:
            resultlist.loc[i]=res.get()
            i+=1
        print resultlist
        resultlist.to_csv(symbol+ str(K_MIN)+' finanlresults.csv')

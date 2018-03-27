# -*- coding: utf-8 -*-
'''
Lvyi3MAWin策略多进程参数优化
'''
import Lvyi3MAWin
import pandas as pd
import numpy as np
import os
import DATA_CONSTANTS as DC
import multiprocessing

if __name__=='__main__':
    #====================参数和文件夹设置======================================
    #参数设置
    strategyName='Lvyi3MAWin'
    exchange_id = 'SHFE'
    sec_id='RB'
    K_MIN = 600
    symbol = '.'.join([strategyName,exchange_id, sec_id])
    startdate='2016-01-01'
    enddate = '2017-12-31'

    #文件路径
    upperpath=DC.getUpperPath(2)
    foldername = ' '.join([exchange_id, sec_id, str(K_MIN)])
    resultpath=upperpath+"\\Results\\"
    os.chdir(resultpath)
    try:
        os.mkdir(foldername)
    except:
        print ("%s folder already exsist!" %foldername)
    os.chdir(foldername)

    # ======================数据准备==============================================
    #取参数集
    parasetlist=pd.read_csv(resultpath+'ParameterOptSet3MA.csv')
    paranum=parasetlist.shape[0]
    # 取合约信息
    symbolInfo = DC.SymbolInfo(symbol)

    # 取跨合约数据
    contractswaplist = DC.getContractSwaplist(symbol)
    swaplist = np.array(contractswaplist.swaputc)

    #取K线数据
    rawdata = DC.getBarData(symbol, K_MIN, startdate+' 00:00:00', enddate+' 23:59:59').reset_index(drop=True)
    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    l = []
    resultlist = pd.DataFrame(columns=
                              ['Setname', 'MA_Short', 'MA_Mid', 'MA_Long', 'opentimes', 'end_cash', 'SR', 'Annual','Sharpe','DrawBack',
                               'max_single_loss_rate'])
    for i in range(0, paranum):
        setname = parasetlist.ix[i, 'Setname']
        ma_short = parasetlist.ix[i, 'MA_Short']
        ma_mid = parasetlist.ix[i, 'MA_Mid']
        ma_long = parasetlist.ix[i, 'MA_Long']
        macdParaSet = {
            'MA_Short': ma_short,
            'MA_Mid': ma_mid,
            'MA_Long': ma_long,
        }
        #Lvyi3MAWin(symbolInfo,rawdata,parasetlist,swaplist)
        l.append(pool.apply_async(Lvyi3MAWin,(symbolInfo,rawdata,parasetlist,swaplist)))
    pool.close()
    pool.join()

    # 显示结果
    i = 0
    for res in l:
        resultlist.loc[i] = res.get()
        i += 1
    print resultlist
    finalresults=("%s %d finalresults.csv"%(symbol,K_MIN))
    resultlist.to_csv(finalresults)
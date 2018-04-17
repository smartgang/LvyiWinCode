# -*- coding: utf-8 -*-
'''
LvyiNoKdJWin策略多进程参数优化
'''
import LvyiWin
import pandas as pd
import numpy as np
import os
import DATA_CONSTANTS as DC
import multiprocessing
import LvyiWin_Parameter


def getResult(symbolinfo,K_MIN,setname,rawdata,para,contractswaplist):
    result ,df ,closeopr,results = LvyiWin.LvyiWin(rawdata=rawdata, paraset=para,contractswaplist=contractswaplist)
    result.to_csv(symbolinfo.symbol + str(K_MIN) + ' ' + setname + ' result.csv')
    del result
    print results
    return results

def getParallelResult(strategyParameter,resultpath,parasetlist,paranum):

    strategyName = strategyParameter['strategyName']
    exchange_id = strategyParameter['exchange_id']
    sec_id = strategyParameter['sec_id']
    K_MIN = strategyParameter['K_MIN']
    startdate = strategyParameter['startdate']
    enddate = strategyParameter['enddate']
    symbol = '.'.join([exchange_id, sec_id])

    # ======================数据准备==============================================
    # 取合约信息
    symbolInfo = DC.SymbolInfo(symbol)
    slip = symbolInfo.getSlip()
    # 取跨合约数据
    contractswaplist = DC.getContractSwaplist(symbol)
    swaplist = np.array(contractswaplist.swaputc)

    # 取K线数据
    rawdata = DC.getBarData(symbol, K_MIN, startdate + ' 00:00:00', enddate + ' 23:59:59').reset_index(drop=True)
    foldername = ' '.join([strategyName, exchange_id, sec_id, str(K_MIN)])
    try:
        os.chdir(resultpath)
        os.mkdir(foldername)
    except:
        print ("%s folder already exsist!" %foldername)
    os.chdir(foldername)

    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    l = []
    resultlist = pd.DataFrame(columns=
                              ['Setname', 'MA_Short', 'MA_Long', 'KDJ_N', 'DMI_N', 'opentimes', 'end_cash',
                               'SR', 'Annual', 'Sharpe', 'DrawBack', 'max_single_loss_rate'])
    for i in range(0, paranum):
        setname = parasetlist.ix[i, 'Setname']
        kdj_n = parasetlist.ix[i, 'KDJ_N']
        dmi_n = parasetlist.ix[i, 'DMI_N']
        ma_short = parasetlist.ix[i, 'MA_Short']
        ma_long = parasetlist.ix[i, 'MA_Long']
        paraset = {
            'Setname':setname,
            'KDJ_N': kdj_n,
            'KDJ_M': 3,
            'KDJ_HLim': 85,
            'KDJ_LLim': 15,
            'DMI_N': dmi_n,
            'DMI_M': 6,
            'MA_Short': ma_short,
            'MA_Long': ma_long,
            'initial_cash': 20000,
            'commission_ratio': 0.00012,
            'margin_rate': 0.2,
            'slip': slip
        }
        #l.append(getResult(symbolInfo, K_MIN, setname, rawdata, paraset, swaplist))
        l.append(pool.apply_async(getResult, (symbolInfo, K_MIN, setname, rawdata, paraset, swaplist)))
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
    return resultlist

if __name__=='__main__':
    #====================参数和文件夹设置======================================
    #文件路径
    upperpath=DC.getUpperPath(LvyiWin_Parameter.folderLevel)
    resultpath = upperpath + LvyiWin_Parameter.resultFolderName

    # 取参数集
    parasetlist = pd.read_csv(resultpath + LvyiWin_Parameter.parasetname)
    paranum = parasetlist.shape[0]
    #参数设置
    strategyParameterSet=[]
    if not LvyiWin_Parameter.symbol_KMIN_opt_swtich:
        #单品种单周期模式
        paradic={
        'strategyName':LvyiWin_Parameter.strategyName,
        'exchange_id': LvyiWin_Parameter.exchange_id,
        'sec_id': LvyiWin_Parameter.sec_id,
        'K_MIN': LvyiWin_Parameter.K_MIN,
        'startdate': LvyiWin_Parameter.startdate,
        'enddate' : LvyiWin_Parameter.enddate,
        }
        strategyParameterSet.append(paradic)
    else:
        #多品种多周期模式
        symbolset = pd.read_excel(resultpath + LvyiWin_Parameter.symbol_KMIN_set_filename)
        symbolsetNum=symbolset.shape[0]
        for i in range(symbolsetNum):
            exchangeid=symbolset.ix[i,'exchange_id']
            secid=symbolset.ix[i,'sec_id']
            strategyParameterSet.append({
                'strategyName': symbolset.ix[i,'strategyName'],
                'exchange_id': exchangeid,
                'sec_id': secid,
                'K_MIN': symbolset.ix[i,'K_MIN'],
                'startdate': symbolset.ix[i,'startdate'],
                'enddate': symbolset.ix[i,'enddate'],
            }
            )

    allsymbolresult = pd.DataFrame(columns=
                                   ['Setname', 'MA_Short', 'MA_Long', 'KDJ_N', 'DMI_N', 'opentimes', 'end_cash',
                                    'SR', 'Annual', 'Sharpe', 'DrawBack', 'max_single_loss_rate',
                               'strategyName','exchange_id','sec_id','K_MIN'])
    for strategyParameter in strategyParameterSet:
        r=getParallelResult(strategyParameter,resultpath,parasetlist,paranum)
        r['strategyName']=strategyParameter['strategyName']
        r['exchange_id']=strategyParameter['exchange_id']
        r['sec_id'] = strategyParameter['sec_id']
        r['K_MIN'] = strategyParameter['K_MIN']
        allsymbolresult=pd.concat([allsymbolresult,r])
    allsymbolresult.reset_index(drop=False,inplace=True)
    os.chdir(resultpath)
    allsymbolresult.to_csv(LvyiWin_Parameter.strategyName+"_symbol_KMIN_results.csv")
# -*- coding: utf-8 -*-
'''
LvyiNoKdJWin策略多进程参数优化
'''
from LvyiWin import LvyiWin
import pandas as pd
import numpy as np
import os
import DATA_CONSTANTS as DC
import ResultStatistics as RS
import multiprocessing
import LvyiWin_Parameter as Parameter
import time

def getResult(strategyName, symbolinfo, K_MIN, setname, rawdataDic, para, result_para_dic, indexcols,timestart):
    time1 = time.time()
    print ("%s Enter %.3f" % (setname, time1-timestart))

    initialCash = result_para_dic['initialCash']
    positionRatio = result_para_dic['positionRatio']
    remove_polar_switch = result_para_dic['remove_polar_switch']
    remove_polaar_rate = result_para_dic['remove_polaar_rate']

    symbollist = symbolinfo.getSymbolList()
    symbolDomainDic = symbolinfo.getSymbolDomainDic()
    result = pd.DataFrame()
    last_domain_utc = None
    print para['Setname']
    for symbol in symbollist:
        if last_domain_utc:
            # 如果上一个合约的最后一次平仓时间超过其主力合约结束时间，则要修改本次合约的开始时间为上一次平仓后
            symbol_domain_start = last_domain_utc
            symbolDomainDic[symbol][0] = last_domain_utc
        else:
            symbol_domain_start = symbolDomainDic[symbol][0]
        symbol_domain_end = symbolDomainDic[symbol][1]
        rawdata = rawdataDic[symbol]
        r = LvyiWin(symbolinfo=symbolinfo, rawdata=rawdata, paraset=para)
        r['symbol'] = symbol  # 增加主力全约列
        r = r.loc[(r['openutc'] >= symbol_domain_start) & (r['openutc'] <= symbol_domain_end)]
        last_domain_utc = None
        if r.shape[0] > 0:
            last_close_utc = r.iloc[-1]['closeutc']
            if last_close_utc > symbol_domain_end:
                # 如果本合约最后一次平仓时间超过其主力合约结束时间，则要修改本合约的主力结束时间为平仓后
                symbolDomainDic[symbol][1] = last_close_utc
                last_domain_utc = last_close_utc
            result = pd.concat([result, r])
    result.reset_index(drop=True, inplace=True)

    # 去极值操作
    if remove_polar_switch:
        result = RS.opr_result_remove_polar(result, remove_polaar_rate)

    # 全部操作结束后，要根据修改完的主力时间重新接出一份主连来计算dailyK
    domain_bar = pd.DataFrame()
    for symbol in symbollist:
        symbol_domain_start = symbolDomainDic[symbol][0]
        symbol_domain_end = symbolDomainDic[symbol][1]
        rbar = rawdataDic[symbol]
        bars = rbar.loc[(rbar['utc_time'] >= symbol_domain_start) & (rbar['utc_endtime'] < symbol_domain_end)]
        domain_bar = pd.concat([domain_bar, bars])

    dailyK = DC.generatDailyClose(domain_bar)
    result['commission_fee'], result['per earn'], result['own cash'], result['hands'] = RS.calcResult(result,
                                                                                                      symbolinfo,
                                                                                                      initialCash,
                                                                                                      positionRatio)
    result.to_csv(strategyName + ' ' + symbolinfo.domain_symbol + str(K_MIN) + ' ' + setname + ' result.csv', index=False)
    dR = RS.dailyReturn(symbolinfo, result, dailyK, initialCash)  # 计算生成每日结果
    dR.calDailyResult()
    dR.dailyClose.to_csv((strategyName + ' ' + symbolinfo.domain_symbol + str(K_MIN) + ' ' + setname + ' dailyresult.csv'))
    results = RS.getStatisticsResult(result, False, indexcols, dR.dailyClose)
    del result
    print results
    return [setname]+results #在这里附上setname

def getParallelResult(strategyParameter,resultpath,parasetlist,paranum,indexcols):

    strategyName = strategyParameter['strategyName']
    exchange_id = strategyParameter['exchange_id']
    sec_id = strategyParameter['sec_id']
    K_MIN = strategyParameter['K_MIN']
    startdate = strategyParameter['startdate']
    enddate = strategyParameter['enddate']
    domain_symbol = '.'.join([exchange_id, sec_id])
    result_para_dic = strategyParameter['result_para_dic']
    # ======================数据准备==============================================
    # 取合约信息
    symbolInfo = DC.SymbolInfo(domain_symbol, startdate, enddate)
    # 取跨合约数据
    # contractswaplist = DC.getContractSwaplist(domain_symbol)
    # swaplist = np.array(contractswaplist.swaputc)

    # 取K线数据
    # rawdata = DC.getBarData(symbol, K_MIN, startdate + ' 00:00:00', enddate + ' 23:59:59').reset_index(drop=True)
    rawdataDic = DC.getBarBySymbolList(domain_symbol, symbolInfo.getSymbolList(), K_MIN, startdate, enddate)
    # dailyK数据改到getResult中根据结果来重新取
    # dailyK = DC.generatDailyClose(rawdata) #生成按日的K线
    foldername = ' '.join([strategyName, exchange_id, sec_id, str(K_MIN)])
    try:
        os.chdir(resultpath)
        os.mkdir(foldername)
    except:
        print ("%s folder already exsist!" %foldername)
    os.chdir(foldername)
    timestart = time.time()
    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    l = []
    resultlist = pd.DataFrame(columns=['Setname']+indexcols)
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
        }
        #l.append(getResult(strategyName, symbolInfo, K_MIN, setname, rawdataDic, paraset, positionRatio, initialCash, indexcols,timestart))
        l.append(pool.apply_async(getResult, (strategyName, symbolInfo, K_MIN, setname, rawdataDic, paraset, positionRatio, initialCash, indexcols,timestart)))
    pool.close()
    pool.join()
    timeend = time.time()
    print ("total time %.2f" % (timeend - timestart))
    # 显示结果
    i = 0
    for res in l:
        resultlist.loc[i] = res.get()
        i += 1
    # print resultlist
    finalresults = ("%s %s %d finalresults.csv" % (strategyName, domain_symbol, K_MIN))
    resultlist.to_csv(finalresults)
    return resultlist

if __name__=='__main__':
    #====================参数和文件夹设置======================================
    #文件路径
    upperpath=DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName

    # 取参数集
    parasetlist = pd.read_csv(resultpath + Parameter.parasetname)
    paranum = parasetlist.shape[0]

    #indexcols
    indexcols=Parameter.ResultIndexDic
    #for d, f in Parameter.ResultIndexDic.items():
    #    if f:indexcols.append(d)

    #参数设置
    strategyParameterSet=[]
    if not Parameter.symbol_KMIN_opt_swtich:
        #单品种单周期模式
        paradic={
        'strategyName':Parameter.strategyName,
        'exchange_id': Parameter.exchange_id,
        'sec_id': Parameter.sec_id,
        'K_MIN': Parameter.K_MIN,
        'startdate': Parameter.startdate,
        'enddate' : Parameter.enddate,
        'result_para_dic': Parameter.result_para_dic
        }
        strategyParameterSet.append(paradic)
    else:
        #多品种多周期模式
        symbolset = pd.read_excel(resultpath + Parameter.symbol_KMIN_set_filename)
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
                'result_para_dic': Parameter.result_para_dic
            }
            )
    allsymbolresult_cols=['Setname']+indexcols+[ 'strategyName','exchange_id','sec_id','K_MIN']
    allsymbolresult = pd.DataFrame(columns=allsymbolresult_cols)
    for strategyParameter in strategyParameterSet:
        r=getParallelResult(strategyParameter,resultpath,parasetlist,paranum,indexcols)
        r['strategyName']=strategyParameter['strategyName']
        r['exchange_id']=strategyParameter['exchange_id']
        r['sec_id'] = strategyParameter['sec_id']
        r['K_MIN'] = strategyParameter['K_MIN']
        allsymbolresult=pd.concat([allsymbolresult,r])
    allsymbolresult.reset_index(drop=False,inplace=True)
    os.chdir(resultpath)
    allsymbolresult.to_csv(Parameter.strategyName+"_symbol_KMIN_results.csv")
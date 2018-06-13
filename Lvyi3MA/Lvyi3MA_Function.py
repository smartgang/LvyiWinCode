# -*- coding: utf-8 -*-

import pandas as pd
import os
import DATA_CONSTANTS as DC
import numpy as np
import ResultStatistics as RS
import Lvyi3MA_Parameter as Parameter
def calDailyReturn():
    ''''''
    startdate='2016-01-01'
    enddate = '2018-04-30'
    symbol = 'SHFE.RB'
    K_MIN = 3600
    symbolinfo = DC.SymbolInfo(symbol, startdate, enddate)
    strategyName = Parameter.strategyName
    #rawdata = DC.getBarData(symbol, K_MIN, startdate + ' 00:00:00', enddate + ' 23:59:59').reset_index(drop=True)
    #dailyK = DC.generatDailyClose(rawdata)
    bardic = DC.getBarBySymbolList(symbol, symbolinfo.getSymbolList(), K_MIN, startdate, enddate)

    upperpath=DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    foldername = ' '.join([strategyName, Parameter.exchange_id, Parameter.sec_id, str(K_MIN)])
    #foldername = ' '.join([strategyName, Parameter.exchange_id, Parameter.sec_id, str(K_MIN)])+'\\DynamicStopLoss-18.0\\'
    #foldername = ' '.join([strategyName, Parameter.exchange_id, Parameter.sec_id, str(K_MIN)])+'\\OnceWinNoLoss8.0\\'
    #foldername = ' '.join([strategyName, Parameter.exchange_id, Parameter.sec_id, str(K_MIN)])+'\\dsl_-0.020ownl_0.008\\'
    os.chdir(foldername)
    parasetlist = pd.read_csv(resultpath + Parameter.parasetname)
    paranum = parasetlist.shape[0]

    filesuffix='result.csv'
    #filesuffix = 'resultDSL_by_tick.csv'
    #filesuffix = 'resultOWNL_by_tick.csv'
    #filesuffix = 'result_multiSLT.csv'
    indexcols=Parameter.ResultIndexDic
    resultList=[]
    for i in range(paranum):
        setname = parasetlist.ix[i, 'Setname']
        print setname
        oprdf=pd.read_csv(strategyName + ' ' + symbolinfo.domain_symbol + str(K_MIN) + ' ' + setname + ' '+filesuffix)
        symbolDomainDic = symbolinfo.amendSymbolDomainDicByOpr(oprdf)
        bars = DC.getDomainbarByDomainSymbol(symbolinfo.getSymbolList(), bardic, symbolDomainDic)
        dailyK = DC.generatDailyClose(bars)

        dR=RS.dailyReturn(symbolinfo,oprdf,dailyK,Parameter.initialCash)
        dR.calDailyResult()
        dR.dailyClose.to_csv(strategyName + ' ' + symbolinfo.domain_symbol + str(K_MIN) + ' ' + setname + ' daily'+filesuffix)

        results = RS.getStatisticsResult(oprdf, False, indexcols, dR.dailyClose)
        print results
        resultList.append([setname] + results)

    resultdf = pd.DataFrame(resultList,columns=['Setname'] + indexcols)
    resultdf.to_csv("%s %s %d finalresults.csv" % (strategyName,symbol, K_MIN))

if __name__=='__main__':
    calDailyReturn()
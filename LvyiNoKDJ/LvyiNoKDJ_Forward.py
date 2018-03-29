# -*- coding: utf-8 -*-
import multiTargetForward as mtf
from datetime import datetime
import pandas as pd
import DATA_CONSTANTS as DC
import os
import multiprocessing
import numpy as np
import LvyiNoKDJ_Parameter

def getForward(symbol,K_MIN,parasetlist,rawdatapath,startdate,enddate,nextmonth,windowsSet,colslist,resultfilesuffix):
    forwordresultpath = rawdatapath + '\\ForwardResults\\'
    forwardrankpath = rawdatapath + '\\ForwardRank\\'
    monthlist = [datetime.strftime(x, '%b-%y') for x in list(pd.date_range(start=startdate, end=enddate, freq='M'))]
    monthlist.append(nextmonth)
    os.chdir(rawdatapath)
    try:
        os.mkdir('ForwardResults')
    except:
        print 'ForwardResults already exist!'
    try:
        os.mkdir('ForwardRank')
    except:
        print 'ForwardRank already exist!'
    try:
        os.mkdir('ForwardOprAnalyze')
    except:
        print 'ForwardOprAnalyze already exist!'

    starttime = datetime.now()
    print starttime
    # 多进程优化，启动一个对应CPU核心数量的进程池
    pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
    l = []
    for whiteWindows in windowsSet:
        # l.append(mtf.runPara(whiteWindows, symbol, K_MIN, parasetlist, monthlist, rawdatapath, forwordresultpath, forwardrankpath, colslist, resultfilesuffix))
        l.append(pool.apply_async(mtf.runPara, (
        whiteWindows, symbol, K_MIN, parasetlist, monthlist, rawdatapath, forwordresultpath, forwardrankpath, colslist,
        resultfilesuffix)))
    pool.close()
    pool.join()

    mtf.calGrayResult(symbol, K_MIN, windowsSet, forwardrankpath, rawdatapath)
    mtf.calOprResult(rawdatapath, symbol, K_MIN, nextmonth, columns=colslist, resultfilesuffix=resultfilesuffix)
    endtime = datetime.now()
    print starttime
    print endtime

def getDslForward(dslset,symbol, K_MIN, parasetlist, folderpath, startdate, enddate, nextmonth, windowsSet):
    print ('DSL forward start!')
    colslist = mtf.getColumnsName(True)
    resultfilesuffix = 'resultDSL_by_tick.csv'
    for dslTarget in dslset:
        rawdatapath = folderpath + "DynamicStopLoss" + str(dslTarget * 1000) + '\\'
        getForward(symbol, K_MIN, parasetlist, rawdatapath, startdate, enddate, nextmonth, windowsSet, colslist,resultfilesuffix)
    print ('DSL forward finished!')

def getownlForward(ownlset,symbol, K_MIN, parasetlist, folderpath, startdate, enddate, nextmonth, windowsSet):
    print ('OWNL forward start!')
    colslist = mtf.getColumnsName(True)
    resultfilesuffix = 'resultOWNL_by_tick.csv'
    for ownlTarget in ownlset:
        rawdatapath = folderpath + "OnceWinNoLoss" + str(ownlTarget*1000) + '\\'
        getForward(symbol, K_MIN, parasetlist, rawdatapath, startdate, enddate, nextmonth, windowsSet, colslist,resultfilesuffix)
    print ('OWNL forward finished!')

def getdsl_ownlForward(dsl_ownl_list,symbol, K_MIN, parasetlist, folderpath, startdate, enddate, nextmonth, windowsSet):
    print ('DSL_OWNL forward start!')
    colslist = mtf.getColumnsName(True)
    resultfilesuffix = 'result_dsl_ownl.csv'
    for dsl_ownl in dsl_ownl_list:
        newfolder = ("dsl_%.3f_ownl_%.3f\\" % (dsl_ownl[0], dsl_ownl[1]))
        rawdatapath = folderpath + newfolder  # ！！正常:'\\'，双止损：填上'\\+双止损目标文件夹\\'
        getForward(symbol, K_MIN, parasetlist, rawdatapath, startdate, enddate, nextmonth, windowsSet, colslist, resultfilesuffix)
    print ('DSL_OWNL forward finished!')

if __name__=='__main__':
    # ======================================参数配置===================================================
    strategyName=LvyiNoKDJ_Parameter.strategyName
    exchange_id = LvyiNoKDJ_Parameter.exchange_id
    sec_id = LvyiNoKDJ_Parameter.sec_id
    K_MIN = LvyiNoKDJ_Parameter.K_MIN
    symbol= LvyiNoKDJ_Parameter.symbol
    startdate = LvyiNoKDJ_Parameter.startdate
    enddate = LvyiNoKDJ_Parameter.enddate
    nextmonth = LvyiNoKDJ_Parameter.nextMonthName
    '''
    strategyName='LvyiNoKDJWin'
    exchange_id = 'SHFE'
    sec_id = 'RB'
    K_MIN = 600
    symbol = '.'.join([exchange_id, sec_id])
    startdate = '2016-01-01'
    enddate = '2017-12-31'
    nextmonth = 'Jan-18'
    '''
    # windowsSet=[1,2,3,4,5,6,9,12,15]
    windowsSet = range(LvyiNoKDJ_Parameter.forwardWinStart, LvyiNoKDJ_Parameter.forwardWinEnd+1)  # 白区窗口值
    commonForward=LvyiNoKDJ_Parameter.common_forward
    #双止损开关和参数设置
    dslStep=LvyiNoKDJ_Parameter.dslStep_forward
    dsl=LvyiNoKDJ_Parameter.calcDsl_forward
    ownlStep=LvyiNoKDJ_Parameter.ownlStep_forward
    ownl=LvyiNoKDJ_Parameter.calcOwnl_forward
    dslownl=LvyiNoKDJ_Parameter.calcDslOwnl_forward

    dslTargetList=np.arange(LvyiNoKDJ_Parameter.dslTargetStart_close, LvyiNoKDJ_Parameter.dslTargetEnd_close, dslStep)
    ownlTargetlist=np.arange(LvyiNoKDJ_Parameter.ownlTargetStart_close,LvyiNoKDJ_Parameter.ownltargetEnd_close, ownlStep)
    dsl_ownl_List=LvyiNoKDJ_Parameter.dsl_ownl_set

    # ============================================文件路径========================================================
    upperpath = DC.getUpperPath(uppernume=2)
    resultpath = upperpath + "\\Results\\"
    foldername = ' '.join([strategyName,exchange_id, sec_id, str(K_MIN)])
    folderpath = resultpath + foldername + '\\'

    parasetlist = pd.read_csv(resultpath + LvyiNoKDJ_Parameter.parasetname)
    if commonForward:
        colslist = mtf.getColumnsName(False)
        resultfilesuffix = 'result.csv'
        getForward(symbol,K_MIN,parasetlist,folderpath,startdate,enddate,nextmonth,windowsSet,colslist,resultfilesuffix)
    if dsl:
        getDslForward(dslTargetList,symbol,K_MIN,parasetlist,folderpath,startdate,enddate,nextmonth,windowsSet)
    if ownl:
        getownlForward(ownlTargetlist,symbol,K_MIN,parasetlist,folderpath,startdate,enddate,nextmonth,windowsSet)
    if dslownl:
        getdsl_ownlForward(dsl_ownl_List,symbol,K_MIN,parasetlist,folderpath,startdate,enddate,nextmonth,windowsSet)



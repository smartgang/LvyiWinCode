# -*- coding: utf-8 -*-
import multiTargetForward as mtf
from datetime import datetime
import pandas as pd
import DATA_CONSTANTS as DC
import os
import multiprocessing
import Lvyi3MA_Parameter
import numpy as np

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
    # 文件路径
    upperpath = DC.getUpperPath(Lvyi3MA_Parameter.folderLevel)
    resultpath = upperpath + Lvyi3MA_Parameter.resultFolderName

    # 取参数集
    parasetlist = pd.read_csv(resultpath + Lvyi3MA_Parameter.parasetname)
    paranum = parasetlist.shape[0]

    # ======================================参数配置===================================================

    # 参数设置
    strategyParameterSet = []
    if not Lvyi3MA_Parameter.symbol_KMIN_opt_swtich:
        # 单品种单周期模式
        paradic = {
            'strategyName': Lvyi3MA_Parameter.strategyName,
            'exchange_id': Lvyi3MA_Parameter.exchange_id,
            'sec_id': Lvyi3MA_Parameter.sec_id,
            'K_MIN': Lvyi3MA_Parameter.K_MIN,
            'startdate': Lvyi3MA_Parameter.startdate,
            'enddate': Lvyi3MA_Parameter.enddate,
            'symbol': '.'.join([Lvyi3MA_Parameter.exchange_id, Lvyi3MA_Parameter.sec_id]),
            'calcDsl': Lvyi3MA_Parameter.calcDsl_close,
            'calcOwnl': Lvyi3MA_Parameter.calcOwnl_close,
            'calcDslOwnl': Lvyi3MA_Parameter.calcDslOwnl_close,
            'dslStep':Lvyi3MA_Parameter.dslStep_close,
            'dslTargetStart':Lvyi3MA_Parameter.dslTargetStart_close,
            'dslTargetEnd':Lvyi3MA_Parameter.dslTargetEnd_close,
            'ownlStep' : Lvyi3MA_Parameter.ownlStep_close,
        }
        strategyParameterSet.append(paradic)
    else:
        # 多品种多周期模式
        symbolset = pd.read_excel(resultpath + Lvyi3MA_Parameter.stoploss_set_filename,index_col='No')
        symbolsetNum = symbolset.shape[0]
        for i in range(symbolsetNum):
            exchangeid = symbolset.ix[i, 'exchange_id']
            secid = symbolset.ix[i, 'sec_id']
            strategyParameterSet.append({
                'strategyName': symbolset.ix[i, 'strategyName'],
                'exchange_id': exchangeid,
                'sec_id': secid,
                'K_MIN': symbolset.ix[i, 'K_MIN'],
                'startdate': symbolset.ix[i, 'startdate'],
                'enddate': symbolset.ix[i, 'enddate'],
                'symbol': '.'.join([exchangeid, secid]),
                'calcDsl': symbolset.ix[i, 'calcDsl'],
                'calcOwnl': symbolset.ix[i, 'calcOwnl'],
                'calcDslOwnl': symbolset.ix[i, 'calcDslOwnl'],
                'dslStep': symbolset.ix[i, 'dslStep'],
                'dslTargetStart': symbolset.ix[i, 'dslTargetStart'],
                'dslTargetEnd': symbolset.ix[i, 'dslTargetEnd'],
                'ownlStep': symbolset.ix[i, 'ownlStep'],
                'ownlTargetStart': symbolset.ix[i, 'ownlTargetStart'],
                'ownltargetEnd': symbolset.ix[i, 'ownltargetEnd'],
                'nolossThreshhold': symbolset.ix[i, 'nolossThreshhold']
            }
            )


    strategyName=Lvyi3MA_Parameter.strategyName
    exchange_id = Lvyi3MA_Parameter.exchange_id
    sec_id = Lvyi3MA_Parameter.sec_id
    K_MIN = Lvyi3MA_Parameter.K_MIN
    symbol= '.'.join([exchange_id, sec_id])
    startdate = Lvyi3MA_Parameter.startdate
    enddate = Lvyi3MA_Parameter.enddate
    nextmonth = Lvyi3MA_Parameter.nextMonthName
    # windowsSet=[1,2,3,4,5,6,9,12,15]
    windowsSet = range(Lvyi3MA_Parameter.forwardWinStart, Lvyi3MA_Parameter.forwardWinEnd+1)  # 白区窗口值
    commonForward=Lvyi3MA_Parameter.common_forward
    #双止损开关和参数设置
    dslStep=Lvyi3MA_Parameter.dslStep_forward
    dsl=Lvyi3MA_Parameter.calcDsl_forward
    ownlStep=Lvyi3MA_Parameter.ownlStep_forward
    ownl=Lvyi3MA_Parameter.calcOwnl_forward
    dslownl=Lvyi3MA_Parameter.calcDslOwnl_forward

    dslTargetList=np.arange(Lvyi3MA_Parameter.dslTargetStart_close, Lvyi3MA_Parameter.dslTargetEnd_close, dslStep)
    ownlTargetlist=np.arange(Lvyi3MA_Parameter.ownlTargetStart_close,Lvyi3MA_Parameter.ownltargetEnd_close, ownlStep)
    dsl_ownl_List=Lvyi3MA_Parameter.dsl_ownl_set

    # ============================================文件路径========================================================
    upperpath = DC.getUpperPath(uppernume=2)
    resultpath = upperpath + "\\Results\\"
    foldername = ' '.join([strategyName,exchange_id, sec_id, str(K_MIN)])
    folderpath = resultpath + foldername + '\\'

    parasetlist = pd.read_csv(resultpath + Lvyi3MA_Parameter.parasetname)

    parasetlist = pd.read_csv(resultpath + Lvyi3MA_Parameter.parasetname)
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
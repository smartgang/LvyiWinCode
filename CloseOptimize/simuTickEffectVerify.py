# -*- coding: utf-8 -*-
'''
验证模拟tick和真实tick的效果差异
DSL和OWNL分开对比，视结果如有必要再结合
时间：2017-10-01 —— 2017-12-01

读取dsl/ownl平仓数据，并按验证时间截取
计算dsl/ownl的原始ret,new_ret,ret_delta
读取真实tick平仓数据，计算真实tick的new_ret,retdelta
每组参数保存一个总数，计算真实和虚拟new_ret的差值
'''
import DATA_CONSTANTS as DC
import pandas as pd
import os
import time
def verifyDslSimuTick(sn,symbol,K_MIN,setname,tickstartutc,tickendutc,tofolder):
    print ("sn:%d setname:%s"%(sn,setname))
    dsldf=pd.read_csv(tofolder + symbol + str(K_MIN) + ' ' + setname + ' resultDSL_by_tick.csv')
    #只截取tick时间范围内的opr
    dsldf = dsldf.loc[(dsldf['openutc'] > tickstartutc) & (dsldf['openutc'] < tickendutc)]
    oriretsum=dsldf['ret'].sum()
    dslretsum=dsldf['new_ret'].sum()
    workdslretsum=dsldf.loc[dsldf['new_closeutc']!=dsldf['closeutc'],'new_ret'].sum()
    workdsloriretsum=dsldf.loc[dsldf['new_closeutc']!=dsldf['closeutc'],'ret'].sum()
    retdelta=dslretsum-oriretsum
    workretdelta=workdslretsum-workdsloriretsum
    dslworknum=dsldf.loc[dsldf['new_closeutc']!=dsldf['closeutc'],'new_ret'].count()

    tickdf=pd.read_csv(tofolder + symbol + str(K_MIN) + ' ' + setname + ' resultDSL_by_realtick.csv')
    tickretsum=tickdf['new_ret'].sum()
    tickworkretsum=tickdf.loc[tickdf['new_closeutc']!=tickdf['closeutc'],'new_ret'].sum()
    tickworkoriretsum=tickdf.loc[tickdf['new_closeutc']!=tickdf['closeutc'],'ret'].sum()
    tickretdelta=tickretsum-oriretsum
    tickworkretdelta = tickworkretsum - tickworkoriretsum
    tickworknum=tickdf.loc[tickdf['new_closeutc']!=tickdf['closeutc'],'new_ret'].count()

    totaloprnum=dsldf.shape[0]
    simuTickRetDelta=tickretdelta-retdelta

    return [setname,simuTickRetDelta,tickworknum,dslworknum,totaloprnum,tickretdelta,retdelta,tickworkretdelta,workretdelta,tickworkretsum,workdslretsum,
            tickworkoriretsum,workdsloriretsum,tickretsum,dslretsum,oriretsum]

def verifyOwnlSimuTick(sn,symbol,K_MIN,setname,tickstartutc,tickendutc,tofolder):
    print ("sn:%d setname:%s"%(sn,setname))
    ownldf=pd.read_csv(tofolder+symbol + str(K_MIN) + ' ' + setname + ' resultOWNL_by_tick.csv')
    #只截取tick时间范围内的opr
    ownldf = ownldf.loc[(ownldf['openutc'] > tickstartutc) & (ownldf['openutc'] < tickendutc)]
    oriretsum=ownldf['ret'].sum()
    dslretsum=ownldf['new_ret'].sum()
    workdslretsum=ownldf.loc[ownldf['new_closeutc']!=ownldf['closeutc'],'new_ret'].sum()
    workdsloriretsum=ownldf.loc[ownldf['new_closeutc']!=ownldf['closeutc'],'ret'].sum()
    retdelta=dslretsum-oriretsum
    workretdelta=workdslretsum-workdsloriretsum
    dslworknum=ownldf.loc[ownldf['new_closeutc']!=ownldf['closeutc'],'new_ret'].count()

    tickdf=pd.read_csv(tofolder + symbol + str(K_MIN) + ' ' + setname + ' resultDSL_by_realtick.csv')
    tickretsum=tickdf['new_ret'].sum()
    tickworkretsum=tickdf.loc[tickdf['new_closeutc']!=tickdf['closeutc'],'new_ret'].sum()
    tickworkoriretsum=tickdf.loc[tickdf['new_closeutc']!=tickdf['closeutc'],'ret'].sum()
    tickretdelta=tickretsum-oriretsum
    tickworkretdelta = tickworkretsum - tickworkoriretsum
    tickworknum=tickdf.loc[tickdf['new_closeutc']!=tickdf['closeutc'],'new_ret'].count()

    totaloprnum=ownldf.shape[0]
    simuTickRetDelta=tickretdelta-retdelta

    return [setname,simuTickRetDelta,tickworknum,dslworknum,totaloprnum,tickretdelta,retdelta,tickworkretdelta,workretdelta,tickworkretsum,workdslretsum,
            tickworkoriretsum,workdsloriretsum,tickretsum,dslretsum,oriretsum]

if __name__ =='__main__':
    #参数配置
    exchange_id = 'SHFE'
    sec_id='RB'
    symbol = '.'.join([exchange_id, sec_id])
    K_MIN = 600
    topN=4500
    pricetick=DC.getPriceTick(symbol)
    slip=pricetick
    starttime='2017-09-01'
    endtime='2017-12-11'
    tickstarttime='2017-10-01'
    tickendtime='2017-12-01'
    tickstartutc = float(time.mktime(time.strptime(tickstarttime + ' 00:00:00', "%Y-%m-%d %H:%M:%S")))
    tickendutc = float(time.mktime(time.strptime(tickendtime + ' 23:59:59', "%Y-%m-%d %H:%M:%S")))

    # 优化参数
    # stoplossStep=-0.002
    # stoplossList = np.arange(-0.02, -0.04, stoplossStep)
    stoplossList = [-0.022]
    winSwitchList = [0.009]

    # 文件路径
    upperpath = DC.getUpperPath(uppernume=2)
    resultpath = upperpath + "\\Results\\"
    foldername = ' '.join([exchange_id, sec_id, str(K_MIN)])
    oprresultpath = resultpath + foldername

    # 读取finalresult文件并排序，取前topN个
    finalresult = pd.read_csv(oprresultpath + "\\" + symbol + str(K_MIN) + " finanlresults.csv")
    finalresult = finalresult.sort_values(by='end_cash', ascending=False)
    totalnum = finalresult.shape[0]

    os.chdir(oprresultpath)

    '''
    # dsl
    resultlist=[]
    for stoplossTarget in stoplossList:
        dslFolderName = "DynamicStopLoss" + str(stoplossTarget * 1000) + '\\'
        for sn in range(0, topN):
            opr = finalresult.iloc[sn]
            setname=opr['Setname']
            resultlist.append(verifyDslSimuTick(sn,symbol,K_MIN,setname,tickstartutc,tickendutc,dslFolderName))

   
    allresultdf = pd.DataFrame(resultlist,
        columns=['setname', 'simuTickRetDelta', 'tickWorkNum', 'dslWorkNum', 'totalOprNum', 'tickRetDelta', 'dslRetDelta',
                 'tickWorkRetDelta', 'dslWorkretDelta', 'tickWorkRetSum', 'dslWorkRetSum', 'tickWorkOriRetSum', 'dslWorkOriRetSum',
                 'tickRetSum', 'dslRetSum', 'oriRetSum'])
    allresultdf.to_csv(symbol + str(K_MIN) + ' finalresult_dsl_simutick_Veryfy.csv')
    '''
    # ownl
    resultlist=[]
    for winSwitch in winSwitchList:
        ownlFolderName = "OnceWinNoLoss" + str(winSwitch * 1000)+'\\'
        for sn in range(0, topN):
            opr = finalresult.iloc[sn]
            setname=opr['Setname']
            resultlist.append(verifyOwnlSimuTick(sn, symbol, K_MIN, setname, tickstartutc, tickendutc, ownlFolderName))

    allresultdf = pd.DataFrame(resultlist,
                               columns=['setname', 'simuTickRetDelta', 'tickWorkNum', 'ownlWorkNum', 'totalOprNum',
                                        'tickRetDelta', 'ownlRetDelta',
                                        'tickWorkRetDelta', 'ownlWorkretDelta', 'tickWorkRetSum', 'ownlWorkRetSum',
                                        'tickWorkOriRetSum', 'ownlWorkOriRetSum',
                                        'tickRetSum', 'ownlRetSum', 'oriRetSum'])
    allresultdf.to_csv(symbol + str(K_MIN) + ' finalresult_ownl_simutick_Veryfy.csv')
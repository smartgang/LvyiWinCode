# -*- coding: utf-8 -*-
'''
每月更新参数时使用
'''
import pandas as pd
import numpy as np
import time
import ResultStatistics as RS
from datetime import datetime
import DATA_CONSTANTS as DC

def  getMonthParameter(startmonth,endmonth,symbol,K_MIN,parasetlist,oprresultpath,targetpath):
    '''
    根据输出参数计算目标月份应该使用的参数集
    :param month: 目标月份
    :param ranktarget: 评价纬度
    :param windowns: 窗口大小
    :param oprresultpath:
    :param targetpath:
    :return:
    '''
    print ('Calculating month parameters,start from %s to %s' % (startmonth,endmonth))
    print datetime.now()
    parasetlen = parasetlist.shape[0]
    annual_list = []
    sharpe_list= []
    success_rate_list = []
    drawback_list = []
    set_list=[]
    for i in np.arange(0, parasetlen):
        setname = parasetlist.ix[i, 'Setname']
        print setname
        filename = oprresultpath + symbol + str(K_MIN) + ' ' + setname + ' result.csv'
        resultdf = pd.read_csv(filename)
        starttime = startmonth+ '-01 00:00:00'
        endtime = endmonth + '-01 00:00:00'
        startutc = float(time.mktime(time.strptime(starttime, "%Y-%m-%d %H:%M:%S")))
        endutc = float(time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M:%S")))
        resultdata = resultdf.loc[(resultdf['openutc'] >= startutc) & (resultdf['openutc'] < endutc)]
        resultdata = resultdata.reset_index(drop=True)
        annual_list.append(RS.annual_return(resultdata))
        sharpe_list.append(RS.sharpe_ratio(resultdata))
        success_rate_list.append(RS.success_rate(resultdata))
        drawback, a, b = RS.max_drawback(resultdata)
        drawback_list.append(drawback)
        set_list.append(setname)
        # print('annual:%f.2,sharpe:%f.2,success_rate:%f.2,drawback:%f.2'%(annual,sharpe,success_rate,drawback))
    df = pd.DataFrame(set_list, columns=['Setname'])
    df['Annual']=annual_list
    df['Sharpe']=sharpe_list
    df['SuccessRate']=success_rate_list
    df['DrawBack']=drawback_list

    rangarray = range(df.shape[0], 0, -1)
    df = df.sort_values(by='Annual', ascending=False)
    df['AnnualRank']=0
    df['AnnualRank'] += rangarray
    df = df.sort_values(by='Sharpe', ascending=False)
    df['SharpeRank']=0
    df['SharpeRank'] += rangarray
    df = df.sort_values(by='SuccessRate', ascending=False)
    df['SuccessRank']=0
    df['SuccessRank'] += rangarray
    df = df.sort_values(by='DrawBack', ascending=False)
    df['DrawbackRank']=0
    df['DrawbackRank'] += rangarray

    df = df.sort_values(by='Setname', ascending=True)
    df['Rank1'] = df['AnnualRank']  # 目标集1：年化收益
    df['Rank2'] = df['SharpeRank']  # 目标集2：夏普值
    df['Rank3'] = df['AnnualRank'] * 0.6 + df['DrawbackRank'] * 0.4  # 目标集3：年化收益*0.6+最大回撤*0.4
    df['Rank4'] = df['SharpeRank'] * 0.6 + df['DrawbackRank'] * 0.4  # 目标集4：夏普*0.6+最大回撤*0.4
    df['Rank5'] = df['AnnualRank'] * 0.4 + df['SharpeRank'] * 0.3 + \
                  df['SuccessRank'] * 0.1 + df['DrawbackRank'] * 0.2  # 目标集5：4目标综合
    df['Rank6'] = df['SuccessRank']
    df['Rank7'] = df['SuccessRank'] * 0.5 + df['AnnualRank'] * 0.5

    filenamehead = ("%s_%s_%d_%s_parameter" % (targetpath, symbol, K_MIN, endmonth))
    df.to_csv(filenamehead + '.csv')
    print ('Calculating month parameters Finished! From %s to %s' % (startmonth, endmonth))
    print datetime.now()


if __name__ == '__main__':
    #参数配置
    exchange_id = 'DCE'
    sec_id='I'
    K_MIN = 600
    symbol = '.'.join([exchange_id, sec_id])

    #文件路径
    upperpath=DC.getUpperPath(uppernume=2)
    resultpath=upperpath+"\\Results\\"
    foldername = ' '.join([exchange_id, sec_id, str(K_MIN)])
    rawdatapath=resultpath+foldername+'\\'

    parasetlist = pd.read_csv(resultpath+'ParameterOptSet1.csv')

    starttime=datetime.now()
    print starttime
    getMonthParameter('2017-11','2018-02',symbol,K_MIN,parasetlist,rawdatapath,rawdatapath)
    endtime = datetime.now()
    print starttime
    print endtime
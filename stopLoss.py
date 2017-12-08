# -*- coding: utf-8 -*-
'''
止损优化
程序流程：
    1.读入result文件，读入bar数据
    2.按每一个操作，取出操作的开始和结束index，根据index取bar数据的close列
    3.maxloss=(close.min()-openprice）/openprice
    4.if maxloss>stoplossTarget:ret=openprice*(1+stoplossTarget)-slip,ret_r=ret/openprice
    5.统计其他收益
'''
import pandas as pd
import DATA_CONSTANTS as DC
import numpy as np
symbol='SHFE.RB'
K_MIN=60
stopLossTarget=0.02
slip=0.1
#!!!可能要做一下index的对齐，具体调试的时候再看
#——都是通过DC读的数据，不用对齐
bardata = DC.GET_DATA(DC.DATA_TYPE_RAW, symbol, K_MIN, '2016-01-05 09:00:00').reset_index(drop=True)
oprlist =pd.read_csv('testdata\SHFE.RB600 Set2867 MS4 ML21 KN24 DN40 result.csv')
oprnum=oprlist.shape[0]
for i in np.arange(0,20,1):
    opr=oprlist.iloc[i]
    openindex=opr.openindex
    closeindex=opr.closeindex
    closemin=bardata.loc[openindex:closeindex+1].close.min()
    openprice = opr.openprice
    print ('openindex:%d,openprice:%d,closemin:%d'%(openindex,openprice,closemin))
    if openprice>closemin:
        maxloss=
    print 'a'


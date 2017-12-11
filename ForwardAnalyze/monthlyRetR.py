# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

parasetlist=pd.read_csv('D:\\002 MakeLive\myquant\LvyiWin\Results\\ParameterOptSet.csv')
datapath='D:\\002 MakeLive\myquant\LvyiWin\Results\\SHFE RB600 slip\\'
parasetlen=parasetlist.shape[0]
symbol='SHFE.RB'
K_MIN=600
prodlist=[]
for i in np.arange(0, parasetlen):
    setname=parasetlist.ix[i,'Setname']
    print setname
    filename=datapath+symbol + str(K_MIN) + ' ' + setname + ' result.csv'
    result=pd.read_csv(filename)
    result['month'] =result.opentime.str.slice(0, 7)
    #print result.month
    result['ret_r_1'] = result['ret_r'] + 1
    grouped_ret_r = result['ret_r_1'].groupby(result['month'])
    ret_r_prod = grouped_ret_r.prod()
    ret_r_prod.name=setname
    prodlist.append(ret_r_prod)

proddf=pd.DataFrame(prodlist)
proddf.to_csv('prodresult.csv')
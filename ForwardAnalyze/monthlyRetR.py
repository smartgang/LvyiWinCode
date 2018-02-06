# -*- coding: utf-8 -*-
'''
多层推进分析第1步：
计算每个组合每个月的独立收益
'''
import pandas as pd
import numpy as np
import DATA_CONSTANTS as DC

def monthyRetR(parasetlist,datapath,symbol,K_MIN):
    parasetlen = parasetlist.shape[0]
    prodlist=[]
    for i in np.arange(0, parasetlen):
        setname=parasetlist.ix[i,'Setname']
        print setname
        filename=datapath+symbol + str(K_MIN) + ' ' + setname + ' result.csv'
        result=pd.read_csv(filename)
        result['month'] =result.opentime.str.slice(0, 7)#月是7，天是10
        #print result.month
        result['ret_r_1'] = result['ret_r'] + 1
        grouped_ret_r = result['ret_r_1'].groupby(result['month'])
        ret_r_prod = grouped_ret_r.prod()
        ret_r_prod.name=setname
        prodlist.append(ret_r_prod)

    proddf=pd.DataFrame(prodlist)
    #proddf.index.name='Setname'
    tf="%s%s_%d_monthly_retr.csv" %(datapath,symbol,K_MIN)
    proddf.to_csv(tf)
    return tf

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
    oprresultpath=resultpath+foldername

    parasetlist = pd.read_csv(resultpath+'ParameterOptSet1.csv')
    datapath =resultpath+foldername+'\\'

    monthyRetR(parasetlist,datapath,symbol,K_MIN)
# -*- coding: utf-8 -*-
'''
计算3MA平仓的new_ret结果
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
        #filename=datapath+symbol + str(K_MIN) + ' ' + setname + ' result.csv'
        filename=symbol+str(K_MIN)+' '+setname+' 3MAresult3.csv'
        result=pd.read_csv(filename)
        result['month'] =result.opentime.str.slice(0, 7)#月是7，天是10
        #print result.month
        result['ret_r_1'] = result['new_ret_r'] + 1
        grouped_ret_r = result['ret_r_1'].groupby(result['month'])
        ret_r_prod = grouped_ret_r.prod()
        ret_r_prod.name=setname
        prodlist.append(ret_r_prod)

    proddf=pd.DataFrame(prodlist)
    proddf.index.name = 'Setname'
    tf="%s%s_%d_monthly_retr_3MA.csv" %(datapath,symbol,K_MIN)
    proddf.to_csv(tf)
    return tf

if __name__ == '__main__':
    #参数配置
    exchange_id = 'DCE'
    sec_id='I'
    symbol = '.'.join([exchange_id, sec_id])
    K_MIN = 600

    #文件路径
    upperpath=DC.getUpperPath(uppernume=2)
    resultpath=upperpath+"\\Results\\"
    foldername = ' '.join([exchange_id, sec_id, str(K_MIN)])
    oprresultpath=resultpath+foldername
    parasetlist=pd.read_csv(resultpath+'ParameterOptSet1.csv')
    datapath=oprresultpath+'\\ThreeMAClose3to4\\'
    monthyRetR(parasetlist,datapath,symbol,K_MIN)
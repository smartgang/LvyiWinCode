# -*- coding: utf-8 -*-
'''
采用相同周期K线
初始设定：
ma_mid=(ma_short+ma_long)/2
只计算回测结果中end cash排名top2000的参数组合
内容：
ma_short下穿ma_mid平多
ma_short上破ma_mid平空
计算过程：
读取回测结果，按end cash排名，取出top2000的参数组合名称
根据名称参数计算ma_mid，读取oprResult
读取bardata，对齐index,计算ma_mid,以及ma_short和ma_mid的cross（copy读法）
遍历oprResult，找到每一个opr中间的ma_mid_cross，返回strtime,utc_time,index,close
重新计算ret,ret_r
计算end cash结果并保存
final result要保存之前的end cash和新的end cash做对比
结果分析：
综合对比top2000的end cash结果，看总体是否有改善
挑选典型参数组(end cash最大、改善最大，改善最小），看策略生效的特征
'''
import pandas as pd
import DATA_CONSTANTS as DC
import MA
if __name__ == '__main__':
    #参数配置
    exchange_id = 'DCE'
    sec_id='I'
    symbol = '.'.join([exchange_id, sec_id])
    K_MIN = 600
    topN=2000
    slip=0.5

    #文件路径
    upperpath=DC.getUpperPath(uppernume=2)
    resultpath=upperpath+"\\Results\\"
    foldername = ' '.join([exchange_id, sec_id, str(K_MIN)])

    #读取finalresult文件并排序，取前testnum个
    finalresult=pd.read_csv(resultpath+foldername+"\\"+symbol+str(K_MIN)+" finanlresults.csv")
    finalresult=finalresult.sort_values(by='end_cash',ascending=False)
    finalresult=finalresult.iloc[0:topN]
    oprset = finalresult.iloc[0]


    #计算mamid，并计算ma和cross
    mashort=oprset['MA_Short']
    malong=oprset['MA_Long']
    mamid=int((mashort+malong)/2)
    bardata=DC.getBarData(symbol,K_MIN,'2016-01-01 00:00:00','2018-01-01 00:00:00')
    df_MA = MA.MA(bardata['close'], mashort, mamid)
    df_MA.drop('close', axis=1, inplace=True)
    df = pd.concat([bardata, df_MA], axis=1)

    #读取opr
    oprfilename=symbol+str(K_MIN)+' '+oprset['Setname']+' result.csv'
    oprresult=pd.read_csv(resultpath+foldername+"\\"+oprfilename)
    print oprresult.head(10)
    oprnum=oprresult.shape[0]
    for i in range(oprnum):
        opr=oprresult.iloc[i]
        oprtype=opr['tradetype']
        openutc=opr['openutc']
        closeutc=opr['closeutc']
        #判断是否有mamid的交叉导致新的平仓
        crossdf=df.loc[(df['utc_time']>=openutc)&(df['utc_time']<=closeutc)]
        if oprtype==1:
            cross=crossdf.loc[crossdf['MA_Cross']==-1]
        else:
            cross=crossdf.loc[crossdf['MA_Cross']==1]
        if cross.shape[0]>0:
            c=cross.iloc[0]
            openprice=opr['openprice']
            newcloseprice=c['close']
            newclosetime=c['strtime']
            newcloseutc=c['utc_time']
            newcloseindex=c['Unnamed: 0']
            newret=((newcloseprice - openprice) * oprtype) - slip
            oprresult.iloc[i]['newret'] = newret
            oprresult.iloc[i]['newret_r']=result['ret_r']=result['ret']/result['closeprice']
